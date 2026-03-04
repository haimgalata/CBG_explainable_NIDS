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


def generate_random_attack_profile():
    category = random.choice(list(ATTACK_PROFILES.keys()))
    profile = ATTACK_PROFILES[category]

    return {
        "category": category,
        "abuse_score": random.randint(*profile["abuse_score"]),
        "vt_malicious_count": random.randint(*profile["vt_malicious_count"]),
        "ipqs_fraud_score": random.randint(*profile["ipqs_fraud_score"]),
    }