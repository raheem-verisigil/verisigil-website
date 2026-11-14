# VeriSigil AI — Verifiable Consequence Boundaries

**Runtime control and evidence for consequential AI actions at declared execution boundaries.**

VeriSigil is being developed to answer a precise systems question: when an AI-driven action is about to change an external system, can the protected workflow re-establish authority and required conditions, bind the decision to the exact action and parameters, refuse when required evidence is missing or contradictory, and produce independently checkable evidence?

The architecture is intentionally bounded. VeriSigil complements identity, IAM, policy, model-safety, human-governance and actuator systems; it does not replace them.

## Current product architecture

- **Verifiable Consequence Boundaries** — the declared point where a consequential action is evaluated and controlled.
- **Runtime Authority** — current authority and required conditions are checked for the action about to execute.
- **Parameter-Locked Execution** — the decision is bound to the exact action and parameters.
- **Fail-Closed Runtime** — inability to establish a required condition does not become implicit permission.
- **Cryptographic Execution Receipts** — signed evidence supports independent verification of the recorded decision.

The architectural direction is frozen during the current proof-closure phase. The immediate work is to strengthen the existing invariant, not add unrelated product layers.

## Current phase: PROVE

The current evaluation candidate is the isolated staging branch of the API repository. It includes a Supabase-backed validation-receipt adapter and fail-closed execution-authorization middleware.

**Important:** the current Terry adversarial test substitutes an in-memory fake receipt store. The database schema and atomic consume function have been inspected, and an operator-reported rollback SQL smoke test showed first consume succeeds and second consume returns no record. The deployed API's complete Supabase insert/read/consume path has not yet been independently verified.

Other current limitations:
- Authority and state registries remain in-memory in the staging harness.
- Process-restart recovery and cross-instance replay behavior are not yet proven.
- Downstream actuator enforcement and real payment execution are not proven.
- The current signing path uses Ed25519; post-quantum signing is not claimed.
- Current Z3 proof execution is not claimed.
- No production-wide coverage, universal AI safety, regulatory certification or legal compliance claim is made.

## Historical reference evidence

Earlier reference-environment work reported an 11/11 STILL adversarial result, receipt integrity/offline verification, tamper detection and parameter binding on tested paths. Those results are historical evidence for their own build and conditions. They must not be treated as proof that the current Terry staging candidate has passed live Supabase integration, restart recovery, multi-instance concurrency or downstream actuator tests.

## Authoritative current evidence

The controlling status, exact evaluation commit, test boundaries and remaining proof gates are maintained in the [API repository's Current Evidence Baseline](https://github.com/raheem-verisigil/verisigil-api/blob/main/EVIDENCE_BASELINE.md).

- [Current bounded evaluation branch](https://github.com/raheem-verisigil/verisigil-api/tree/security/terry-fail-closed-execution-20261113)
- [Current staging commit](https://github.com/raheem-verisigil/verisigil-api/commit/5a26584360ad4abca503a625f9cd74e1b9abe652)
- [Bounded challenge protocol](https://github.com/raheem-verisigil/verisigil-api/blob/main/CHALLENGE.md)
- [Safe local reproduction guide](https://github.com/raheem-verisigil/verisigil-api/blob/main/QUICKSTART.md)

## Evidence rules

Implemented code is not automatically tested behavior. A test definition is not a passing test. A successful deployment is not a security result. A valid cryptographic signature proves integrity relative to a trusted key; it does not prove source-data truth, legal compliance, or downstream enforcement.

**BUILD → PROVE → GENERALIZE → INTEROPERATE → STANDARDIZE**

