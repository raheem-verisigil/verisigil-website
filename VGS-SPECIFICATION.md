# VeriSigil Governance Specification (VGS)
# Formal Infrastructure Standards for Autonomous AI Agent Governance
# Version 1.0 — May 2026
# Author: Raheem Larry Babatunde, VeriSigil AI
# verisigilai.com

---

## Abstract

This document defines the VeriSigil Governance Specification (VGS) — a formal infrastructure standard for governing autonomous AI agent execution. VGS defines the primitives required for deterministic, auditable, and forensically verifiable governance of AI agent actions at the execution boundary.

VGS addresses the gap identified independently by multiple governance infrastructure builders: the difference between governance as documentation and governance as execution enforcement.

---

## VGS-001: Runtime Admissibility Specification

### 1.1 Definition

An agent action is **admissible** if and only if:

1. The agent carries a valid cryptographic identity (passport)
2. The agent's trust score meets the minimum threshold for the consequence level
3. The action satisfies all applicable governance invariants
4. The operational conditions under which permissions were granted remain valid
5. No active alerts or regulatory changes have revoked the relevant permissions

### 1.2 Admissibility Evaluation

Admissibility is evaluated at the **execution boundary** — the moment before an action becomes real. It is not evaluated at:
- Model output generation time
- Workflow planning time
- Upstream authorization time

Upstream authorization is necessary but not sufficient. Admissibility must be confirmed at execution time.

### 1.3 Admissibility Decisions

Every admissibility evaluation returns one of three decisions:

```
ALLOW                   — Action admissible. Execute immediately.
DENY                    — Action inadmissible. Hard stop. No execution.
REQUIRE_HUMAN_APPROVAL  — Action requires human gate before execution.
```

### 1.4 Decision Determinism

The same inputs to the admissibility evaluation must always produce the same decision. Governance is not probabilistic. The admissibility function is deterministic and replay-verifiable.

### 1.5 Latency Requirement

Admissibility evaluation must complete in under 100ms to be deployable in production AI systems.

### 1.6 Endpoint

```
POST /v1/guard/verify
POST /v1/invariants/check
POST /v1/progression/evaluate
```

---

## VGS-002: Governance Transition Semantics

### 2.1 Definition

A **governance state transition** is a change in agent execution state from one defined governance state to another.

### 2.2 Defined States

```
UNVERIFIED   — Agent identity not verified
VERIFIED     — Identity verified, trust established
PROVISIONAL  — Trust in provisional range (0.65-0.80)
ADMISSIBLE   — Action admissible under current conditions
ESCALATED    — Awaiting human approval
EXECUTING    — Action executing under governance
COMPLETED    — Action completed, audit trail written
FAILED       — Action failed, requires human review
DENIED       — Action denied, hard stop
```

### 2.3 Permissible Transitions

```
UNVERIFIED  → VERIFIED | DENIED
VERIFIED    → ADMISSIBLE | PROVISIONAL | DENIED
PROVISIONAL → ADMISSIBLE | ESCALATED | DENIED
ADMISSIBLE  → EXECUTING | ESCALATED | DENIED
ESCALATED   → EXECUTING | DENIED
EXECUTING   → COMPLETED | FAILED
COMPLETED   → VERIFIED
FAILED      → ESCALATED | DENIED
DENIED      → (terminal)
```

### 2.4 Transition Preconditions

STATE_A → STATE_B is permissible only if:
- Authority is valid at transition time (not at planning time)
- All applicable invariants are satisfied
- Evidence requirements for the target state are met
- Operational conditions remain consistent with granted permissions

### 2.5 Endpoint

```
POST /v1/state/transition
GET  /v1/state/machine
```

---

## VGS-003: Human Approval Invariants

### 3.1 Mandatory Escalation Conditions

Human approval is **always required** for:

1. Any CRITICAL consequence action — no exceptions
2. Financial transfers exceeding $1,000 USD
3. Production deployments
4. Bulk delete operations (>100 records)
5. Any action where trust score is between 0.65 and 0.80
6. Any action where evidence completeness is below 70% for HIGH consequence

