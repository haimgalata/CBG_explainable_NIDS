import time
from datetime import datetime

from src.prompt_builder import (extract_observable_features, build_expert_prompt, build_consensus_prompt, build_expert_prompt_augmented,count_llm_tokens, extract_llm_likelihood)
from src.clients.gpt_client import GPTClient
from src.clients.gemini_client import GeminiClient
from src.md_writer import write_flow_md
from src.services.ipqualityscore_service import IPQSASNScoreService
from src.services.virustotal_service import VirusTotalService
from src.services.abuseipdb_service import AbuseIPDBService
from src.services.synthetic_reputation import generate_random_attack_profile
from src.config import IPQS_API_KEY, VT_API_KEY, ABUSE_IPDB_API_KEY


def run_consensus_layer(rows, run_output_dir, use_augmentation=False, reputation_mode="default"):
    #llm = GeminiClient()
    llm = GPTClient()

    results = []

    if use_augmentation:
        ipqs_service = IPQSASNScoreService(api_key=IPQS_API_KEY)
        vt_service = VirusTotalService(api_key=VT_API_KEY)
        abuse_service = AbuseIPDBService(api_key=ABUSE_IPDB_API_KEY)

    for idx, row in enumerate(rows, start=1):

        ip_reputation_found = 0

        dst_ip = row["IP_DST_ADDR"]

        if use_augmentation:

            if reputation_mode == "real":

                ipqs_fraud_score = ipqs_service.get_fraud_score(dst_ip)
                vt_malicious_count = vt_service.get_malicious_count(dst_ip)
                abuse_score = abuse_service.get_abuse_score(dst_ip)

            elif reputation_mode == "synthetic":

                profile = generate_random_attack_profile()

                ipqs_fraud_score = profile["ipqs_fraud_score"]
                vt_malicious_count = profile["vt_malicious_count"]
                abuse_score = profile["abuse_score"]

            else:  # default

                ipqs_fraud_score = 0
                vt_malicious_count = 0
                abuse_score = 0

            if use_augmentation and any([ipqs_fraud_score, vt_malicious_count, abuse_score]):
                ip_reputation_found = 1


        observable = extract_observable_features(row)

        # -------------------------
        # Expert A – Malicious
        # -------------------------
        if use_augmentation:

            prompt_attack = build_expert_prompt_augmented(
                observable,
                "malicious",
                ipqs_fraud_score,
                vt_malicious_count,
                abuse_score
            )

        else:

            prompt_attack = build_expert_prompt(observable, "malicious")

        start_time = time.perf_counter()
        explanation_attack = llm.explain(prompt_attack)
        end_time = time.perf_counter()

        latency_attack = end_time - start_time

        Malicious_llm_likelihood = extract_llm_likelihood(explanation_attack)
        Malicious_llm_response_length = len(explanation_attack)
        Malicious_llm_response_tokens = count_llm_tokens(explanation_attack)

        # -------------------------
        # Expert B – Benign
        # -------------------------
        if use_augmentation:

            prompt_benign = build_expert_prompt_augmented(
                observable,
                "benign",
                ipqs_fraud_score,
                vt_malicious_count,
                abuse_score
            )

        else:

            prompt_benign = build_expert_prompt(observable, "benign")

        start_time = time.perf_counter()
        explanation_benign = llm.explain(prompt_benign)
        end_time = time.perf_counter()

        latency_benign = end_time - start_time

        Benign_llm_likelihood = extract_llm_likelihood(explanation_benign)
        Benign_llm_response_length = len(explanation_benign)
        Benign_llm_response_tokens = count_llm_tokens(explanation_benign)

        # -------------------------
        # Judge
        # -------------------------
        prompt_judge = build_consensus_prompt(
            observable,
            explanation_attack,
            explanation_benign
        )

        start_time = time.perf_counter()
        final_decision = llm.explain(prompt_judge)
        end_time = time.perf_counter()

        latency_judge = end_time - start_time

        Decision_llm_likelihood = extract_llm_likelihood(final_decision)
        Decision_llm_response_length = len(final_decision)
        Decision_llm_response_tokens = count_llm_tokens(final_decision)

        # -------------------------
        # Write MD
        # -------------------------
        write_flow_md(
            flow_id=observable.get("ID", idx),
            features=observable,
            explanation=f"""
## Expert A – Attack Hypothesis
{explanation_attack}

## Expert B – Benign Hypothesis
{explanation_benign}

## Consensus Decision
{final_decision}
""",
            output_dir=run_output_dir
        )

        results.append({
            "flow_index": idx,
            "timestamp": datetime.now().isoformat(),
            "layer": "consensus",
            "model": llm.__class__.__name__,
            "latency_attack": round(latency_attack, 3),
            "latency_benign": round(latency_benign, 3),
            "latency_judge": round(latency_judge, 3),
            "observable_features": observable,
            "ip_reputation_found": ip_reputation_found,
            "use_augmentation": use_augmentation,
            "reputation_mode": reputation_mode,
            "Malicious_llm_likelihood": Malicious_llm_likelihood,
            "Malicious_llm_response_length": Malicious_llm_response_length,
            "Malicious_llm_response_tokens": Malicious_llm_response_tokens,
            "Benign_llm_likelihood": Benign_llm_likelihood,
            "Benign_llm_response_length": Benign_llm_response_length,
            "Benign_llm_response_tokens": Benign_llm_response_tokens,
            "Decision_llm_likelihood": Decision_llm_likelihood,
            "Decision_llm_response_length": Decision_llm_response_length,
            "Decision_llm_response_tokens": Decision_llm_response_tokens,
            "expert_attack": explanation_attack,
            "expert_benign": explanation_benign,
            "final_decision": final_decision
        })

    return results