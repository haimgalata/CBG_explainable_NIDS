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

# -------------------------------------------------
# Layer 1 – Basic Prompt OR Expert Basic Prompt
# -------------------------------------------------
def build_basic_prompt(
    observable_features: dict,
    assumption: str | None = None
) -> str:

    features_json = json.dumps(observable_features, indent=2)

    if assumption == "malicious":
        assumption_text = """
Assume the network flow is malicious.
Your task is to construct the strongest possible explanation supporting this hypothesis based only on the observable features.
"""
    elif assumption == "benign":
        assumption_text = """
Assume the network flow is benign.
Your task is to construct the strongest possible explanation supporting this hypothesis based only on the observable features.
"""
    else:
        assumption_text = ""

    if assumption is None:
        neutrality_text = "Do not assume the traffic is malicious or benign."
    else:
        neutrality_text = ""

    return f"""
    You are a cybersecurity analyst reviewing a network flow.

    {assumption_text}

    The flow was flagged as anomalous by an automated system, but this does NOT imply confirmed malicious activity.

    You are given only observable NetFlow features.
    {neutrality_text}

    Respond ONLY in the following structure:

    1. Malicious likelihood (0–1):
    A single numeric value.

    Scoring guidelines:
    - 0.8 – 1.0 → Strong evidence of malicious activity (multiple suspicious indicators)
    - 0.6 – 0.8 → Moderate evidence
    - 0.3 – 0.6 → Weak or uncertain evidence
    - 0.0 – 0.3 → Likely benign

    Important:
    - Be decisive when evidence is strong
    - Avoid clustering around 0.5 unless truly uncertain
    - Use the full range of the scale

    2. Main reasons:
    2–3 short bullet points explaining the assessment.

    3. Suspicious feature combination:
    Features that are individually normal but suspicious together.

    4. Resemblance to known attack behavior:
    State whether there is no or only weak resemblance to a known attack.
    Only name an attack category if evidence is strong.
    Otherwise say: "Insufficient evidence to suggest a known attack pattern."

    5. Most informative feature:
    The single most informative feature.

    Rules:
    - Be concise
    - No tables
    - Avoid overconfidence, but be decisive when evidence is strong

    Network flow features:
    {features_json}
    """


# -------------------------------------------------
# Layer 2 – Augmented Prompt OR Expert Augmented Prompt
# -------------------------------------------------
def build_augmented_prompt(
    observable_features: dict,
    ipqs_fraud_score: int | None,
    vt_malicious_count: int | None,
    abuse_score: int | None,
    assumption: str | None = None
) -> str:

    protocol_num = observable_features.get("PROTOCOL_NUM")
    protocol_explanation = explain_protocol(protocol_num)

    autoencoder_score = observable_features.get("score_Autoencoder")

    features_json = json.dumps(observable_features, indent=2)

    if assumption == "malicious":
        assumption_text = """
Assume the network flow is malicious.
Your task is to construct the strongest possible explanation supporting this hypothesis based only on the observable features.
"""
    elif assumption == "benign":
        assumption_text = """
Assume the network flow is benign.
Your task is to construct the strongest possible explanation supporting this hypothesis based only on the observable features.
"""
    else:
        assumption_text = ""

    if assumption is None:
        neutrality_text = "Do not assume the traffic is malicious or benign."
    else:
        neutrality_text = ""

    external_context = f"""
External IP reputation signals:

These signals provide supporting evidence and should influence your assessment.
High values across multiple sources significantly increase the likelihood of malicious activity.

- IPQualityScore fraud score: {ipqs_fraud_score}
- VirusTotal malicious detections: {vt_malicious_count}
- AbuseIPDB confidence score: {abuse_score}
"""

    feature_context = f"""
Feature context:

Protocol:
PROTOCOL_NUM = {protocol_num} ({protocol_explanation})

Autoencoder anomaly score:
score_Autoencoder = {autoencoder_score} (higher = more anomalous)
"""

    return f"""
You are a cybersecurity analyst reviewing a network flow.

{assumption_text}

The flow was flagged as anomalous by an automated detection system, but this does NOT imply confirmed malicious activity.

{external_context}

{feature_context}

You are given only observable NetFlow features.
{neutrality_text}

Respond ONLY in the following structure:

1. Malicious likelihood (0–1):
A single numeric value.

Scoring guidelines:
- 0.8 – 1.0 → Strong evidence of malicious activity (especially if multiple CTI sources are high)
- 0.6 – 0.8 → Moderate evidence (some suspicious features)
- 0.3 – 0.6 → Weak evidence
- 0.0 – 0.3 → Likely benign 

Important:
- Use CTI signals as supporting evidence, not the only factor
- Combine CTI with flow behavior
- Be decisive when evidence is strong


2. Main reasons:
2–3 short bullet points explaining the assessment.

3. Suspicious feature combination:
Features that are individually normal but suspicious together.

4. Resemblance to known attack behavior:
State whether there is no or only weak resemblance to a known attack.
Only name an attack category if evidence is strong.
Otherwise say: "Insufficient evidence to suggest a known attack pattern."


Rules:
- Be concise
- No tables
- Avoid overconfidence, but be decisive when multiple signals align

Network flow features:
{features_json}
"""

