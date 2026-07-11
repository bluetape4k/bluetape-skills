# Self-Improve Harness

## Benchmark

- Command: TBD
- Result format/parser: TBD
- Primary metric path/unit/direction: TBD
- Baseline repetitions and environment: TBD
- Secondary guarded metrics: TBD
- Candidate timeout/resource limits: TBD

## Protected Inputs

- Trusted candidate base revision source: TBD
- Sealed files/directories: TBD
- Fixture reset/cache policy: TBD

## H001: One Hypothesis

Each candidate must test exactly one measurable hypothesis.

## H002: Benchmark Integrity

Candidates must not edit sealed benchmark files, benchmark fixtures, metric parsers, or baseline reports.

## H003: Regression Guard

Candidates must pass targeted tests before benchmark measurement and must not exceed the configured regression threshold.

## H004: History Awareness

Do not repeat failed approach families without new evidence.

## H005: Checkpoint Writes

Write state through a temporary file, parse it, then rename it. Preserve the
last valid checkpoint and raw benchmark evidence before candidate cleanup.
