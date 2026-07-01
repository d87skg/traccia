Traccia Architecture
AI Execution Truth Architecture
An open protocol for verifiable AI execution.

Version: 1.0
Status: Frozen (Architecture boundaries are stable; Protocol may evolve within the defined layers)

1. Architecture Overview
Traccia is not a monolithic tool. It is a layered architecture with clear separation of concerns. Every component belongs to exactly one of six domains.

text
                    ┌──────────────────────────────┐
                    │        AI Application          │
                    └──────────────┬─────────────────┘
                                   │
                    ┌──────────────▼─────────────────┐
                    │        Agent Runtime            │
                    │  (OpenClaw, LangGraph, CrewAI)  │
                    └──────────────┬─────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐       ┌──────────────────┐       ┌──────────────────┐
│    Emitter    │       │   Middleware      │       │    Recorder       │
│               │       │                   │       │                    │
│ • LangChain   │──────▶│ • Guard           │──────▶│ • Event Builder    │
│ • OpenClaw    │       │ • Validator       │       │ • Evidence Builder │
│ • CLI         │       │ • Replay          │       │ • HashChain        │
└───────────────┘       └──────────────────┘       └────────┬─────────┘
                                                             │
                                              ┌──────────────▼──────────────┐
                                              │          Protocol            │
                                              │                              │
                                              │ • Session / Event / Evidence │
                                              │ • Attribution / Package      │
                                              │ • .evidence JSON Schema      │
                                              └──────────────┬──────────────┘
                                                             │
                                      ┌──────────────────────┼──────────────────────┐
                                      │                      │                      │
                                      ▼                      ▼                      ▼
                              ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
                              │   Registry    │       │     Eval      │       │  Consumers    │
                              │               │       │               │       │               │
                              │ • evidence:// │       │ • Scorer      │       │ • Viewer      │
                              │ • Discovery   │       │ • Benchmark   │       │ • Auditor     │
                              └──────────────┘       └──────────────┘       └──────────────┘
The architecture is strictly layered. Components never skip a layer or import upward.

2. Layer Definitions
Each layer has exactly one responsibility and a strictly defined interface.

2.1 Protocol Layer
Responsibility: Define how facts are expressed.
Artifacts: JSON Schema (.evidence), HashChain specification, Attribution model.
Stability: This layer is the most stable. Changes are additive only (e.g., adding new optional fields).
Dependencies: None. It is the root of the dependency graph.
Consumers: Every other layer reads or writes Protocol objects.

2.2 Recorder Layer
Responsibility: Translate runtime events into Protocol objects.
Key Interface:

python
class Recorder(ABC):
    @abstractmethod
    def observe_llm(self, prompt: str, response: str, metadata: dict): ...
    @abstractmethod
    def observe_tool(self, tool_name: str, input: dict, output: dict, metadata: dict): ...
    @abstractmethod
    def observe_error(self, error: Exception, context: dict): ...
    # ... other observation methods
Rule: All Emitter implementations MUST write to a Recorder. No Emitter may construct Protocol objects directly.

2.3 Emitter Layer
Responsibility: Connect a specific Agent framework runtime to the Recorder.
Examples: LangChainEmitter, CrewAIEmitter, CLIEmitter.
Rule: An Emitter is a thin adapter. It Monkey-patches or hooks framework internals, captures execution events, and forwards them to the Recorder interface. It must contain zero domain logic.

2.4 Middleware Layer
Responsibility: Intercept, filter, or augment the event stream.
Key Interface:

python
class Middleware(ABC):
    @abstractmethod
    def process(self, event: Event) -> Tuple[Event, Action]:
        # Action: PASS, BLOCK, WARN, MODIFY
        ...
Examples: Guard (block dangerous commands), Validator (check HashChain), Replay (record timeline).
Rule: Middleware are composable. They can be chained: Guard -> Validator -> Recorder.

2.5 Registry Layer
Responsibility: Enable discovery, sharing, and permanent referencing of Evidence Packages.
Key Concept: Every package receives a unique, resolvable URI (e.g., evidence://<hash>).
Status: Deferred. Will be activated once there are real sharing needs in the ecosystem.

2.6 Eval Layer
Responsibility: Consume .evidence files and produce evaluation metrics.
Key Concept: Metrics are computed on execution graphs, not just final outputs.
Examples: traccia-eval scorer, analyzer.
Rule: Eval is a consumer only. It never influences the Protocol or Recorder.

3. Data Flow (Standard Path)
Agent Runtime executes a task (e.g., LangChain Agent).

An Emitter hooks the runtime and forwards raw events to the Recorder.

(Optionally) Middleware intercepts events (e.g., Guard blocks a dangerous command).

The Recorder translates events into Protocol objects (Session, Event, Evidence).

The Recorder builds the HashChain and exports an .evidence package.

The package can be registered in the Registry (future).

The package can be consumed by Eval tools or Viewers (Replay).

4. Design Principles
4.1 Freeze Architecture, Not Protocol
The six-layer architecture is frozen. Protocol versions (.evidence v1.x) may evolve, but they stay within the Protocol layer.

4.2 Concept Control
Before adding any new module, ask: Which layer does it belong to? If the answer is not clear, the module is not ready.

4.3 Inevitability over Persuasiveness
We don't ask frameworks to "support" Traccia. We make .evidence generation an unavoidable byproduct of execution. The Emitter/Recorder model achieves this via Monkey-patching and wrapper injection.

4.4 Composition over Configuration
Middleware and Emitters are designed to be composed. Adding a new safety check should not require modifying the core.

4.5 Zero-Config by Default
The goal for any Emitter is to work out of the box. pip install traccia-langchain should be enough.

5. Code Map (Current to Target)
Current Implementation	Target Layer	Status
traccia/reference/python/	Recorder	Needs refactoring to extract Recorder interface.
guard/	Middleware (Guard)	Needs to implement Middleware interface.
cli/traccia.py	Emitter (CLI Wrapper)	Correct. Will remain as a generic Emitter.
(New) emitters/langchain/	Emitter (LangChain)	Highest priority new component.
analyzer/	Eval	Move to Eval layer.
registry/	Registry	Deferred.
6. Roadmap (6-Month Horizon)
Q1: Stabilize Recorder interface. Release traccia-langchain Emitter. Activate community feedback loop.

Q2: Refactor Guard into Middleware. Release traccia-crewai Emitter. Begin OpenClaw native integration.

Q3: Launch traccia-eval benchmark and Leaderboard. Publish HuggingFace dataset.

Q4: Evaluate Registry activation based on ecosystem adoption. Open protocol spec for external RFCs.

"We do not build a tool. We define the truth layer for AI execution."