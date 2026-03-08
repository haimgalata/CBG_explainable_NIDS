from typing import Dict
import pandas as pd
import numpy as np
import json

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
    "src_flag_SYN",
    "score_Autoencoder"
]

PROTOCOL_MAP = {
    0: "HOPOPT – IPv6 Hop-by-Hop Option",
    1: "ICMP – Internet Control Message Protocol (used for ping and diagnostics)",
    2: "IGMP – Internet Group Management Protocol (multicast group management)",
    3: "GGP – Gateway-to-Gateway Protocol",
    4: "IPv4 – IPv4 encapsulation",
    5: "ST – Stream Protocol",
    6: "TCP – Transmission Control Protocol (used for HTTP, HTTPS, SSH, etc.)",
    7: "CBT – Core-Based Trees",
    8: "EGP – Exterior Gateway Protocol",
    9: "IGP – Interior Gateway Protocol",
    10: "BBN-RCC-MON",
    11: "NVP-II – Network Voice Protocol",
    12: "PUP – PARC Universal Packet",
    13: "ARGUS",
    14: "EMCON",
    15: "XNET",
    16: "CHAOS",
    17: "UDP – User Datagram Protocol (DNS, streaming, VoIP)",
    18: "MUX – Multiplexing",
    19: "DCN-MEAS",
    20: "HMP – Host Monitoring Protocol",
    21: "PRM – Packet Radio Measurement",
    22: "XNS-IDP – Xerox Network Services IDP",
    23: "TRUNK-1",
    24: "TRUNK-2",
    25: "LEAF-1",
    26: "LEAF-2",
    27: "RDP – Reliable Data Protocol",
    28: "IRTP – Internet Reliable Transaction Protocol",
    29: "ISO-TP4 – ISO Transport Protocol Class 4",
    30: "NETBLT – Bulk Data Transfer Protocol",
    31: "MFE-NSP",
    32: "MERIT-INP",
    33: "DCCP – Datagram Congestion Control Protocol",
    34: "3PC – Third Party Connect Protocol",
    35: "IDPR – Inter-Domain Policy Routing",
    36: "XTP – Xpress Transfer Protocol",
    37: "DDP – Datagram Delivery Protocol",
    38: "IDPR-CMTP",
    39: "TP++ – Transport Protocol",
    40: "IL – IL Transport Protocol",
    41: "IPv6 – IPv6 encapsulation",
    42: "SDRP – Source Demand Routing Protocol",
    43: "IPv6-Route – Routing Header for IPv6",
    44: "IPv6-Frag – Fragment Header for IPv6",
    45: "IDRP – Inter-Domain Routing Protocol",
    46: "RSVP – Resource Reservation Protocol",
    47: "GRE – Generic Routing Encapsulation (used in VPN tunnels)",
    48: "DSR – Dynamic Source Routing Protocol",
    49: "BNA",
    50: "ESP – Encapsulating Security Payload (IPsec)",
    51: "AH – Authentication Header (IPsec)",
    52: "I-NLSP – Integrated Net Layer Security Protocol",
    53: "SWIPE",
    54: "NARP – NBMA Address Resolution Protocol",
    55: "MOBILE – Mobile IP",
    56: "TLSP – Transport Layer Security Protocol",
    57: "SKIP – Simple Key Management for Internet Protocol",
    58: "ICMPv6 – ICMP for IPv6",
    59: "IPv6-NoNxt – No Next Header for IPv6",
    60: "IPv6-Opts – Destination Options for IPv6",
    61: "Host Internal Protocol",
    62: "CFTP – CFTP",
    63: "Local Network Protocol",
    64: "SAT-EXPAK",
    65: "KRYPTOLAN",
    66: "RVD – MIT Remote Virtual Disk",
    67: "IPPC",
    68: "Distributed File System",
    69: "SAT-MON",
    70: "VISA",
    71: "IPCV",
    72: "CPNX",
    73: "CPHB",
    74: "WSN – Wang Span Network",
    75: "PVP – Packet Video Protocol",
    76: "BR-SAT-MON",
    77: "SUN-ND",
    78: "WB-MON",
    79: "WB-EXPAK",
    80: "ISO-IP",
    81: "VMTP – Versatile Message Transport Protocol",
    82: "SECURE-VMTP",
    83: "VINES",
    84: "TTP",
    85: "NSFNET-IGP",
    86: "DGP – Dissimilar Gateway Protocol",
    87: "TCF",
    88: "EIGRP – Cisco routing protocol",
    89: "OSPF – Open Shortest Path First routing protocol",
    90: "Sprite RPC",
    91: "LARP – Locus Address Resolution Protocol",
    92: "MTP – Multicast Transport Protocol",
    93: "AX.25 – Amateur Packet Radio",
    94: "IPIP – IP-in-IP encapsulation",
    95: "MICP – Mobile Internetworking Control Protocol",
    96: "SCC-SP",
    97: "ETHERIP – Ethernet over IP",
    98: "ENCAP – Encapsulation Header",
    99: "Private Encryption Scheme",
    100: "GMTP – General Multicast Transport Protocol",
    101: "IFMP – Ipsilon Flow Management Protocol",
    102: "PNNI – PNNI over IP",
    103: "PIM – Protocol Independent Multicast",
    104: "ARIS",
    105: "SCPS – Space Communications Protocol",
    106: "QNX",
    107: "A/N – Active Networks",
    108: "IPComp – IP Payload Compression Protocol",
    109: "SNP – Sitara Networks Protocol",
    110: "Compaq-Peer",
    111: "IPX-in-IP",
    112: "VRRP – Virtual Router Redundancy Protocol",
    113: "PGM – Pragmatic General Multicast",
    114: "ZeroHop",
    115: "L2TP – Layer 2 Tunneling Protocol",
    116: "DDX",
    117: "IATP",
    118: "STP – Schedule Transfer Protocol",
    119: "SRP – SpectraLink Radio Protocol",
    120: "UTI",
    121: "SMP",
    122: "SM – Simple Message Protocol",
    123: "PTP – Performance Transparency Protocol",
    124: "ISIS over IPv4",
    125: "FIRE",
    126: "CRTP – Combat Radio Transport Protocol",
    127: "CRUDP",
    128: "SSCOPMCE",
    129: "IPLT",
    130: "SPS – Secure Packet Shield",
    131: "PIPE",
    132: "SCTP – Stream Control Transmission Protocol",
    133: "FC – Fibre Channel",
    134: "RSVP-E2E-IGNORE",
    135: "Mobility Header",
    136: "UDPLite – Lightweight UDP",
    137: "MPLS-in-IP",
    138: "MANET – Mobile Ad-hoc Networks",
    139: "HIP – Host Identity Protocol",
    140: "Shim6 – Site Multihoming by IPv6 Intermediation",
    141: "WESP – Wrapped Encapsulating Security Payload",
    142: "ROHC – Robust Header Compression"
}

