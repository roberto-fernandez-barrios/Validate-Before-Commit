# Paper 2 long-stream downstream validation checkpoint 001

## Protocol

- post_windows: 100
- severities: 0.75, 1.0
- seeds: final seed directories found in `results/raw/paper2_downstream_long_stream_final_001_seed_*`
- trigger policy: q=0.95, k=3

## Generated artifacts

- `results\raw\paper2_downstream_long_stream_final_001\paper2_downstream_long_stream_final_by_seed.csv`
- `results\raw\paper2_downstream_long_stream_final_001\paper2_downstream_long_stream_final_summary.csv`
- `results\tables\paper2_downstream_long_stream_final_001\paper_table_long_stream_summary_compact.csv`
- `results\tables\paper2_downstream_long_stream_final_001\paper_table_long_stream_qk_vs_mmd_paired.csv`

## Interpretation guideline

This experiment tests whether a longer downstream stream makes the QK-MMD
monitoring advantage translate into direct downstream performance gains.

If MMD-RBF and QK-MMD trigger at the same window, downstream metrics will
be nearly identical because all methods use the same retraining mechanism.

In that case, the operational QK-MMD claim should remain focused on
post-drift monitoring coverage rather than final retrained accuracy.
