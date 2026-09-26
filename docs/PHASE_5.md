# Phase 5 — Property reconciliation

Date: 2026-09-26

## Outcome

A deterministic engine compares submitted property records with registered demo
geometry. It runs three explainable checks:

1. undivided shares total 100%;
2. declared carpet area is within 5% of mapped area;
3. a volume has no more than one active exclusive ownership claim.

The synthetic data deliberately contains a 103% share total, a 20% area mismatch
for Unit 401, and two active deed claims for Unit 302.

## Build and run

```bash
python3 scripts/build_demo.py
python3 scripts/reconcile_demo.py
python3 -m http.server 8000
```

Open 
.


## Scope

The output is a risk/consistency report for authorized human review. It is not a
fraud judgment, title decision, or substitute for examining source documents.

