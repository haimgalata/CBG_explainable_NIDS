import time
from datetime import datetime
from src.prompt_builder import extract_observable_features, build_basic_prompt
from src.clients.gpt_client import GPTClient
from src.clients.gemini_client import GeminiClient
from src.md_writer import write_flow_md
from src.utils.llm_utils import extract_llm_likelihood, count_llm_tokens

def run_baseline_layer(rows, run_output_dir):
    #llm = GeminiClient()
    llm = GPTClient()

    results = []

    for idx, row in enumerate(rows, start=1):
        observable = extract_observable_features(row)

        prompt = build_basic_prompt(observable)

        start_time = time.perf_counter()
        explanation = llm.explain(prompt)
        end_time = time.perf_counter()

        latency = end_time - start_time

        llm_likelihood = extract_llm_likelihood(explanation)
        llm_response_length = len(explanation)
        llm_response_tokens = count_llm_tokens(explanation)

        write_flow_md(
            flow_id=observable["ID"],
            features=observable,
            explanation=explanation,
            output_dir=run_output_dir,
        )

        results.append({
            "flow_index": idx,
            "timestamp": datetime.now().isoformat(),
            "layer": "baseline",
            "model": llm.__class__.__name__,
            "llm_latency_seconds": round(latency, 3),
            "observable_features": observable,
            "llm_likelihood": llm_likelihood,
            "llm_response_length": llm_response_length,
            "llm_response_tokens": llm_response_tokens,
            "explanation": explanation
        })

    return results
