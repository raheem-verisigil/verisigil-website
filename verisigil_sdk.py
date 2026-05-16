"""
VeriSigil AI — Governed Execution SDK
======================================
One file. Drop into any project.
Every agent action governed automatically.

Usage:
    from verisigil import VeriSigil, govern

    vs = VeriSigil(api_key="your-api-key", agent_id="vsa_xxx")

    # Decorator — automatic governance
    @vs.govern(action="payment", consequence="HIGH")
    def transfer_funds(amount, recipient):
        # VeriSigil intercepts before this runs
        return execute_transfer(amount, recipient)

    # Direct call
    decision = vs.verify(
        action="payment",
        details={"amount_usd": 5000}
    )

    # Context manager
    with vs.governed_action("delete_records", consequence="HIGH") as gate:
        if gate.allowed:
            delete_records()

    # Progression admissibility
    result = vs.progression(
        workflow_id="wf_001",
        current_step=3,
        total_steps=5,
        intended_action="transfer_funds",
        evidence={"amount_usd": 50000, "approval_chain": "approved"},
        consequence="HIGH"
    )

    # Continuous monitoring
    monitor = vs.start_monitor(workflow_id="wf_001")
    while running:
        check = monitor.check(trust_score=0.963)
        if not check.admissible:
            break
        time.sleep(30)

    # Survivability check
    score = vs.survivability(
        action="delete_records",
        consequence="HIGH",
        context={"backup_confirmed": True}
    )

Full documentation: https://verisigilai.com/sdk.html
API docs: https://verisigil-api-production.up.railway.app/docs
"""

import functools
import time
import uuid
from typing import Optional, Callable, Any
from contextlib import contextmanager

try:
    import httpx
    _HTTP_CLIENT = "httpx"
except ImportError:
    import urllib.request
    import json as _json
    _HTTP_CLIENT = "urllib"

__version__ = "0.6.0"
__author__  = "VeriSigil AI"
__url__     = "https://verisigilai.com"


# ── EXCEPTIONS ───────────────────────────────────────────────

class VeriSigilError(Exception):
    """Base VeriSigil exception."""
    pass

class ActionDenied(VeriSigilError):
    """Raised when Runtime Guard denies an action."""
    def __init__(self, reason: str, confidence: float = 0.0):
        self.reason     = reason
        self.confidence = confidence
        super().__init__(f"Action DENIED: {reason}")

class ActionEscalated(VeriSigilError):
    """Raised when action requires human approval."""
    def __init__(self, reason: str, approval_url: str = "", approval_id: str = ""):
        self.reason       = reason
        self.approval_url = approval_url
        self.approval_id  = approval_id
        super().__init__(f"Action requires human approval: {reason}\nApproval URL: {approval_url}")

class ProgressionBlocked(VeriSigilError):
    """Raised when progression is not admissible."""
    def __init__(self, decision: str, reasons: list):
        self.decision = decision
        self.reasons  = reasons
        super().__init__(f"Progression {decision}: {' | '.join(reasons)}")


# ── DECISION RESULT ──────────────────────────────────────────

class Decision:
    def __init__(self, data: dict):
        self._data        = data
        self.decision     = data.get("decision", "DENY")
        self.allowed      = self.decision == "ALLOW"
        self.denied       = self.decision == "DENY"
        self.escalated    = self.decision == "REQUIRE_HUMAN_APPROVAL"
        self.confidence   = data.get("confidence", 0.0)
        self.reason       = data.get("reason", "")
        self.trust_score  = data.get("trust_score", 0.0)
        self.approval_url = data.get("approval_url", "")
        self.approval_id  = data.get("approval_id", "")
        self.execution_id = data.get("execution_id", "")
        self.latency_ms   = data.get("latency_ms", 0.0)
        self.chain_block  = data.get("chain_block")

    def __bool__(self):
        return self.allowed

    def __repr__(self):
        return f"Decision({self.decision}, confidence={self.confidence:.2f}, latency={self.latency_ms}ms)"

    def raise_if_not_allowed(self):
        """Raise appropriate exception if not allowed."""
        if self.denied:
            raise ActionDenied(self.reason, self.confidence)
        if self.escalated:
            raise ActionEscalated(self.reason, self.approval_url, self.approval_id)