def explain_protocol(protocol_num):
    return PROTOCOL_MAP.get(protocol_num, "Unknown protocol number")

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

import re

def extract_llm_likelihood(text: str) -> float | None:

    match = re.search(
        r'Likelihood.*?\n\s*[*]*\s*([0-9]*\.?[0-9]+)',
        text,
        re.IGNORECASE
    )

    if match:
        return float(match.group(1))

    return None

# -------------------------------------------------
# Layer 1 – Basic Prompt (Raw only)
# -------------------------------------------------
def build_basic_prompt(observable_features: dict) -> str:

    features_json = json.dumps(observable_features, indent=2)

    return f"""
You are a cybersecurity analyst.

The following network flow was flagged as anomalous by an automated detection system.
This does NOT imply confirmed malicious activity.

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
   Otherwise, explicitly state:
   "Insufficient evidence to suggest a known attack pattern."

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

# -------------------------------------------------
# Layer 2 – Augmented Prompt
# -------------------------------------------------
def build_augmented_prompt(
    observable_features: dict,
    ipqs_fraud_score: int | None,
    vt_malicious_count: int | None,
    abuse_score : int | None
) -> str:

    protocol_num = observable_features.get("PROTOCOL_NUM")
    protocol_explanation = explain_protocol(protocol_num)

    autoencoder_score = observable_features.get("score_Autoencoder")
    features_json = json.dumps(observable_features, indent=2)

    external_context = f"""
Note:
Some features originate from external IP reputation services 
(e.g., VirusTotal, IPQualityScore, AbuseIPDB).
These signals are contextual and probabilistic, 
and do NOT constitute definitive evidence of malicious activity.

External IP reputation signals:
- IPQualityScore fraud score: {ipqs_fraud_score}
- VirusTotal malicious detections: {vt_malicious_count}
- AbuseIPDB confidence score: {abuse_score}
"""
    feature_context = f"""
