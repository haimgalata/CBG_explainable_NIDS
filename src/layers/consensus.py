import time
from datetime import datetime

from src.prompt_builder import (
    extract_observable_features,
    build_basic_prompt,
    build_augmented_prompt,
    build_consensus_prompt
)

from src.clients.gpt_client import GPTClient
from src.clients.gemini_client import GeminiClient

from src.md_writer import write_flow_md

from src.services.ipqualityscore_service import IPQSASNScoreService
from src.services.virustotal_service import VirusTotalService
from src.services.abuseipdb_service import AbuseIPDBService
from src.services.synthetic_reputation import generate_random_attack_profile

from src.config import IPQS_API_KEY, VT_API_KEY, ABUSE_IPDB_API_KEY

from src.utils.llm_utils import extract_llm_likelihood, count_llm_tokens


def run_consensus_layer(rows, run_output_dir, use_augmentation=False, reputation_mode="default"):

    # llm = GeminiClient()
    llm = GPTClient()

    results = []

    if use_augmentation:
        ipqs_service = IPQSASNScoreService(api_key=IPQS_API_KEY)
        vt_service = VirusTotalService(api_key=VT_API_KEY)
        abuse_service = AbuseIPDBService(api_key=ABUSE_IPDB_API_KEY)

    for idx, row in enumerate(rows, start=1):

        dst_ip = row["IP_DST_ADDR"]

        # -------------------------
        # External enrichment (CTI)
        # -------------------------
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

            ip_reputation_found = int(any([
                ipqs_fraud_score,
                vt_malicious_count,
                abuse_score
            ]))

        else:
            ipqs_fraud_score = 0
            vt_malicious_count = 0
            abuse_score = 0
            ip_reputation_found = 0

        observable = extract_observable_features(row)

        autoencoder_score = observable.get("score_Autoencoder")

        # -------------------------
        # Expert A – Malicious
        # -------------------------
        if use_augmentation:

            prompt_attack = build_augmented_prompt(
                observable,
                ipqs_fraud_score,
                vt_malicious_count,
                abuse_score,
                assumption="malicious"
            )

        else:

            prompt_attack = build_basic_prompt(
                observable,
                assumption="malicious"
            )

        start_time = time.perf_counter()
        explanation_attack = llm.explain(prompt_attack)
        end_time = time.perf_counter()

        latency_attack = end_time - start_time

        malicious_llm_likelihood = extract_llm_likelihood(explanation_attack)
        malicious_llm_response_length = len(explanation_attack)
        malicious_llm_response_tokens = count_llm_tokens(explanation_attack)

        # -------------------------
        # Expert B – Benign
        # -------------------------
        if use_augmentation:

            prompt_benign = build_augmented_prompt(
                observable,
                ipqs_fraud_score,
                vt_malicious_count,
                abuse_score,
                assumption="benign"
            )

        else:

            prompt_benign = build_basic_prompt(
                observable,
                assumption="benign"
            )

        start_time = time.perf_counter()
        explanation_benign = llm.explain(prompt_benign)
        end_time = time.perf_counter()

        latency_benign = end_time - start_time

        benign_llm_likelihood = extract_llm_likelihood(explanation_benign)
        benign_llm_response_length = len(explanation_benign)
        benign_llm_response_tokens = count_llm_tokens(explanation_benign)

        # -------------------------
        # Judge
        # -------------------------
        prompt_judge = build_consensus_prompt(
            observable,
            explanation_attack,
            explanation_benign,
            ipqs_fraud_score,
            vt_malicious_count,
            abuse_score,
            use_context=use_augmentation
        )

        start_time = time.perf_counter()
        final_decision = llm.explain(prompt_judge)
        end_time = time.perf_counter()

        latency_judge = end_time - start_time

        decision_llm_likelihood = extract_llm_likelihood(final_decision)
        decision_llm_response_length = len(final_decision)
        decision_llm_response_tokens = count_llm_tokens(final_decision)

        # -------------------------
        # Total LLM metrics
        # -------------------------
        total_llm_latency_seconds = (
            latency_attack +
            latency_benign +
            latency_judge
        )

        total_llm_response_length = (
            malicious_llm_response_length +
            benign_llm_response_length +
            decision_llm_response_length
        )

        total_llm_response_tokens = (
            malicious_llm_response_tokens +
            benign_llm_response_tokens +
            decision_llm_response_tokens
        )

        # -------------------------
        # Write MD
        # -------------------------
        explanation_text = f"""
## Expert A – Attack Hypothesis
{explanation_attack}

## Expert B – Benign Hypothesis
{explanation_benign}

## Consensus Decision
{final_decision}
"""

        if use_augmentation:
            write_flow_md(
                flow_id=observable.get("ID", idx),
                features=observable,
                explanation=explanation_text,
                output_dir=run_output_dir,
                ipqs_fraud_score=ipqs_fraud_score,
                vt_malicious_count=vt_malicious_count,
                abuse_score=abuse_score
            )
        else:
            write_flow_md(
                flow_id=observable.get("ID", idx),
                features=observable,
                explanation=explanation_text,
                output_dir=run_output_dir
            )

        # -------------------------
        # Build result object
        # -------------------------
        result = {
            "flow_index": idx,
            "timestamp": datetime.now().isoformat(),
            "layer": "consensus",
            "model": llm.__class__.__name__,

            "use_augmentation": use_augmentation,
            "reputation_mode": reputation_mode
        }

        if use_augmentation:
            result["ipqs_fraud_score"] = ipqs_fraud_score
            result["vt_malicious_count"] = vt_malicious_count
            result["abuse_score"] = abuse_score
            result["ip_reputation_found"] = ip_reputation_found

        result.update({

            "autoencoder_score": autoencoder_score,

            "latency_attack": round(latency_attack, 3),
            "latency_benign": round(latency_benign, 3),
            "latency_judge": round(latency_judge, 3),

            "total_llm_latency_seconds": round(total_llm_latency_seconds, 3),
            "total_llm_response_length": total_llm_response_length,
            "total_llm_response_tokens": total_llm_response_tokens,

            "observable_features": observable,

            "malicious_llm_likelihood": malicious_llm_likelihood,
            "malicious_llm_response_length": malicious_llm_response_length,
            "malicious_llm_response_tokens": malicious_llm_response_tokens,

            "benign_llm_likelihood": benign_llm_likelihood,
            "benign_llm_response_length": benign_llm_response_length,
            "benign_llm_response_tokens": benign_llm_response_tokens,

            "decision_llm_likelihood": decision_llm_likelihood,
            "decision_llm_response_length": decision_llm_response_length,
            "decision_llm_response_tokens": decision_llm_response_tokens,

            "expert_attack": explanation_attack,
            "expert_benign": explanation_benign,
            "final_decision": final_decision
        })

        results.append(result)

    return results