# -------------------------------------------------
# Consensus – Judge Prompt
# -------------------------------------------------
def build_consensus_prompt(
    observable_features: dict,
    attack_explanation: str,
    benign_explanation: str,
    ipqs_fraud_score: int | None = None,
    vt_malicious_count: int | None = None,
    abuse_score: int | None = None,
    use_context: bool = False
) -> str:

    features_json = json.dumps(observable_features, indent=2)

    cti_block = ""
    feature_context = ""

    if use_context:

        protocol_num = observable_features.get("PROTOCOL_NUM")
        protocol_explanation = explain_protocol(protocol_num)

        autoencoder_score = observable_features.get("score_Autoencoder")

        cti_block = f"""
External IP reputation signals:

These signals provide supporting evidence and should influence your decision.
Consistent high values across multiple sources strongly indicate malicious activity.

- IPQualityScore fraud score: {ipqs_fraud_score}
- VirusTotal malicious detections: {vt_malicious_count}
- AbuseIPDB confidence score: {abuse_score}
"""

        feature_context = f"""
Feature context:

Protocol:
PROTOCOL_NUM = {protocol_num} ({protocol_explanation})

Autoencoder anomaly score:
score_Autoencoder = {autoencoder_score} (higher = more anomalous)
"""

    return f"""
You are a senior cybersecurity analyst acting as a strict and decisive judge.

You are given:
1) Network flow features
2) Expert A opinion 
3) Expert B opinion 

Your task is to compare both explanations and determine which is better supported by the evidence.

You MUST make a clear decision when evidence favors one side.

Do NOT assume either expert is correct.
Prefer reasoning grounded in the provided evidence.
Identify unsupported assumptions or weak reasoning.

Respond ONLY in the following structure:

1. Malicious likelihood (0–1):
A single numeric value.

2. Which expert is more accurate:
A / B 

3. Key justification:
2–3 short bullet points.

4. Confidence (0–1):
A single numeric value between 0 and 1 representing how confident you are in your decision.

--------------------------------------------------

Scoring guidelines:
- 0.8 – 1.0 → Strong evidence supporting malicious interpretation (Expert A correct)
- 0.6 – 0.8 → Moderate support for malicious
- 0.3 – 0.6 → Mixed or uncertain evidence
- 0.0 – 0.3 → Strong evidence supporting benign interpretation (Expert B correct)

Important:
- Do NOT default to the middle (0.5)
- If one explanation is clearly stronger → push the score toward extremes
- Use the full range of the scale
- Base your decision on evidence, not wording quality

Decision rules:
- If Expert A is clearly better supported → score above 0.7
- If Expert B is clearly better supported → score below 0.3
- If both are weak or equally supported → stay in mid range

--------------------------------------------------


Network flow features:
{features_json}

{cti_block}

{feature_context}

--------------------------------------------------

Expert A (malicious assumption):
{attack_explanation}

--------------------------------------------------

Expert B (benign assumption):
{benign_explanation}
"""

# להוסיף חלוקה על flow זדוני לשלוח ל LLM 3 API נפרדים: ב1 מצאתי מידע לגבי הבכל השירותים, 2 מצאתי רק בחלק ובחלק הוא מפויע 0, 3 לא מצאתי כלום
