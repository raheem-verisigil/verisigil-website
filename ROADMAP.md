# VeriSigil AI — Engineering Roadmap

## Strategic position

**Architecture:** Verifiable Consequence Boundaries  
**Capability:** Cryptographic Consequence Enforcement  
**Runtime:** Runtime Authority  
**Evidence:** Cryptographic Execution Receipts  
**Current phase:** PROVE

The architecture and terminology remain frozen during this phase. Work is directed at proving and strengthening the existing execution-boundary invariant, not adding unrelated product categories.

## Phase 1 — PROVE · Current

**Objective:** establish independently reproducible evidence for the declared protected execution boundary.

Engineering gates:
1. Exercise receipt creation, retrieval and one-time consumption through the deployed staging API and Supabase REST—not only direct SQL and mocked tests.
2. Prove receipt recovery after an independent process restart.
3. Prove that simultaneous consume attempts through two independent API instances produce exactly one successful consumption.
4. Establish durable persistence and freshness for authority/state registries, or explicitly exclude them from the current claim.
5. Run focused security tests and the complete unit suite on the exact evaluation commit; retain raw CI output.
6. Close the Temporal Standing gap by re-deriving live authority at the point of execution and testing both preserving and defeating changes.
7. Integrate a controlled downstream actuator with an independently observable side effect before claiming actuator enforcement.

Historical 9/9 composed-proof and 11/11 STILL results remain attributable to their original reference build and conditions. They are not substitutes for the current staging gates above.

**Success condition:** the current declared execution boundary has reproducible, commit-linked evidence, explicit exclusions and independently reviewable results.

## Phase 2 — GENERALIZE · After proof closure

**Objective:** determine whether the same invariant survives materially different consequence surfaces.

Candidate validation classes:
- financial action;
- privileged database mutation;
- production deployment;
- sensitive-data export;
- external filing;
- delegated agent-to-agent action.

These are future validation targets, not claims of current production coverage.

**Success condition:** direct-bypass and independent-verification tests demonstrate the same invariant across multiple materially different actuator classes.

## Phase 3 — INTEROPERATE · After generalization

**Objective:** make the enforcement contract portable across independent AI runtimes, identity systems, policy systems, protected resources and enterprise execution environments.

Adapters are accepted only when their behavior is tested against the same invariant and evidence contract.

## Phase 4 — STANDARDIZE · After interoperability

**Objective:** publish a stable, versioned execution-boundary contract with conformance tests and independently reproducible reference implementations.

No standardization or certification claim is made before this phase is achieved.

## Change-control rule

A new feature does not enter the core architecture merely because a reviewer requests it. It must strengthen the declared invariant, close an evidenced gap, or be required for a validated integration. Every material claim must remain tied to a reproducible artifact, commit, environment and test result.

