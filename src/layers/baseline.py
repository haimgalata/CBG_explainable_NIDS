import time
from datetime import datetime

from src.prompt_builder import extract_observable_features, build_basic_prompt
from src.clients.gpt_client import GPTClient
from src.md_writer import write_flow_md


def run_basic_layer(rows, run_output_dir):
    llm = GPTClient()
    results = []

    for idx, row in enumerate(rows, start=1):
        observable = extract_observable_features(row)

        prompt = build_basic_prompt(observable)

        start_time = time.perf_counter()
        explanation = llm.explain(prompt)
        end_time = time.perf_counter()

        latency = end_time - start_time

        write_flow_md(
            flow_id=observable["ID"],
            features=observable,
            explanation=explanation,
            output_dir=run_output_dir,
        )

        results.append({
            "flow_index": idx,
            "timestamp": datetime.now().isoformat(),
            "layer": "basic",
            "model": llm.__class__.__name__,
            "llm_latency_seconds": round(latency, 3),
            "observable_features": observable,
            "explanation": explanation
        })

    return results