class ProgressionResult:
    def __init__(self, data: dict):
        self._data             = data
        self.decision          = data.get("decision", "")
        self.allowed           = self.decision == "PROGRESSION_ALLOWED"
        self.requires_evidence = self.decision == "PROGRESSION_REQUIRES_EVIDENCE"
        self.requires_authority= self.decision == "PROGRESSION_REQUIRES_AUTHORITY"
        self.requires_human    = self.decision == "PROGRESSION_REQUIRES_HUMAN_REVIEW"
        self.anomaly           = self.decision == "PROGRESSION_TRAJECTORY_ANOMALY"
        self.reasons           = data.get("reasons", [])
        self.missing_evidence  = data.get("missing_evidence", [])
        self.authority_level   = data.get("authority_level", "")
        self.trust_score       = data.get("trust_score", 0.0)
        self.latency_ms        = data.get("latency_ms", 0.0)
        self.chain_block       = data.get("chain_block")

    def __bool__(self):
        return self.allowed

    def raise_if_blocked(self):
        if not self.allowed:
            raise ProgressionBlocked(self.decision, self.reasons)


class SurvivabilityResult:
    def __init__(self, data: dict):
        self._data              = data
        self.score              = data.get("survivability_score", 0.0)
        self.recommendation     = data.get("recommendation", "BLOCK")
        self.risk_level         = data.get("risk_level", "HIGH")
        self.reversible         = data.get("reversible", False)
        self.factors            = data.get("factors", [])
        self.recovery_estimate  = data.get("recovery_estimate", "unknown")
        self.should_proceed     = self.recommendation in ("PROCEED", "PROCEED_WITH_CAUTION")

    def __repr__(self):
        return f"Survivability(score={self.score:.3f}, recommendation={self.recommendation})"


class ContinuousMonitor:
    def __init__(self, client, monitor_data: dict):
        self._client    = client
        self.monitor_id = monitor_data.get("monitor_id", "")
        self.agent_id   = monitor_data.get("agent_id", "")
        self.interval   = monitor_data.get("interval_sec", 30)
        self.status     = monitor_data.get("status", "monitoring")
        self._data      = monitor_data

    def check(self, trust_score: float = 0.963, context: dict = None) -> dict:
        """Run one admissibility check. Call this periodically."""
        result = self._client._post("/v1/continuous/check", {
            "monitor_id":  self.monitor_id,
            "trust_score": trust_score,
            "context":     context or {},
        })
        return result

    def __repr__(self):
        return f"ContinuousMonitor(id={self.monitor_id}, agent={self.agent_id}, interval={self.interval}s)"


# ── GOVERNED ACTION CONTEXT MANAGER ─────────────────────────

class GovernedAction:
    def __init__(self, decision: Decision):
        self._decision = decision
        self.allowed   = decision.allowed
        self.decision  = decision.decision
        self.reason    = decision.reason

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


# ── MAIN SDK CLASS ───────────────────────────────────────────

