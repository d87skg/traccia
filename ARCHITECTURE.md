# OpenBase Architecture

OpenBase is a protocol, not a framework. This document defines what belongs where — and why.

---

## Core Protocol (Immutable)

The OpenBase Protocol defines the minimum interoperable layer for AI agent execution evidence.

| Component | Purpose | Status |
|-----------|---------|--------|
| **OBS** | OpenBase Schema — canonical event vocabulary | Stable |
| **Evidence** | Structured, verifiable execution trace (`.evidence`) | Stable |
| **Replay** | Convert Evidence to human-readable timeline | Stable |
| **Conformance** | Certification engine — verify agent claims | Stable |

**Rule:** No new component enters Core without a 12-month stabilization period in Extensions first.

---

## SDK Layer: Traccia

Traccia is the official developer SDK for OpenBase. It translates agent execution into OpenBase Evidence.

| Component | Purpose | Status |
|-----------|---------|--------|
| `traccia intercept` | Auto-generate Evidence from any Python agent | Active |
| `traccia diagnose` | Analyze Evidence and output root cause report | Active |
| `traccia guard` | Security policy gateway between agent and tools | Active |
| Session | Agent lifecycle boundary | SDK layer |
| Attribution Chain | Actor responsibility tracking | SDK layer |
| Evidence Package | Bundled execution trace (ZIP) | SDK layer |
| Renderer | Convert Evidence to Markdown/JSON/Text | SDK layer |

**One-sentence definition:** Traccia adds verifiable execution, replay, and evidence to any AI agent in minutes.

---

## Reference Runtime: OpenClaw

OpenClaw is a reference agent runtime that produces OpenBase Evidence natively.

---

## Enterprise Extensions

| Extension | Purpose | Status |
|-----------|---------|--------|
| **Guard** | Security policy enforcement | Active |
| **Audit** | Enterprise compliance reporting | Planned |
| **Risk** | Agent risk scoring | Planned |
| **Compliance** | Regulatory framework mapping | Planned |
| **Governance** | Multi-party approval workflows | Planned |

---

## Experimental Extensions

| Extension | Purpose | Status |
|-----------|---------|--------|
| **Residual Engine** | 4D execution quality scoring | Experimental |
| **Entropy Injection** | Controlled adversarial testing | Experimental |
| **Loop** | Closed-loop feedback training | Experimental |
| **Registry** | Global evidence discovery | Experimental (local-only) |
| **Rust Core** | High-performance runtime | Experimental (traccia-rs/) |

These are preserved for future activation when ecosystem scale demands them.

---

## Archived Concepts

| Concept | Why Archived |
|---------|-------------|
| **AES** | Absorbed into Attribution Chain |
| **AEF** | Absorbed into Evidence Package |
| **Aegis** | Renamed to OpenBase |

---

## Design Principles

1. **Core is minimal.** Only what is required for interoperability.
2. **SDK is the entry point.** Nobody should need to read the protocol to get started.
3. **Extensions prove themselves before entering Core.** 12-month stabilization minimum.
4. **One protocol, many SDKs.** Traccia is Python; future SDKs may be Rust, TypeScript, Go.
5. **Freeze early, evolve slowly.** Core changes are additive only.
