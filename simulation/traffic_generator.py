import random
from copy import deepcopy
from network.feature_extraction import get_benign_sample, get_attack_samples

def apply_jitter(features: dict, intensity_level: str) -> dict:
    """
    Applies small random noise (jitter) to the features so that 
    generated flows don't look identically hardcoded.
    
    intensity_level: "LOW", "MEDIUM", "HIGH"
    """
    jitter_scale = {
        "LOW": 0.05,     # 5% variation
        "MEDIUM": 0.15,  # 15% variation
        "HIGH": 0.30     # 30% variation
    }.get(intensity_level, 0.10)
    
    new_features = deepcopy(features)
    for key, val in new_features.items():
        if val > 0:
            # Random uniform multiplier between (1 - scale) and (1 + scale)
            multiplier = 1.0 + random.uniform(-jitter_scale, jitter_scale)
            new_features[key] = float(val * multiplier)
            
    return new_features

def generate_synthetic_flow(scenario: str, intensity_level: str) -> dict:
    """
    Retrieves the exact CICIDS2017 feature medians for the given scenario
    and applies random jitter.
    
    scenario: "BENIGN", "PortScan", "DoS", "DDoS", "BruteForce"
    """
    if scenario == "BENIGN":
        base_features = get_benign_sample()
    else:
        attacks = get_attack_samples()
        base_features = attacks.get(scenario, get_benign_sample())
        
    return apply_jitter(base_features, intensity_level)
