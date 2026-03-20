# CBG Explainable NIDS

Explainable Network Intrusion Detection using LLM-based reasoning.

Pipeline:

Baseline → Augmented → Consensus

---

## Layers

- **baseline** – NetFlow features only  
- **augmented** – NetFlow + external context (IP reputation + Autoencoder score)  
- **consensus** – Expert debate + judge decision

---

## Activate Environment

```bash
.venv\Scripts\activate
```

---

## Run

If no row range is provided, the system runs on the default flow **(row 397)**.

---

## Baseline

```bash
python -m src.run_explanations --layer baseline
```

Specific row:

```bash
python -m src.run_explanations --layer baseline --start 260 --end 261
```

---

## Augmented

Default mode (CTI values = 0)

```bash
python -m src.run_explanations --layer augmented
```

Real CTI

```bash
python -m src.run_explanations --layer augmented --mode real
```

Synthetic CTI

```bash
python -m src.run_explanations --layer augmented --mode synthetic
```

Specific row

```bash
python -m src.run_explanations --layer augmented --start 260 --end 261
```

---

## Consensus

Consensus from baseline experts

```bash
python -m src.run_explanations --layer consensus
```

Consensus with augmented context (CTI = 0)

```bash
python -m src.run_explanations --layer consensus --consensus_mode augmented
```

Consensus with real CTI

```bash
python -m src.run_explanations --layer consensus --consensus_mode augmented --mode real
```

Consensus with synthetic CTI

```bash
python -m src.run_explanations --layer consensus --consensus_mode augmented --mode synthetic
```

Specific row

```bash
python -m src.run_explanations --layer consensus --start 260 --end 261
```

---

## Parameters

```
--layer
baseline | augmented | consensus
(required)

--consensus_mode
baseline | augmented
(default: baseline)

--mode
real | synthetic | default
(default: default)

--start
start index in dataset
(default: 397)

--end
end index (exclusive)
(default: 398)
```

---

## Output

```
outputs/runs/<RUN_ID>_<layer>/
```

Each run contains:

```
results.json
md/   (per-flow explanations)
```

---
---

## 🔧 TODO / Future Work

### 🧠 Synthetic CTI Improvements
- [ ] Improve synthetic CTI realism by introducing multiple intelligence scenarios:
  - **Full CTI coverage** – signals available across all services (IPQS, VirusTotal, AbuseIPDB)
  - **Partial CTI coverage** – signals available only from some services (others return 0)
  - **No CTI available** – simulate missing intelligence / false negatives

### 📊 Evaluation & Outputs
- [x] Create evaluation CSV  
  *(ID, Actual_Label, LLM_Prediction, Label, IP_Reputation_Found, Latency, Tokens, Length, LLM_Explanation)*

### 🔗 Pipeline Integration
- [ ] Connect the explanation pipeline to the anomaly detection stage  
  *(NetFlow / Autoencoder pipeline)*

---

CBG Internship – Explainable NIDS
