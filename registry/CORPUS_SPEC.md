# Traccia Evidence Corpus Specification v0.1

## Purpose
A public, anonymized collection of AI agent execution traces (.evidence files) for research, evaluation, and training.

## Structure
- Each evidence package is stored as a .evidence zip file.
- Metadata is recorded in entries.jsonl.
- Files are stored in corpus/ directory with UUID filenames.

## Upload Rules
- Evidence package must pass 	raccia verify.
- No personally identifiable information (PII) is collected.
- Session objectives are stored as-is but can be anonymized by the contributor.

## URI Scheme
evidence://<sha256_prefix> uniquely identifies each package.

## Contribution
Use POST /api/upload with raw .evidence binary, or run python upload.py <file>.
