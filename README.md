# CBG Explainable NIDS

Explainable Network Intrusion Detection using LLM reasoning.

---

## Layers

- **baseline** – NetFlow features only  
- **augmented** – NetFlow + IP reputation (IPQualityScore, VirusTotal, AbuseIPDB)  
- **consensus** – Aggregated explanation from multiple LLM runs

---

## Activate Environment

```
.venv\Scripts\activate
```

---

## Run

### Baseline

```
python -m src.run_explanations --layer baseline --start 0 --end 5
```

### Augmented (real reputation)

```
python -m src.run_explanations --layer augmented --mode real --start 0 --end 5
```

### Augmented (synthetic reputation)

```
python -m src.run_explanations --layer augmented --mode synthetic --start 0 --end 5
```

### Augmented (default reputation)

```
python -m src.run_explanations --layer augmented --mode default --start 0 --end 5
```
### Consensus


#### Parameters

```
--layer  baseline | augmented | consensus
         default: baseline

--start  start index (inclusive)
         default: 0

--end    end index (exclusive)
         default: process until dataset end

--mode   real | synthetic
         default: real (augmented layer only)
```

Example:

```
python -m src.run_explanations --layer consensus --mode synthetic --start 0 --end 5

python -m src.run_explanations --layer consensus --consensus_augmented --mode real --start 0 --end 1 

python -m src.run_explanations --layer consensus --consensus_augmented --mode synsynthetic  --start 0 --end 1

python -m src.run_explanations --layer consensus --consensus_augmented --mode defulte  --start 0 --end 1     
```

---

## Output

```
outputs/runs/<RUN_ID>_<layer>_<mode>/
```

Contains:

```
results.json
md/   (per-flow explanations)
```

---

CBG Internship – Explainable NIDS