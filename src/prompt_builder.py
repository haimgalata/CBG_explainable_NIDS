from typing import Dict
import pandas as pd
import numpy as np
import json

# עמודות שמותר לשלוח ל-GPT
# כולל כל התצפיות, ללא עמודות תוצאה / החלטה
ALLOWED_FEATURES = [
    "ID",
    "IP_SRC_ADDR",
    "IP_DST_ADDR",
    "L4_SRC_PORT",
    "L4_DST_PORT",
    "PROTOCOL_NUM",
    "FIRST_SWITCHED",
    "LAST_SWITCHED",
    "IN_PKTS",
    "IN_BYTES",
    "FLOW_DURATION_MILLISECONDS",
    "avg_in_packet_size",
    "inter_arrival_ms",
    "dst_flows_in_window",
    "src_entropy_PROTOCOL",
    "src_IN_PKTS_sum",
    "src_flows_in_window",
    "src_flag_SYN"
]


def extract_observable_features(row: pd.Series) -> Dict[str, object]:
    """
    Extracts observable (non-decision) features from a NetFlow row
    and converts all values to JSON-serializable Python types.
    """
    observable_data = {}

    for feature in ALLOWED_FEATURES:
        if feature in row:
            value = row[feature]

            # Convert numpy / pandas types to native Python types
            if isinstance(value, (np.integer,)):
                value = int(value)
            elif isinstance(value, (np.floating,)):
                value = float(value)
            elif pd.isna(value):
                value = None
            else:
                value = str(value)

            observable_data[feature] = value

    return observable_data


def build_explanation_prompt(
    observable_features: dict,
    ipqs_fraud_score: int | None = None,
    vt_malicious_count: int | None = None
) -> str:

    features_json = json.dumps(observable_features, indent=2)

    external_context = ""

    if ipqs_fraud_score is not None or vt_malicious_count is not None:
        external_context = f"""
        External IP reputation signals (context only, not definitive evidence):
        - IPQualityScore fraud score: {ipqs_fraud_score}
        - VirusTotal malicious detections: {vt_malicious_count}
        """

    prompt = f"""
You are a cybersecurity analyst.

The following network flow was flagged as anomalous by an automated detection system.
This does NOT imply confirmed malicious activity.

Note:
Some features originate from external IP reputation services (e.g., VirusTotal, IPQualityScore).
These signals are contextual and probabilistic, and do NOT constitute definitive evidence of malicious activity.

{external_context}

You are provided with observable network flow features only.
Do NOT assume the traffic is malicious or benign.

Your task is to provide a concise, cautious assessment.

Respond in the following structure only:

1. Likelihood (0–1):
   A single numeric value.

2. Main reasons:
   2–3 short bullet points explaining the assessment.

3. Suspicious feature combination:
   Name a small group of features that are individually normal,
   but suspicious when considered together.

4. Resemblance to known attack behavior:
   State whether the behavior shows **no resemblance or only weak resemblance**
   to any general attack category.
   Only name a category if the resemblance is strong and unambiguous.
   Otherwise, explicitly state: "Insufficient evidence to suggest a known attack pattern."

5. Most informative feature:
   Name the single most informative feature or observation.

Important constraints:
- Be concise
- Do not use tables
- Do not exceed 6 short bullet points total
- Avoid definitive conclusions
- Avoid naming specific attacks unless clearly justified
- Prefer stating insufficient or weak evidence over naming an attack category

Network flow features:
{features_json}
"""
    return prompt


