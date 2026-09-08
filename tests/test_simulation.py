"""
tests/test_simulation.py

Tests for the virtual network simulation engine.
"""

import pytest
from simulation.network import create_default_topology, VirtualDevice
from simulation.traffic_generator import generate_synthetic_flow, apply_jitter
from simulation.scenarios import (
    get_scenario_generator, CLIENT_A, ATTACKER, SERVER_B, DDOS_IPS,
)
from simulation.simulator import generate_simulation_batch


# ─── Virtual Network Tests ─────────────────────────────────────────────────────

class TestVirtualNetwork:

    def test_topology_creation(self):
        net = create_default_topology()
        assert len(net.devices) >= 4  # Router, Server, Client, Attacker + DDoS nodes

    def test_ip_scheme(self):
        net = create_default_topology()
        ips = [d.ip_address for d in net.devices]
        assert "10.0.0.1" in ips      # Router
        assert "10.0.0.10" in ips     # Client A
        assert "10.0.0.50" in ips     # Attacker
        assert "10.0.0.100" in ips    # Server B

    def test_device_types(self):
        net = create_default_topology()
        assert len(net.get_clients()) >= 1
        assert len(net.get_servers()) >= 1
        assert len(net.get_attackers()) >= 1
        assert net.get_router() is not None

    def test_ddos_nodes(self):
        net = create_default_topology()
        attackers = net.get_attackers()
        atk_ips = [a.ip_address for a in attackers]
        for ip in DDOS_IPS:
            assert ip in atk_ips

    def test_get_device_by_ip(self):
        net = create_default_topology()
        srv = net.get_device_by_ip("10.0.0.100")
        assert srv is not None
        assert srv.hostname == "Server-B"

    def test_nonexistent_ip_returns_none(self):
        net = create_default_topology()
        assert net.get_device_by_ip("99.99.99.99") is None


# ─── Traffic Generator Tests ──────────────────────────────────────────────────

class TestTrafficGenerator:

    def test_jitter_modifies_values(self):
        base = {"flow_dur": 100.0, "pkt_rate": 50.0}
        jittered = apply_jitter(base, "HIGH")
        assert jittered["flow_dur"] != 100.0
        assert jittered["flow_dur"] > 0
        assert jittered["pkt_rate"] > 0

    def test_benign_flow_has_all_features(self):
        flow = generate_synthetic_flow("BENIGN", "LOW")
        assert "Fwd IAT Total" in flow
        assert "Flow Duration" in flow
        assert len(flow) == 20

    def test_attack_flow_has_all_features(self):
        for attack in ["DoS", "DDoS", "PortScan", "BruteForce"]:
            flow = generate_synthetic_flow(attack, "MEDIUM")
            assert len(flow) == 20
            assert "Flow Bytes/s" in flow

    def test_benign_different_from_attack(self):
        benign = generate_synthetic_flow("BENIGN", "LOW")
        dos = generate_synthetic_flow("DoS", "HIGH")
        assert benign["Flow Duration"] != dos["Flow Duration"]


# ─── Scenario Tests ────────────────────────────────────────────────────────────

class TestScenarios:

    def test_normal_scenario_uses_correct_ips(self):
        net = create_default_topology()
        events = list(get_scenario_generator("Normal Traffic", net, "MEDIUM", 5))
        assert len(events) == 5
        for e in events:
            assert e["source_ip"] == CLIENT_A
            assert e["destination_ip"] == SERVER_B
            assert e["scenario"] == "BENIGN"

    def test_portscan_scenario(self):
        net = create_default_topology()
        events = list(get_scenario_generator("Port Scan", net, "MEDIUM", 20))
        assert len(events) == 20
        atk_events = [e for e in events if e["scenario"] == "PortScan"]
        assert len(atk_events) > 0
        for e in atk_events:
            assert e["source_ip"] == ATTACKER

    def test_ddos_scenario_uses_distributed_ips(self):
        net = create_default_topology()
        events = list(get_scenario_generator("DDoS", net, "HIGH", 50))
        ddos_events = [e for e in events if e["scenario"] == "DDoS"]
        source_ips = set(e["source_ip"] for e in ddos_events)
        # Should have multiple attacker IPs
        assert len(source_ips) > 1

    def test_suspicious_scenario(self):
        net = create_default_topology()
        events = list(get_scenario_generator("Suspicious Traffic", net, "MEDIUM", 20))
        assert len(events) == 20
        scenarios = set(e["scenario"] for e in events)
        # Should have a mix
        assert len(scenarios) >= 1

    def test_all_scenarios_are_registered(self):
        from simulation.scenarios import SCENARIO_MAP
        expected = ["Normal Traffic", "Port Scan", "Brute Force", "DoS", "DDoS", "Suspicious Traffic"]
        for name in expected:
            assert name in SCENARIO_MAP


# ─── Simulator Batch Tests ─────────────────────────────────────────────────────

class TestSimulator:

    def test_batch_generation(self):
        batch = generate_simulation_batch("Normal Traffic", "LOW", 1)
        assert len(batch) == 5  # 1 sec * 10 * 0.5 = 5

    def test_batch_cap(self):
        batch = generate_simulation_batch("DoS", "HIGH", 60)
        assert len(batch) <= 500  # Hard cap

    def test_batch_events_have_required_fields(self):
        batch = generate_simulation_batch("Port Scan", "MEDIUM", 1)
        for event in batch:
            assert "source_ip" in event
            assert "destination_ip" in event
            assert "features" in event
            assert "scenario" in event
            assert "protocol" in event

    def test_dynamic_switch_scenario(self):
        from simulation.scenarios import run_dynamic_switch_scenario
        net = create_default_topology()
        events = list(run_dynamic_switch_scenario(
            network=net,
            initial_scenario="Normal Traffic",
            injected_attack="Port Scan",
            intensity="LOW",
            num_events=10,
            switch_ratio=0.4,
        ))
        assert len(events) == 10
        baseline_events = [e for e in events if e.get("simulation_phase") == "BASELINE"]
        attack_events = [e for e in events if e.get("simulation_phase") == "SUDDEN_ATTACK"]
        assert len(baseline_events) == 4
        assert len(attack_events) == 6
        assert attack_events[0]["is_injected"] is True
        assert baseline_events[0]["is_injected"] is False

    def test_generate_simulation_batch_with_injection(self):
        batch = generate_simulation_batch(
            scenario_name="Normal Traffic",
            intensity="LOW",
            duration_sec=2,
            injected_attack="DDoS",
            switch_ratio=0.5,
        )
        assert len(batch) == 10
        scenarios = [e.get("simulation_phase") for e in batch]
        assert "BASELINE" in scenarios
        assert "SUDDEN_ATTACK" in scenarios

    def test_run_instant_attack_burst(self):
        from simulation.simulator import run_instant_attack_burst
        results = run_instant_attack_burst("Port Scan", count=3, intensity="MEDIUM")
        assert len(results) == 3
        for res in results:
            assert "prediction" in res
            assert "db_event" in res
            assert "was_blocked" in res
            assert res["prediction"]["predicted_class"] in [
                "BENIGN", "PortScan", "DoS Hulk", "DDoS", "FTP-Patator", "SSH-Patator", "Bot", "DoS", "Port Scan", "BLOCKED"
            ]
