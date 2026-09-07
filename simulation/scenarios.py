"""
simulation/scenarios.py

Attack scenario generators for the AI-SNIDS virtual lab.

Each scenario yields a sequence of simulated flow event dicts
that are then passed through the real AI prediction pipeline.

SAFETY: No real network traffic is generated. These are purely
data structures representing flow characteristics.
"""

import random
from typing import Generator
from simulation.network import VirtualNetwork
from simulation.traffic_generator import generate_synthetic_flow


# ─── Constants ─────────────────────────────────────────────────────────────────

CLIENT_A  = "10.0.0.10"
ATTACKER  = "10.0.0.50"
SERVER_B  = "10.0.0.100"
DDOS_IPS  = [f"10.0.0.{50 + i}" for i in range(1, 7)]  # 10.0.0.51–56


def _generate_event(
    src_ip: str, dst_ip: str, dst_port: int,
    protocol: str, scenario: str, intensity: str
) -> dict:
    """Build a single simulated flow event dict."""
    return {
        "source_ip": src_ip,
        "destination_ip": dst_ip,
        "source_port": random.randint(1024, 65535),
        "destination_port": dst_port,
        "protocol": protocol,
        "features": generate_synthetic_flow(scenario, intensity),
        "scenario": scenario,
    }


# ─── Scenario Generators ──────────────────────────────────────────────────────

def run_normal_scenario(
    network: VirtualNetwork, intensity: str, num_events: int
) -> Generator[dict, None, None]:
    """Client A ↔ Server B — normal web browsing traffic."""
    for _ in range(num_events):
        yield _generate_event(
            CLIENT_A, SERVER_B,
            random.choice([80, 443]), "TCP", "BENIGN", intensity
        )


def run_portscan_scenario(
    network: VirtualNetwork, intensity: str, num_events: int
) -> Generator[dict, None, None]:
    """Attacker scans Server B across many ports."""
    ports_to_scan = [21, 22, 23, 25, 53, 80, 110, 135, 139, 443, 445, 3389, 8080]

    for _ in range(num_events):
        if random.random() < 0.90:
            yield _generate_event(
                ATTACKER, SERVER_B,
                random.choice(ports_to_scan), "TCP", "PortScan", intensity
            )
        else:
            # Background legitimate traffic
            yield _generate_event(
                CLIENT_A, SERVER_B, 443, "TCP", "BENIGN", intensity
            )


def run_bruteforce_scenario(
    network: VirtualNetwork, intensity: str, num_events: int
) -> Generator[dict, None, None]:
    """Attacker attempts brute force on SSH/FTP."""
    for _ in range(num_events):
        if random.random() < 0.85:
            yield _generate_event(
                ATTACKER, SERVER_B,
                random.choice([21, 22]), "TCP", "BruteForce", intensity
            )
        else:
            yield _generate_event(
                CLIENT_A, SERVER_B, 80, "TCP", "BENIGN", intensity
            )


def run_dos_scenario(
    network: VirtualNetwork, intensity: str, num_events: int
) -> Generator[dict, None, None]:
    """Single attacker floods Server B."""
    for _ in range(num_events):
        if random.random() < 0.95:
            yield _generate_event(
                ATTACKER, SERVER_B, 80, "TCP", "DoS", intensity
            )
        else:
            yield _generate_event(
                CLIENT_A, SERVER_B, 443, "TCP", "BENIGN", intensity
            )


def run_ddos_scenario(
    network: VirtualNetwork, intensity: str, num_events: int
) -> Generator[dict, None, None]:
    """Multiple distributed attackers flood Server B."""
    for _ in range(num_events):
        if random.random() < 0.95:
            atk_ip = random.choice(DDOS_IPS)
            yield _generate_event(
                atk_ip, SERVER_B, 80, "TCP", "DDoS", intensity
            )
        else:
            yield _generate_event(
                CLIENT_A, SERVER_B, 443, "TCP", "BENIGN", intensity
            )


def run_suspicious_scenario(
    network: VirtualNetwork, intensity: str, num_events: int
) -> Generator[dict, None, None]:
    """Mixed traffic — uncertain behavior that may confuse the model."""
    attack_types = ["PortScan", "BruteForce", "DoS", "DDoS"]

    for _ in range(num_events):
        r = random.random()
        if r < 0.40:
            # Normal traffic
            yield _generate_event(
                CLIENT_A, SERVER_B, 443, "TCP", "BENIGN", intensity
            )
        elif r < 0.70:
            # Random attack type from attacker
            atk_type = random.choice(attack_types)
            yield _generate_event(
                ATTACKER, SERVER_B,
                random.choice([21, 22, 80, 443]), "TCP", atk_type, intensity
            )
        else:
            # Benign-looking traffic from attacker IP (ambiguous)
            yield _generate_event(
                ATTACKER, SERVER_B, 443, "TCP", "BENIGN", intensity
            )


# ─── Scenario Registry ────────────────────────────────────────────────────────

SCENARIO_MAP = {
    "Normal Traffic":     run_normal_scenario,
    "Port Scan":          run_portscan_scenario,
    "Brute Force":        run_bruteforce_scenario,
    "DoS":                run_dos_scenario,
    "DDoS":               run_ddos_scenario,
    "Suspicious Traffic": run_suspicious_scenario,
}


def get_scenario_generator(
    scenario_name: str, network: VirtualNetwork,
    intensity: str, num_events: int
):
    """Return a generator for the named scenario."""
    func = SCENARIO_MAP.get(scenario_name, run_normal_scenario)
    return func(network, intensity, num_events)
