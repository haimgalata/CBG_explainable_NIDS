"""
Synthetic CTI (Cyber Threat Intelligence) for experiment design.

Current: Binary (attack=high scores, benign=zeros). Random attack category.

Improvement ideas (see EXPERIMENTS.md):
- full_cti: All 3 services return signals (like current attack profile)
- partial_cti: Only 1-2 services return signals, others 0 (realistic incomplete intel)
- no_cti: All zeros even for attacks (simulate false negative / missing intel)
- severity_levels: Low/medium/high attack severity with corresponding score ranges
"""
import random


ATTACK_PROFILES = {
    "scanner": {
        "abuse_score": (40, 65),
        "vt_malicious_count": (0, 2),
        "ipqs_fraud_score": (35, 60),
    },
    "ddos": {
        "abuse_score": (70, 90),
        "vt_malicious_count": (0, 5),
        "ipqs_fraud_score": (60, 85),
    },
    "malware": {
        "abuse_score": (85, 100),
        "vt_malicious_count": (10, 35),
        "ipqs_fraud_score": (80, 100),
    }
}


def generate_random_attack_profile(label: int):

    # אם תקיפה → תן CTI אמיתי
    if label == 1:
        category = random.choice(list(ATTACK_PROFILES.keys()))
        profile = ATTACK_PROFILES[category]

        return {
            "category": category,
            "abuse_score": random.randint(*profile["abuse_score"]),
            "vt_malicious_count": random.randint(*profile["vt_malicious_count"]),
            "ipqs_fraud_score": random.randint(*profile["ipqs_fraud_score"]),
        }

    # אם benign → אפסים
    else:
        return {
            "category": "benign",
            "abuse_score": 0,
            "vt_malicious_count": 0,
            "ipqs_fraud_score": 0,
        }