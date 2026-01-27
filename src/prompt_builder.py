from typing import Dict
import pandas as pd
import numpy as np

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


import json

def build_explanation_prompt(observable_features: dict) -> str:
    features_json = json.dumps(observable_features, indent=2)

    prompt = f"""
You are a cybersecurity analyst.

The following network flow was flagged as anomalous by an upstream
detection system.
This does NOT imply confirmed malicious activity.

You are given observable network flow measurements only.
Do NOT assume the flow is malicious or benign.
Do NOT name any attack or classification.

Your task:
- Analyze the network behavior described by the features
- Identify characteristics that may have contributed to the anomaly score
- Explain possible reasons cautiously and factually
- Avoid definitive conclusions

Network flow features:
{features_json}

Provide a clear, structured explanation in plain English.
"""
    return prompt
