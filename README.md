# VeriSigil AI

## Verifiable Consequence Boundaries for AI Actions

VeriSigil provides infrastructure for governing **consequential AI actions at declared execution boundaries**, with independently verifiable evidence of the enforcement result.

**AI systems decide. VeriSigil determines whether registered consequential actions are authorized to become real, enforces that decision at declared execution boundaries, and produces independently verifiable evidence of the result.**

> **Scope:** This describes registered protected workflows and declared enforcement surfaces. It is not a claim of universal AI coverage or universal prevention of unauthorized consequences.

### Approved architecture terminology

- **Architecture:** Verifiable Consequence Boundaries
- **Hero capability:** Cryptographic Consequence Enforcement
- **Runtime control:** Runtime Authority
- **Core mechanisms:** Authority-at-Consequence · Parameter-Locked Execution · Fail-Closed Runtime
- **Evidence:** Cryptographic Execution Receipts

The terminology above is intentionally narrow. The project is under architecture and terminology freeze: evidence comes before expansion.

---

## Why the boundary matters

AI systems can generate actions that have consequences outside the model: a payment, database mutation, deployment, data export, filing, or other external operation.

The important question is not only whether an action was generated, or whether an identity and policy existed somewhere upstream. At the declared execution boundary, the system must establish whether the **specific action is still authorized now**, under the conditions and parameters that will actually be executed.

Conceptually:

```text
AI / Agent
    |
    v
Identity + existing authorization / policy
    |
    v
VeriSigil
    |  current authority
    |  current conditions
    |  exact action
    |  exact parameters
    |  enforcement requirements
    |
    +---- REFUSE ----> no governed external effect
    |
    +---- ALLOW -----> declared protected execution boundary
                              |
                              v
                       external consequence
                              |
                              v
                 Cryptographic Execution Receipt
``` 

The model, agent framework, identity provider, policy engine, or external provider may change. The enforcement invariant is intended to remain stable.

---

## What is currently evidenced

The public proof program separates implementation, tested behavior, independent verification, and production claims.

| Area | Current status |
|---|---|
| Architecture freeze | **IN EFFECT** |
| Production claim | **NOT ALLOWED** |
| Locked production claim | **NOT YET DELIVERED** |
| Receipt integrity and Ed25519 verification | **VERIFIED** |
| Independent offline receipt verification | **VERIFIED** |
| Honest `UNDETERMINED` behavior | **VERIFIED** |
| STILL adversarial suite | **11/11 demonstrated on live Railway + Supabase** |
| Tamper detection | **DEMONSTRATED on live endpoint** |
| Parameter binding / commitment enforcement | **DEMONSTRATED on tested payment path** |
| Inadmissible tested paths reaching Paystack | **0 in tested scenarios** |
| Delegation live rerun | **PENDING independent confirmation** |
| Real Paystack transaction reference | **NOT PROVEN** |
| Multi-instance distributed atomicity | **NOT PROVEN** |
| Complete endpoint coverage | **NOT PROVEN** |
| Regulatory certification | **NOT CLAIMABLE** |

The authoritative public status and evidence surface is [`trust.html`](trust.html). Do not infer capabilities beyond the published evidence and limitations.

---

## Reproduce before trusting

The repository is intended to be a technical proof surface, not a feature catalogue.

Start here:

1. [`QUICKSTART.md`](QUICKSTART.md) — reproduce receipt verification and the expected bounded outcomes.
2. [`CHALLENGE.md`](CHALLENGE.md) — open adversarial testing protocol and current challenge boundaries.
3. [`VERISIGIL_PROOF_REPORT_V1.md`](VERISIGIL_PROOF_REPORT_V1.md) — consolidated proof report and claim ceiling.
4. [`CLAIMS_REGISTRY.md`](CLAIMS_REGISTRY.md) — frozen claims registry.
5. [`ActuatorSpec.md`](ActuatorSpec.md) — actuator-side contract and tested enforcement boundary, where present.

Proof scripts and formal artifacts in the repository are retained as reproducibility evidence. Historical specifications may contain terminology or architectural claims that are no longer authoritative; current claims are governed by the claims registry and proof report.

### Minimal research question

A useful first experiment is:

> Can an unauthorized variation of a consequential action be refused at the declared protected boundary, without the external state mutation occurring, while the result remains independently verifiable from the evidence?

The answer must be established by the relevant test and its recorded evidence—not by this README.

---

## Evidence hierarchy

VeriSigil uses a deliberately conservative claim ladder:

- **Implemented:** the mechanism exists in code.
- **Tested:** the mechanism has passed a defined reproducible test.
- **Independently verified:** evidence can be checked without relying on the originating runtime's narrative.
- **Generalized:** the invariant survives materially different consequence surfaces.
- **Interoperable:** the contract works across independent upstream and downstream environments.

A stronger claim is not inferred from a weaker one.

---

## What VeriSigil is not

VeriSigil is not presented here as:

- a universal AI safety system;
- a replacement for identity, IAM, policy engines, or enterprise security controls;
- a regulator, auditor, bank, payment institution, or government authority;
- proof that every AI action is governed;
- proof that every unauthorized consequence is prevented;
- proof of model reasoning correctness or policy correctness;
- regulatory certification or legal compliance certification;
- proof of live-money production payment execution where no real provider reference has been established;
- proof of complete distributed or multi-instance atomicity.

These boundaries are part of the architecture's credibility, not omissions to be hidden.

---

## Longer-term direction

The long-term engineering objective is provider-neutral enforcement at consequential execution boundaries:

```text
AI system / agent runtime
        |
        v
   VeriSigil enforcement
        |
        +----> payment
        +----> database mutation
        +----> deployment
        +----> enterprise workflow
        +----> government / external API
        +----> other consequential actuator
```

This is a direction for generalization and interoperability, not a claim that all of these surfaces are currently protected in production.

The sequence is deliberate:

**BUILD → PROVE → GENERALIZE → INTEROPERATE → STANDARDIZE → BECOME INFRASTRUCTURE**

The current phase is **PROVE**.

---

## Formal and technical material

The repository contains specifications, test vectors, verification tools, proof scripts, and formal artifacts. These should be read according to their status and date rather than treated as one undifferentiated product surface.

Where applicable, the project maintains public research/specification records and DOI-linked material. The current proof report and claims registry remain the primary references for what can be claimed today.

---

## Contributing / adversarial testing

The most valuable contribution is evidence that falsifies or strengthens a bounded claim.

Before proposing architectural changes:

1. reproduce the existing behavior;
2. inspect the current claims registry;
3. identify the exact invariant or claim boundary being tested;
4. record whether the result is PASS, FAIL, NOT_DIAGNOSTIC, or a NEW_FINDING;
5. do not silently convert a test result into a broader claim.

Architecture and terminology are currently frozen. New features, categories, and terminology are not being added merely to expand the surface area.

See [`CHALLENGE.md`](CHALLENGE.md) for the public adversarial testing protocol.

---

## Public surfaces

- [Website](https://verisigilai.com/)
- [Trust / evidence status](https://verisigilai.com/trust.html)
- [Demo and API surface](https://verisigilai.com/demos.html)
- [Terms](https://verisigilai.com/terms.html)

**Evidence before expansion. Reproduction before trust.**
