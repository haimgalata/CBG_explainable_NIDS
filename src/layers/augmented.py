import time
from datetime import datetime

from src.prompt_builder import extract_observable_features, build_augmented_prompt, extract_llm_likelihood, count_llm_tokens
from src.clients.gpt_client import GPTClient
from src.clients.gemini_client import GeminiClient
from src.services.ipqualityscore_service import IPQSASNScoreService
from src.services.virustotal_service import VirusTotalService
from src.services.abuseipdb_service import AbuseIPDBService
from src.services.synthetic_reputation import generate_random_attack_profile
from src.config import IPQS_API_KEY, VT_API_KEY, ABUSE_IPDB_API_KEY
from src.md_writer import write_flow_md


def run_augmented_layer(rows, run_output_dir, reputation_mode):
    #llm = GeminiClient()
    llm = GPTClient()

    # External services only exist here
    ipqs_service = IPQSASNScoreService(api_key=IPQS_API_KEY)
    vt_service = VirusTotalService(api_key=VT_API_KEY)
    abuse_service = AbuseIPDBService(api_key=ABUSE_IPDB_API_KEY)

    results = []

    for idx, row in enumerate(rows, start=1):
        observable = extract_observable_features(row)

        dst_ip = row["IP_DST_ADDR"]


        # ---- External enrichment ----
        if reputation_mode == "real":

            ipqs_fraud_score = ipqs_service.get_fraud_score(dst_ip)
            vt_malicious_count = vt_service.get_malicious_count(dst_ip)
            abuse_score = abuse_service.get_abuse_score(dst_ip)

            if any([
                ipqs_fraud_score,
                vt_malicious_count,
                abuse_score
            ]):
                ip_reputation_found = 1
            else:
                ip_reputation_found = 0


        elif reputation_mode == "synthetic":

            profile = generate_random_attack_profile()

            abuse_score = profile["abuse_score"]
            vt_malicious_count = profile["vt_malicious_count"]
            ipqs_fraud_score = profile["ipqs_fraud_score"]

            ip_reputation_found = 1


        elif reputation_mode == "default":

            # clean reputation (no API calls)
            ipqs_fraud_score = 0
            vt_malicious_count = 0
            abuse_score = 0

            ip_reputation_found = 0

        # ---- Build enriched prompt ----
        prompt = build_augmented_prompt(
            observable,
            ipqs_fraud_score=ipqs_fraud_score,
            vt_malicious_count=vt_malicious_count,
            abuse_score=abuse_score
        )

        start_time = time.perf_counter()
        explanation = llm.explain(prompt)
        end_time = time.perf_counter()

        latency = end_time - start_time

        llm_likelihood = extract_llm_likelihood(explanation)
        llm_response_length = len(explanation)
        llm_response_tokens = count_llm_tokens(explanation)
        autoencoder_score = observable.get("score_Autoencoder")

        write_flow_md(
            flow_id=observable.get("ID", idx),
            features=observable,
            explanation=explanation,
            output_dir=run_output_dir,
            ipqs_fraud_score=ipqs_fraud_score,
            vt_malicious_count=vt_malicious_count,
            abuse_score=abuse_score
        )

        results.append({
            "flow_index": idx,
            "timestamp": datetime.now().isoformat(),
            "layer": "augmented",
            "model": llm.__class__.__name__,
            "llm_latency_seconds": round(latency, 3),
            "observable_features": observable,
            "reputation_mode": reputation_mode,
            "ipqs_fraud_score": ipqs_fraud_score,
            "vt_malicious_count": vt_malicious_count,
            "abuse_score": abuse_score,
            "ip_reputation_found": ip_reputation_found,
            "autoencoder_score": autoencoder_score,
            "llm_likelihood": llm_likelihood,
            "llm_response_length": llm_response_length,
            "llm_response_tokens": llm_response_tokens,
            "explanation": explanation
        })

    return results
