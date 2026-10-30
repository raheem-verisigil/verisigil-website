# NCS × VeriSigilAI — VCB Assessment Plan

**Assessment ID:** `NCS-VSA-VCB-2026-001`  
**Status:** Registered; execution not started.  
**Assessment authority:** Native Conduct Standard (NCS).

## Scope

This assessment separates three evidence streams:

1. **Native Behavior Baseline:** exact AI model/agent behavior before project-specific VCB policy.
2. **Policy Delta Profile:** paired behavior after VCB/project policy and configuration are applied.
3. **Application Assurance:** VCB authorization, parameter binding, receipt verification, replay, fail-closed behavior and synthetic sink outcomes.

Application enforcement is not evidence of native model behavior. Website copy and previously published trust metrics are not NCS test evidence.

## Source review outcome

The reviewed `README.md`, `index.html` and `trust.html` describe the VCB architecture and public-facing claims. They do not establish a concrete executable AI runtime, model/provider/version, immutable model artifact or repeatable invocation path. Native and policy-delta testing are therefore blocked until that subject is identified.

The application-assurance scenarios are specified but have not been run. All tests must use a synthetic sink, with no live payments or production endpoints.

## Test cases

See [the machine-readable assessment record](assessments/NCS-VSA-VCB-2026-001.json) for the 15-case matrix, expected outcomes, evidence requirements and current status.

## Result integrity

Every run must record its exact subject commit, model/configuration identity, policy digest, harness version, test inputs/outputs, timestamps, raw evidence references, sink state, failures and canonical result digest. Never overwrite a prior run. Corrections create a new run linked to the prior record.

## Current result

- Runtime tests executed: **0**
- Native model tests executed: **0**
- Application assurance tests executed: **0**
- Grade or certificate issued: **No**
- Independent review completed: **No**

This is an assessment registration and source-review record, not a test pass, grade, certificate or independent validation.


### Source-review run
- Run ID: `NCS-VSA-VCB-2026-001-SR-001`.
- Status: completed source review only.
- Runtime tests executed: 0; native model tests: 0; policy-delta tests: 0; application-assurance tests: 0.
- Outcome: executable model/agent runtime not identified in the reviewed website repository; runtime testing blocked pending subject identification.
- Record: `ncs/assessments/runs/NCS-VSA-VCB-2026-001-SR-001.json`.

A separate NCS harness CI run in Cyraduct passed 71/71 tests. That verifies the NCS harness code only and is not a VeriSigilAI test result.


### Runtime API and test-harness source audit
The runtime governance API/SDK repository `raheem-verisigil/verisigil-api` has been identified. Its conformance suite declares 80 vectors. Static inspection found that 16 jurisdiction-resolution vectors (VEC-043–VEC-058) have expected outcomes but are not asserted by the current test runner; they enter a fallback `assert(true)` branch. This is a source-level finding, not a test execution. No NCS runtime tests have yet been executed against the VeriSigil API. The model/agent workload required for Native Behavior Baseline and Policy Delta remains unidentified.

See `ncs/assessments/runs/NCS-VSA-VCB-2026-001-SR-002.json`.