### 3.2 Approval Record Requirements

Every human approval must record:
- Approver identity (cryptographically verifiable)
- Timestamp of decision
- Decision (APPROVED / REJECTED)
- Confidence level presented to approver at time of decision
- Evidence completeness score at time of decision

### 3.3 Approval Expiry

Approvals expire after 24 hours. Expired approvals cannot authorize execution under any circumstances.

### 3.4 Friction Requirements

| Consequence Level | Minimum Review Period | Acknowledgments Required |
|-------------------|----------------------|--------------------------|
| MEDIUM | 0 seconds | 0 |
| HIGH | 3 seconds | 1 |
| CRITICAL | 10 seconds | 3 |

### 3.5 Endpoint

```
POST /v1/approvals/create
GET  /v1/approvals/{id}
POST /v1/approvals/{id}/decide
```

---

## VGS-004: Cryptographic Governance Receipt

### 4.1 Definition

A **governance receipt** is a cryptographically signed artifact produced at the execution boundary for every governance decision. It constitutes forensic evidence that governance was applied.

### 4.2 Receipt Schema

```json
{
  "receipt_version":    "VGS-004-1.0",
  "decision_id":        "exec_xxxxxxxx",
  "agent_id":           "vsa_xxxxxxxx",
  "action_type":        "payment",
  "decision":           "ALLOW | DENY | REQUIRE_HUMAN_APPROVAL",
  "state_hash":         "sha256:...",
  "authority_hash":     "sha256:...",
  "evidence_hash":      "sha256:...",
  "admissibility_score": 0.9400,
  "trust_score":        0.9630,
  "invariants_checked": 40,
  "invariants_violated": 0,
  "workflow_id":        "wf_xxxxxxxx",
  "timestamp":          "2026-05-17T00:00:00.000000",
  "schema":             "VGS-004",
  "verifiable":         true,
  "cross_jurisdiction": true,
  "signature":          "ed25519:..."
}
```

### 4.3 Receipt Properties

- **Deterministic**: Same inputs always produce same state_hash
- **Tamper-evident**: Any modification invalidates the signature
- **Cross-jurisdiction**: Verifiable without access to the live system
- **Replay-verifiable**: Receipt can be independently reconstructed from inputs
- **Chain-anchored**: Every receipt is anchored to the Merkle governance chain

### 4.4 EU AI Act Compliance

Receipt retention for minimum 6 months satisfies Article 12 and Article 19 of the EU AI Act.

### 4.5 Endpoint

```
POST /v1/governance/receipt
GET  /v1/chain/replay/{execution_id}
```

---

## VGS-005: Intent-Bound Execution Protocol

### 5.1 Definition

**Intent-bound execution** requires that every agent action be bound to a declared intent. Execution that deviates materially from declared intent is blocked or escalated.

### 5.2 Intent-Action Binding

An action is **intent-aligned** if:
- The action type is semantically consistent with the declared intent
- The action parameters do not exceed the scope implied by the declared intent
- The consequence level is proportionate to the stated purpose

### 5.3 Mismatch Detection

Intent-action mismatch is detected when:
- Action type involves financial transfer but declared intent contains no payment language
- Action type involves deletion but declared intent contains no removal language
- Action scope (amount, count, target) materially exceeds the declared intent scope

### 5.4 Mismatch Enforcement

| Consequence Level | Mismatch Response |
|-------------------|-------------------|
| LOW | WARNING — logged to audit trail |
| MEDIUM | REQUIRE_HUMAN_APPROVAL |
| HIGH | DENY — intent mismatch blocks execution |
| CRITICAL | DENY — always |

### 5.5 Endpoint

```
POST /v1/intent/bind
```

---

## Governance Invariant Registry

### Category I: Identity Invariants