class VeriSigil:
    """
    VeriSigil Governed Execution SDK.

    Every method call that touches an AI agent action
    is automatically governed, logged, and chained.
    """

    BASE_URL = "https://verisigil-api-production.up.railway.app"

    def __init__(
        self,
        api_key:       str,
        agent_id:      str,
        org_id:        str  = "default",
        base_url:      str  = None,
        raise_on_deny: bool = True,
        timeout:       int  = 10,
    ):
        self.api_key       = api_key
        self.agent_id      = agent_id
        self.org_id        = org_id
        self.base_url      = base_url or self.BASE_URL
        self.raise_on_deny = raise_on_deny
        self.timeout       = timeout
        self._session      = None

    # ── HTTP HELPERS ─────────────────────────────────────────

    def _post(self, path: str, data: dict) -> dict:
        """Make a POST request to VeriSigil API."""
        url     = f"{self.base_url}{path}"
        headers = {
            "Content-Type": "application/json",
            "x-api-key":    self.api_key,
            "x-sdk-version": __version__,
        }
        if _HTTP_CLIENT == "httpx":
            with httpx.Client(timeout=self.timeout) as c:
                r = c.post(url, json=data, headers=headers)
                return r.json()
        else:
            import json
            req  = urllib.request.Request(
                url,
                data    = json.dumps(data).encode(),
                headers = headers,
                method  = "POST",
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return json.loads(r.read())

    def _get(self, path: str, params: dict = None) -> dict:
        """Make a GET request to VeriSigil API."""
        import json
        url = f"{self.base_url}{path}"
        if params:
            qs  = "&".join(f"{k}={v}" for k,v in params.items())
            url = f"{url}?{qs}"
        if _HTTP_CLIENT == "httpx":
            with httpx.Client(timeout=self.timeout) as c:
                r = c.get(url, headers={"x-api-key": self.api_key})
                return r.json()
        else:
            req = urllib.request.Request(
                url, headers={"x-api-key": self.api_key}, method="GET"
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return json.loads(r.read())

    # ── CORE: RUNTIME GUARD ──────────────────────────────────

    def verify(
        self,
        action:      str,
        details:     dict = None,
        resource:    str  = "",
        context:     str  = "production",
    ) -> Decision:
        """
        Verify an action with Runtime Guard.
        Returns Decision object — check .allowed, .denied, .escalated.

        Example:
            decision = vs.verify("payment", {"amount_usd": 5000})
            if decision.allowed:
                execute()
        """
        result = self._post("/v1/guard/verify", {
            "agent_id":       self.agent_id,
            "action_type":    action,
            "action_details": details or {},
            "resource":       resource or f"{action}_api",
            "context":        context,
        })
        decision = Decision(result)
        if self.raise_on_deny:
            decision.raise_if_not_allowed()
        return decision

    # ── DECORATOR ────────────────────────────────────────────

    def govern(
        self,
        action:      str,
        consequence: str = "MEDIUM",
        details_fn:  Optional[Callable] = None,
    ):
        """
        Decorator — automatically govern any function.

        Example:
            @vs.govern(action="payment", consequence="HIGH")
            def transfer_funds(amount, recipient):
                return execute_transfer(amount, recipient)
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Build details from kwargs or details_fn
                details = {}
                if details_fn:
                    details = details_fn(*args, **kwargs)
                elif kwargs:
                    details = {k: v for k, v in kwargs.items()
                               if isinstance(v, (str, int, float, bool))}

                decision = self.verify(action=action, details=details)
                if not decision.allowed:
                    if self.raise_on_deny:
                        decision.raise_if_not_allowed()
                    return None

                return func(*args, **kwargs)
            return wrapper
        return decorator

    # ── CONTEXT MANAGER ──────────────────────────────────────

    @contextmanager
    def governed_action(self, action: str, details: dict = None, consequence: str = "MEDIUM"):
        """
        Context manager for governed actions.

        Example:
            with vs.governed_action("delete_records", consequence="HIGH") as gate:
                if gate.allowed:
                    delete_records()
        """
        decision = self.verify(action=action, details=details or {})
        yield GovernedAction(decision)

    # ── PROGRESSION ADMISSIBILITY ────────────────────────────

    def progression(
        self,
        workflow_id:      str,
        current_step:     int,
        total_steps:      int,
        intended_action:  str,
        evidence:         dict = None,
        consequence:      str  = "MEDIUM",
        previous_steps:   list = None,
        raise_if_blocked: bool = False,
    ) -> ProgressionResult:
        """
        Evaluate progression admissibility.
        Should this specific state transition be permitted now?

        Example:
            result = vs.progression(
                workflow_id="wf_001",
                current_step=3,
                total_steps=5,
                intended_action="transfer_funds",
                evidence={"approval_chain": "approved"},
                consequence="HIGH"
            )
            if result.allowed:
                proceed()
        """
        result = self._post("/v1/progression/evaluate", {
            "agent_id":        self.agent_id,
            "workflow_id":     workflow_id,
            "current_step":    current_step,
            "total_steps":     total_steps,
            "previous_steps":  previous_steps or [],
            "intended_action": intended_action,
            "evidence":        evidence or {},
            "consequence_level": consequence,
            "org_id":          self.org_id,
        })
        pr = ProgressionResult(result)
        if raise_if_blocked:
            pr.raise_if_blocked()
        return pr

    # ── CONTINUOUS MONITORING ────────────────────────────────

    def start_monitor(
        self,
        workflow_id:  str,
        interval_sec: int = 30,
    ) -> ContinuousMonitor:
        """
        Start continuous admissibility monitoring.

        Example:
            monitor = vs.start_monitor("wf_001", interval_sec=60)
            while agent_running:
                check = monitor.check(trust_score=0.963)
                if not check.get("admissible"):
                    agent.pause()
                time.sleep(60)
        """
        result = self._post(
            f"/v1/continuous/start?agent_id={self.agent_id}"
            f"&workflow_id={workflow_id}"
            f"&interval_sec={interval_sec}"
            f"&org_id={self.org_id}",
            {}
        )
        return ContinuousMonitor(self, result)

    # ── SURVIVABILITY SCORING ────────────────────────────────

    def survivability(
        self,
        action:      str,
        consequence: str  = "MEDIUM",
        context:     dict = None,
    ) -> SurvivabilityResult:
        """
        Score execution survivability before running an action.
        0.0 = catastrophic · 1.0 = fully recoverable

        Example:
            score = vs.survivability("delete_records", "HIGH",
                                     {"backup_confirmed": True})
            if score.should_proceed:
                delete_records()
        """
        result = self._post("/v1/survivability/score", {
            "agent_id":         self.agent_id,
            "action":           action,
            "consequence":      consequence,
            "workflow_context": context or {},
        })
        return SurvivabilityResult(result)

    # ── REVALIDATION ─────────────────────────────────────────

    def revalidate(
        self,
        execution_id:      str,
        workflow_step:     int,
        original_decision: str,
        context:           dict = None,
    ) -> dict:
        """
        Revalidate a previously approved execution.
        Call at key workflow checkpoints to confirm approval still holds.

        Example:
            result = vs.revalidate(
                execution_id="exec_xxx",
                workflow_step=4,
                original_decision="ALLOW"
            )
            if not result["still_valid"]:
                agent.pause()
        """
        return self._post("/v1/revalidate", {
            "agent_id":          self.agent_id,
            "execution_id":      execution_id,
            "workflow_step":     workflow_step,
            "original_decision": original_decision,
            "current_context":   context or {},
            "org_id":            self.org_id,
        })

    # ── CHAIN PROVENANCE ─────────────────────────────────────

    def start_chain(self, workflow_id: str) -> str:
        """
        Start an agent chain for multi-agent provenance tracking.
        Returns chain_id — pass to other agents in the workflow.

        Example:
            chain_id = vs.start_chain("wf_multi_001")
            # Pass chain_id to Agent B, Agent C...
        """
        result = self._post(
            f"/v1/chain/provenance/start?agent_id={self.agent_id}"
            f"&workflow_id={workflow_id}&org_id={self.org_id}",
            {}
        )
        return result.get("chain_id", "")

    def record_call(
        self,
        chain_id:    str,
        callee_id:   str,
        action:      str,
        decision:    str,
        trust_score: float = 0.963,
    ) -> dict:
        """Record one agent calling another in a chain."""
        return self._post("/v1/chain/provenance/record", {
            "chain_id":    chain_id,
            "caller_id":   self.agent_id,
            "callee_id":   callee_id,
            "action":      action,
            "decision":    decision,
            "trust_score": trust_score,
        })

    def get_chain(self, chain_id: str) -> dict:
        """Get full provenance for a chain."""
        return self._get(f"/v1/chain/provenance/{chain_id}")

    # ── HEALTH & STATUS ──────────────────────────────────────

    def health(self) -> dict:
        """Check VeriSigil API health."""
        return self._get("/health")

    def governance_summary(self) -> dict:
        """Get full runtime governance summary."""
        return self._get("/v1/governance/summary")

    def __repr__(self):
        return f"VeriSigil(agent={self.agent_id}, org={self.org_id}, v{__version__})"


# ── CONVENIENCE FUNCTIONS ────────────────────────────────────

def govern(
    api_key:     str,
    agent_id:    str,
    action:      str,
    consequence: str = "MEDIUM",
):
    """
    Quick decorator without instantiating VeriSigil.

    Example:
        @govern(api_key="vs_xxx", agent_id="vsa_xxx", action="payment")
        def transfer_funds(amount):
            pass
    """
    vs = VeriSigil(api_key=api_key, agent_id=agent_id)
    return vs.govern(action=action, consequence=consequence)


# ── USAGE EXAMPLES ───────────────────────────────────────────

EXAMPLE_USAGE = """
# ── BASIC USAGE ──────────────────────────────────────────

from verisigil import VeriSigil

vs = VeriSigil(
    api_key  = "vs_org_xxx_your_api_key",
    agent_id = "vsa_your_agent_id",
)

# ── 1. VERIFY BEFORE ACTION ──────────────────────────────

decision = vs.verify("payment", {"amount_usd": 5000})
if decision.allowed:
    transfer_funds(5000)
elif decision.escalated:
    print(f"Awaiting approval: {decision.approval_url}")
else:
    print(f"Blocked: {decision.reason}")

# ── 2. DECORATOR ─────────────────────────────────────────

@vs.govern(action="payment", consequence="HIGH")
def transfer_funds(amount, recipient):
    return execute_transfer(amount, recipient)

# Raises ActionDenied or ActionEscalated automatically

# ── 3. CONTEXT MANAGER ───────────────────────────────────

with vs.governed_action("delete_records", consequence="HIGH") as gate:
    if gate.allowed:
        delete_all_records()

# ── 4. PROGRESSION ADMISSIBILITY ─────────────────────────

result = vs.progression(
    workflow_id     = "wf_payment_001",
    current_step    = 3,
    total_steps     = 5,
    intended_action = "transfer_funds",
    evidence        = {
        "amount_usd":             50000,
        "business_justification": "Vendor Q2 payment",
        "approval_chain":         "manager_approved",
        "requestor_id":           "user_123",
    },
    consequence     = "HIGH",
)
if result.allowed:
    proceed_to_step_4()
elif result.requires_evidence:
    print(f"Need: {result.missing_evidence}")

# ── 5. CONTINUOUS MONITORING ─────────────────────────────

import time
monitor = vs.start_monitor("wf_long_running", interval_sec=30)
while agent.is_running():
    check = monitor.check(trust_score=agent.trust_score)
    if not check.get("admissible"):
        agent.pause(reason=check.get("reasons"))
        break
    time.sleep(30)

# ── 6. SURVIVABILITY CHECK ───────────────────────────────

score = vs.survivability(
    action      = "delete_records",
    consequence = "HIGH",
    context     = {
        "backup_confirmed":  True,
        "rollback_available": True,
        "blast_radius":      "MEDIUM",
    }
)
print(f"Score: {score.score} · {score.recommendation}")
if score.should_proceed:
    delete_records()

# ── 7. RUNTIME REVALIDATION ──────────────────────────────

# At step 1 — approved
decision = vs.verify("payment", {"amount_usd": 50000})
execution_id = decision.execution_id

# At step 4 — revalidate
reval = vs.revalidate(
    execution_id      = execution_id,
    workflow_step     = 4,
    original_decision = "ALLOW",
)
if not reval["still_valid"]:
    agent.pause()

# ── 8. MULTI-AGENT PROVENANCE ────────────────────────────

# Agent A starts chain
chain_id = vs.start_chain("wf_multi_001")

# Agent A calls Agent B
vs.record_call(chain_id, "vsa_agent_b", "data_fetch", "ALLOW")

# Agent B calls Agent C
vs_b = VeriSigil(api_key="vs_xxx", agent_id="vsa_agent_b")
vs_b.record_call(chain_id, "vsa_agent_c", "payment", "REQUIRE_HUMAN_APPROVAL")

# Get full provenance
provenance = vs.get_chain(chain_id)
print(provenance["attribution"])
"""
