"""
simulation/simulator.py

Simulation coordinator for AI-SNIDS.

Generates synthetic flow events, passes them through the REAL
trained Random Forest model, and logs results to SQLite.

Includes application-level simulated blocking:
- If the AI + Risk Engine recommends BLOCK, the source IP is
  added to the BlockedIP table.
- Future events from that IP are automatically rejected.

SAFETY: This is entirely software-level. No OS firewall rules
are created or modified.
"""

from ai.predict import get_predictor
from database.database import get_session
from database.models import SecurityEvent, BlockedIP
from simulation.network import create_default_topology
from simulation.scenarios import get_scenario_generator


def _is_ip_blocked(session, ip: str) -> bool:
    """Check if an IP is on the simulated blocklist."""
    blocked = session.query(BlockedIP).filter_by(
        ip_address=ip, is_active=True
    ).first()
    return blocked is not None


def _add_to_blocklist(session, ip: str, reason: str):
    """Add an IP to the simulated blocklist (or increment count)."""
    existing = session.query(BlockedIP).filter_by(ip_address=ip).first()
    if existing:
        existing.event_count += 1
        existing.is_active = True
    else:
        session.add(BlockedIP(
            ip_address=ip,
            reason=reason,
        ))


def process_simulated_event(event_dict: dict) -> dict:
    """
    Process a single simulated event through the real AI pipeline.

    Returns a dict with all event data + blocking metadata.
    """
    predictor = get_predictor()
    src_ip = event_dict["source_ip"]

    session = get_session()
    try:
        # Check if this IP is already on the simulated blocklist
        if _is_ip_blocked(session, src_ip):
            # Event is rejected — IP was previously blocked
            db_event = SecurityEvent(
                source_ip=src_ip,
                destination_ip=event_dict["destination_ip"],
                source_port=event_dict["source_port"],
                destination_port=event_dict["destination_port"],
                protocol=event_dict["protocol"],
                attack_type="BLOCKED",
                confidence=1.0,
                risk_level="HIGH",
                risk_score=1.0,
                action="BLOCK",
                is_blocked=True,
                notes=f"Traffic rejected — {src_ip} is on the simulated blocklist.",
                data_source="SIMULATION",
                simulation_scenario=event_dict["scenario"],
            )
            session.add(db_event)
            session.commit()
            session.refresh(db_event)

            return {
                "db_event": db_event,
                "was_blocked": True,
                "prediction": {
                    "predicted_class": "BLOCKED",
                    "confidence": 1.0,
                    "risk_level": "HIGH",
                    "risk_score": 1.0,
                    "action": "BLOCK",
                    "is_attack": True,
                    "explanation": f"Source {src_ip} is on the simulated blocklist. Traffic rejected.",
                },
            }

        # Run real AI prediction
        prediction = predictor.predict(event_dict["features"])

        db_event = SecurityEvent(
            source_ip=src_ip,
            destination_ip=event_dict["destination_ip"],
            source_port=event_dict["source_port"],
            destination_port=event_dict["destination_port"],
            protocol=event_dict["protocol"],
            attack_type=prediction["predicted_class"],
            confidence=prediction["confidence"],
            risk_level=prediction["risk_level"],
            risk_score=prediction["risk_score"],
            action=prediction["action"],
            is_blocked=(prediction["action"] == "BLOCK"),
            notes=prediction["explanation"],
            data_source="SIMULATION",
            simulation_scenario=event_dict["scenario"],
        )
        session.add(db_event)

        # If BLOCK action or detected attack from simulated attacker
        should_block = (
            prediction["action"] == "BLOCK"
            or (prediction["predicted_class"] != "BENIGN" and prediction["confidence"] >= 0.75)
        )
        if should_block and src_ip not in ("unknown", "N/A"):
            _add_to_blocklist(
                session, src_ip,
                f"Auto-defense: {prediction['predicted_class']} detected "
                f"(confidence {prediction['confidence']*100:.1f}%, risk {prediction['risk_level']})"
            )

        session.commit()
        session.refresh(db_event)

        return {
            "db_event": db_event,
            "was_blocked": False,
            "prediction": prediction,
        }

    finally:
        session.close()


def generate_simulation_batch(
    scenario_name: str,
    intensity: str,
    duration_sec: int,
    injected_attack: str = "None (Pure Scenario)",
    switch_ratio: float = 0.4,
) -> list:
    """
    Pre-generate a bounded batch of flow events.
    Supports mid-stream sudden attack injection when injected_attack is set.
    Cap at 500 events to prevent UI hang.
    """
    multiplier = {"LOW": 0.5, "MEDIUM": 1.0, "HIGH": 2.0}.get(intensity, 1.0)
    events_per_sec = int(10 * multiplier)
    total_events = min(duration_sec * events_per_sec, 500)

    net = create_default_topology()

    if injected_attack and injected_attack not in ("None (Pure Scenario)", "None", ""):
        from simulation.scenarios import run_dynamic_switch_scenario
        generator = run_dynamic_switch_scenario(
            network=net,
            initial_scenario=scenario_name,
            injected_attack=injected_attack,
            intensity=intensity,
            num_events=total_events,
            switch_ratio=switch_ratio,
        )
    else:
        generator = get_scenario_generator(scenario_name, net, intensity, total_events)

    return list(generator)


def run_instant_attack_burst(scenario_name: str, count: int = 5, intensity: str = "HIGH") -> list[dict]:
    """
    Generate and process an immediate, sudden attack burst.
    Used for instant real-time attack injection pad.
    """
    net = create_default_topology()
    events = list(get_scenario_generator(scenario_name, net, intensity, count))
    results = []
    for event in events:
        res = process_simulated_event(event)
        results.append(res)
    return results

