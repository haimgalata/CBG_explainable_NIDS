# CBG Explainable NIDS

Explainable Network Intrusion Detection using LLM-based reasoning.

Pipeline:

Baseline → Augmented → Consensus

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

# Run

## Baseline

```
python -m src.run_explanations --layer baseline --start 0 --end 5
```

---

## Augmented

### Real reputation

```
python -m src.run_explanations --layer augmented --mode real --start 0 --end 5
```

### Synthetic reputation

```
python -m src.run_explanations --layer augmented --mode synthetic --start 0 --end 5
```

### Default reputation (all CTI values = 0)

```
python -m src.run_explanations --layer augmented --mode default --start 0 --end 5
```

---

# Consensus

### Consensus from baseline runs

```
python -m src.run_explanations --layer consensus --start 0 --end 5
```

### Consensus from augmented runs (real CTI)

```
python -m src.run_explanations --layer consensus --consensus_augmented --mode real --start 0 --end 5
```

### Consensus from augmented runs (synthetic CTI)

```
python -m src.run_explanations --layer consensus --consensus_augmented --mode synthetic --start 0 --end 5
```

### Consensus from augmented runs (default CTI)

```
python -m src.run_explanations --layer consensus --consensus_augmented --mode default --start 0 --end 5
```

---

# Parameters

```
--layer  baseline | augmented | consensus
         default: baseline

--start  start index (inclusive)
         default: 0

--end    end index (exclusive)
         default: until dataset end

--mode   real | synthetic | default
         default: real (augmented layer only)
```

---

# Output

```
outputs/runs/<RUN_ID>_<layer>_<mode>/
```

Each run contains:

```
results.json
md/   (per-flow explanations)
```

---

# Future Work

- [ ] Create evaluation CSV (ID, Actual_Label, LLM_Prediction, Label, IP_Reputation_Found, Latency, Tokens, Length)
- [ ] Run two experiments per flow: synthetic CTI and default CTI (all zeros)
- [ ] Review DDoS article and update synthetic CTI generation logic

---

CBG Internship – Explainable NIDS