| ID | Name | Statement | Violation |
|----|------|-----------|-----------|
| I-01 | Passport Required | No agent may execute any action without a valid cryptographic passport | DENY |
| I-02 | Signature Validity | Every passport must carry a valid Ed25519 signature | DENY |
| I-03 | Passport Expiry | No expired passport may authorize any action | DENY |
| I-04 | Revocation Hard Stop | A revoked passport immediately terminates all active permissions | DENY |
| I-05 | Shadow Clone Block | Identity conflict results in immediate block of both agents | DENY |
| I-06 | Trust Floor | Trust score below 0.50 results in immediate denial | DENY |
| I-07 | Authority Binding | Agent authority is bound to trust score at evaluation time | REQUIRE_HUMAN_APPROVAL |
| I-08 | Issuer Attribution | Every passport must carry verifiable issuer attribution | DENY |

### Category E: Execution Invariants

| ID | Name | Statement | Violation |
|----|------|-----------|-----------|
| E-01 | HIGH Consequence Gate | No HIGH consequence action without valid identity + authority + evidence | REQUIRE_HUMAN_APPROVAL |
| E-02 | CRITICAL Human Requirement | No CRITICAL consequence action without explicit human approval | REQUIRE_HUMAN_APPROVAL |
| E-03 | Payment Threshold | Transfers >$1,000 require approval. >$500,000 are denied | REQUIRE_HUMAN_APPROVAL |
| E-04 | Delete Irreversibility | All bulk delete operations require human approval | REQUIRE_HUMAN_APPROVAL |
| E-05 | Production Deploy Gate | Production deployments always require human approval | REQUIRE_HUMAN_APPROVAL |
| E-06 | Dangerous Tool Block | exec, eval, shell, subprocess are permanently blocked | DENY |
| E-07 | PII Access Control | PII access without GDPR certification is denied | DENY |
| E-08 | Approval Expiry | Expired approvals cannot authorize execution | DENY |
| E-09 | Chain Provenance Required | Multi-agent actions must carry verifiable chain provenance | DENY |
| E-10 | Authority Inheritance Limit | Delegated authority cannot exceed delegating agent's authority | DENY |

### Category A: Audit Invariants

| ID | Name | Statement | Violation |
|----|------|-----------|-----------|
| A-01 | Mandatory Chain Entry | Every governance decision must produce an immutable chain entry | DENY |
| A-02 | Signature Requirement | Every chain entry must carry a valid cryptographic signature | DENY |
| A-03 | Replay Determinism | Every governance decision must be deterministically replayable | CHAIN_INTEGRITY_FAILURE |
| A-04 | Tamper Evidence | Any chain modification must be detectable | CHAIN_INTEGRITY_FAILURE |
| A-05 | Retention Minimum | Chain entries retained minimum 6 months (EU AI Act Article 19) | COMPLIANCE_FAILURE |
| A-06 | Evidence Completeness | HIGH consequence decisions require complete evidence | REQUIRE_HUMAN_APPROVAL |
| A-07 | Approver Identity Record | Every human approval must record approver identity and timestamp | DENY |
| A-08 | Cross-Jurisdiction Receipt | Receipts must be verifiable without access to live system | COMPLIANCE_FAILURE |

### Category P: Progression Invariants

| ID | Name | Statement | Violation |
|----|------|-----------|-----------|
| P-01 | Trajectory Coherence | State transitions must be logically coherent | TRAJECTORY_ANOMALY |
| P-02 | Failed State Block | Progression from failed state requires human review | REQUIRE_HUMAN_REVIEW |
| P-03 | Consequence Binding Disclosure | Agents must be informed of binding point before irreversible transitions | REQUIRES_EVIDENCE |
| P-04 | Evidence Sufficiency Gate | HIGH consequence transitions require complete evidence | REQUIRES_EVIDENCE |
| P-05 | Authority Continuity | Authority must remain valid throughout the workflow | REQUIRES_AUTHORITY |
| P-06 | Condition Stability | Permissions revoked when conditions change materially | PERMISSIONS_REVOKED |
| P-07 | Loop Detection | Actions repeated >3 times without progression are anomalous | TRAJECTORY_ANOMALY |

### Category C: Cognitive Invariants