Feature context:

Protocol information:
- PROTOCOL_NUM = {protocol_num}
- {protocol_explanation}

Autoencoder anomaly score:
- score_Autoencoder = {autoencoder_score}

The autoencoder score represents how anomalous the flow is according to an
unsupervised anomaly detection model.
Higher values indicate that the flow deviates more from normal traffic patterns.
"""

    return f"""
You are a cybersecurity analyst.

The following network flow was flagged as anomalous by an automated detection system.
This does NOT imply confirmed malicious activity.

{external_context}

{feature_context}

You are provided with observable network flow features.
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
   Otherwise, explicitly state:
   "Insufficient evidence to suggest a known attack pattern."

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

def build_expert_prompt_augmented(
    observable_features,
    assumption,
    ipqs_fraud_score,
    vt_malicious_count,
    abuse_score
):

    protocol_num = observable_features.get("PROTOCOL_NUM")
    protocol_explanation = explain_protocol(protocol_num)

    autoencoder_score = observable_features.get("score_Autoencoder")

    features_json = json.dumps(observable_features, indent=2)

    if assumption == "malicious":
        role_text = "Assume the network flow is malicious."
    else:
        role_text = "Assume the network flow is benign."

    return f"""
You are a cybersecurity analyst.

{role_text}

External IP reputation signals:

- IPQualityScore fraud score: {ipqs_fraud_score}
- VirusTotal malicious detections: {vt_malicious_count}
- AbuseIPDB confidence score: {abuse_score}

Protocol information:
PROTOCOL_NUM = {protocol_num}
{protocol_explanation}

Autoencoder anomaly score:
score_Autoencoder = {autoencoder_score}

The autoencoder score indicates how anomalous the flow is according to an unsupervised model.

Respond strictly:

1. Likelihood (0–1):
   A single numeric value.
2. Main reasons (2–3 bullet points)
3. Most informative feature

Network flow:
{features_json}
"""

# -------------------------------------------------
# Consensus – Expert Prompt
# -------------------------------------------------
def build_expert_prompt(observable_features: dict, assumption: str) -> str:
    import json

    features_json = json.dumps(observable_features, indent=2)

    if assumption == "malicious":
        role_text = """
Assume the network flow is malicious.
Your role is to build the strongest possible argument that it represents malicious activity.
"""
    elif assumption == "benign":
        role_text = """
Assume the network flow is benign.
Your role is to build the strongest possible argument that it represents normal, legitimate traffic.
"""
    else:
        raise ValueError("Assumption must be 'malicious' or 'benign'")

    return f"""
You are a cybersecurity analyst.

{role_text}

Important:
Likelihood (0–1) must represent:
the likelihood that the flow is malicious.

Even if you assume it is benign, you must still provide
a likelihood estimate of malicious activity.

Base your reasoning strictly on the observable features.
Avoid speculation.
Be concise.

Respond strictly in this structure:

1. Likelihood (0–1) – likelihood that the flow is malicious
   A single numeric value.
2. Main reasons (2–3 bullet points)
3. Most informative feature

Network flow:
{features_json}
"""

# -------------------------------------------------
# Consensus – Judge Prompt
# -------------------------------------------------
def build_consensus_prompt(
    observable_features: dict,
    attack_explanation: str,
    benign_explanation: str
) -> str:
    import json

    features_json = json.dumps(observable_features, indent=2)

    return f"""
You are a senior cybersecurity analyst acting as a neutral judge.

You are given:

1) Network flow features
2) Expert A opinion (assumes malicious)
3) Expert B opinion (assumes benign)

Your task:

- Compare both explanations
- Evaluate which is more logically grounded in the observable features
- Identify weak or unsupported reasoning
- Provide a final balanced decision

Do NOT assume either expert is correct.
Prefer reasoning that is strictly feature-based.

Respond strictly in this structure:

1. Likelihood (0–1).
   A single numeric value.
2. Which expert is more convincing (A or B or Balanced)
3. Key justification (2–3 bullet points)
4. Most decisive feature

--------------------------------------------------

Network flow:
{features_json}

--------------------------------------------------

Expert A (Malicious assumption):
{attack_explanation}

--------------------------------------------------

Expert B (Benign assumption):
{benign_explanation}
"""

import tiktoken

def count_llm_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    return len(tokens)