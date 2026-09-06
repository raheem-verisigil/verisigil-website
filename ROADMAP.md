# VeriSigil AI — Roadmap

## Current strategic position

**Architecture:** Verifiable Consequence Boundaries  
**Capability:** Cryptographic Consequence Enforcement  
**Runtime:** Runtime Authority  
**Evidence:** Cryptographic Execution Receipts

The architecture and terminology are currently frozen. The roadmap therefore does **not** add new product categories or a long feature catalogue. The immediate objective is to prove the existing invariant rigorously enough to justify generalization.

---

## Phase 1 — PROVE · Current

**Objective:** establish independently reproducible evidence at the declared consequence boundary.

- Complete the remaining independent delegation confirmation.
- Preserve the 9/9 composed proof result and 11/11 STILL result where conditions remain identical.
- Maintain fail-closed behavior and structured refusal evidence.
- Maintain receipt integrity, tamper detection, and offline verification.
- Document the exact payment-path limitation: boundary enforcement is demonstrated; a real Paystack transaction reference is not proven.
- Publish a dated proof report with exact conditions, scenarios, attacks, independent verification, exclusions, and claim ceiling.
- Keep `PRODUCTION_CLAIM_ALLOWED=False` until evidence warrants a change.

**Success condition:** the current material claim boundaries are independently reproducible and the remaining limitations are explicit.

---

## Phase 2 — GENERALIZE · After proof closure

**Objective:** determine whether the same invariant survives materially different consequence surfaces.

Reference validation classes:

1. financial action;
2. privileged database mutation;
3. production deployment;
4. sensitive-data export;
5. external or government filing;
6. delegated agent-to-agent action.

These are validation targets, not current claims of production coverage.

**Success condition:** the same enforcement invariant is demonstrated across multiple materially different actuator classes, including direct-bypass testing and independent evidence verification.

---

## Phase 3 — INTEROPERATE · After generalization

**Objective:** make the enforcement contract portable across independent environments.

Validate integration with different combinations of:

- AI / agent runtimes;
- identity systems;
- policy systems;
- protected resources / actuators;
- cloud and enterprise execution environments.

The test is not whether VeriSigil can replace these systems. The test is whether VeriSigil can sit at the consequential boundary while preserving the invariant.

**Success condition:** provider-neutral interoperability is demonstrated rather than asserted.

---

## Phase 4 — STANDARDIZE · Evidence-led

Only after interoperability evidence exists should the project consider formalizing a stable external enforcement/evidence contract, reference implementations, conformance vectors, or broader ecosystem adoption.

No standards claim is made today.

**Success condition:** independent implementations can reproduce the required boundary behavior and verify the resulting evidence.

---

## Phase 5 — INFRASTRUCTURE · Long term

If the invariant proves portable, interoperable, and independently verifiable, VeriSigil can evolve from a reference implementation into infrastructure used across consequential AI execution environments.

The intended progression is:

**BUILD → PROVE → GENERALIZE → INTEROPERATE → STANDARDIZE → BECOME INFRASTRUCTURE**

This is a strategic direction, not a current market or coverage claim.

---

## Explicit non-goals

This roadmap does not commit the project to becoming:

- a universal AI governance suite;
- a replacement for IAM, policy engines, enterprise security, or model safety;
- a universal agent gateway;
- a regulatory certification platform;
- a dashboard-first governance product;
- a feature-count competition;
- a system claiming every AI action is currently protected.

Evidence before expansion. Reproduction before trust.
