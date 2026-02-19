# CBG Explainable NIDS

Explainable Network Intrusion Detection using LLM-based reasoning.

The system supports two layers:

1. Basic – Uses raw NetFlow features only.
2. Enriched – Uses NetFlow features + IP reputation signals (IPQualityScore, VirusTotal).

------------------------------------------------------------

## Run

Activate environment:

.venv\Scripts\activate

Run Basic layer:

python -m src.run_explanations --layer basic --start 0 --end 5

Run Enriched layer:

python -m src.run_explanations --layer enriched --start 0 --end 5

------------------------------------------------------------

## Parameters

--layer   basic | enriched  
--start   start index  
--end     end index (exclusive)

Example:

python -m src.run_explanations --layer enriched --start 100 --end 120

------------------------------------------------------------

## Output

Each run creates:

outputs/runs/<RUN_ID>_<layer>/

Containing:
- results.json
- md/ (per-flow explanations)

------------------------------------------------------------

CBG Internship – Explainable NIDS