| ID | Name | Statement | Violation |
|----|------|-----------|-----------|
| C-01 | Uncertainty Disclosure | Confidence below 0.75 must disclose uncertainty to approvers | FRICTION_REQUIRED |
| C-02 | Evidence Completeness Display | Approvers must see evidence score before HIGH consequence approvals | FRICTION_REQUIRED |
| C-03 | CRITICAL Friction Minimum | CRITICAL approvals require 10s review and explicit acknowledgment | FRICTION_REQUIRED |
| C-04 | Adversarial Detection Block | Adversarial explanation risk >0.5 blocks standard approval | COMPREHENSION_BLOCKED |
| C-05 | Ambiguity Disclosure | All ambiguities must be disclosed to human approvers | FRICTION_REQUIRED |
| C-06 | Intent Corruption Block | Documents showing intent corruption are blocked from approval | DENY |
| C-07 | Document Integrity Gate | Documents with semantic integrity <0.70 cannot be approved for HIGH actions | DENY |

---

## Standardized Admissibility Schema

Every admissibility evaluation returns a schema-conformant response:

```json
{
  "schema":               "VGS-001",
  "decision":             "ALLOW | DENY | REQUIRE_HUMAN_APPROVAL",
  "admissibility": {
    "authority_valid":     true,
    "evidence_complete":   false,
    "consequence_level":   "HIGH",
    "transition_admissible": false,
    "invariants_satisfied": true,
    "conditions_stable":   true
  },
  "confidence":           0.9400,
  "trust_score":          0.9630,
  "authority_level":      "SOVEREIGN",
  "latency_ms":           42,
  "execution_id":         "exec_xxxxxxxx",
  "receipt":              { "VGS-004 receipt object" },
  "chain_block":          { "block_hash": "...", "tamper_evident": true }
}
```

---

## Relationship to ATF (Agent Trust Framework)

The VeriSigil Governance Specification and the ATF (Agent Trust Framework, RFC-ATF-1 through RFC-ATF-3 by Harold Alberto Nunes Rodelo, OMNIX QUANTUM) address the same missing infrastructure layer from complementary implementations.

| Primitive | ATF | VGS |
|-----------|-----|-----|
| Agent identity | Agent Identity Records (AIR) | Cryptographic Passport (Ed25519) |
| Post-quantum crypto | Dilithium-3 | Ed25519 (Dilithium-3 upgrade planned) |
| Execution gate | Adaptive Veto Machine | Runtime Guard + Progression Admissibility |
| Formal invariants | 40 published invariants | 40 governance invariants (VGS-001) |
| Forensic receipt | Immutable forensic receipt | Cryptographic Governance Receipt (VGS-004) |
| State semantics | Declared intent binding | Intent-Bound Execution (VGS-005) |

Both implementations independently validate the same gap: the absence of deterministic, auditable execution governance at the action boundary.

---

## Implementation Status

| Specification | Status | Endpoint |
|---------------|--------|----------|
| VGS-001 Runtime Admissibility | ✅ Live v0.7.0 | POST /v1/guard/verify |
| VGS-002 Governance State Machine | ✅ Live v0.7.0 | POST /v1/state/transition |
| VGS-003 Human Approval Invariants | ✅ Live v0.7.0 | POST /v1/approvals |
| VGS-004 Cryptographic Receipts | ✅ Live v0.7.0 | POST /v1/governance/receipt |
| VGS-005 Intent-Bound Execution | ✅ Live v0.7.0 | POST /v1/intent/bind |
| 40 Governance Invariants | ✅ Live v0.7.0 | GET /v1/invariants |
| Merkle Chain Audit | ✅ Live v0.6.0 | GET /v1/chain |
| Progression Admissibility | ✅ Live v0.6.0 | POST /v1/progression/evaluate |
| Cognitive Governance | ✅ Live v0.6.2 | POST /v1/cognitive/evaluate |
| Document Semantic Integrity | ✅ Live v0.6.4 | POST /v1/document/semantic-verify |

---

*VeriSigil AI · verisigilai.com · raheem@verisigilai.com*
*Raheem Larry Babatunde · Lagos, Nigeria*
*VGS v1.0 · May 2026*
