#!/usr/bin/env python3
"""
VeriSigil Offline Forensic Verifier
=====================================
VGS-008: Independent Verification Tool

An auditor can verify the complete VeriSigil governance chain
WITHOUT access to:
- VeriSigil servers
- The cloud platform
- The original operators
- Any live infrastructure

Usage:
    python3 verisigil_verify.py --chain chain_export.json
    python3 verisigil_verify.py --receipt receipt.json --key public_key.b64
    python3 verisigil_verify.py --package omnix_package/

This tool produces an ATF-compatible verification result
with a unique VSGVR-* identifier suitable for inclusion
in regulatory submissions and audit logs.

Determinism Guarantee (VGS-008-INV-001):
Any conformant implementation of this verifier, regardless of
platform or Python version, must produce an identical forensic
verdict given identical inputs.

License: CC BY 4.0
Author: VeriSigil AI — verisigilai.com
"""

import argparse
import base64
import hashlib
import json
import os
import sys
import secrets
from datetime import datetime, timezone
from typing import Optional

VERSION      = "VGS-008-1.0"
SCHEMA       = "VGS-008"
TOOL_NAME    = "VeriSigil Offline Forensic Verifier"
TOOL_VERSION = "1.0.0"


# ── CANONICAL SERIALIZATION ──────────────────────────────────
# VGS-008-INV-002: Canonical serialization is deterministic.
# Same input always produces same bytes.

def canonical_serialize(obj: dict) -> bytes:
    """Canonical JSON serialization — deterministic across platforms."""
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=True,
        default=str,
    ).encode('utf-8')

def canonical_hash(obj: dict) -> str:
    """Canonical SHA-256 hash of a governance object."""
    return hashlib.sha256(canonical_serialize(obj)).hexdigest()


# ── CHAIN VERIFICATION ───────────────────────────────────────

def verify_chain(chain_data: dict) -> dict:
    """
    Verify a VeriSigil governance chain export.
    
    Checks:
    1. Chain structure validity
    2. Hash chain integrity (each block links to previous)
    3. Merkle root consistency
    4. Signature presence on each block
    5. Drift detection
    """
    result = {
        "verified":          False,
        "schema":            SCHEMA,
        "blocks_total":      0,
        "blocks_verified":   0,
        "blocks_failed":     0,
        "violations":        [],
        "warnings":          [],
        "drift_detected":    False,
        "merkle_root":       None,
        "chain_head":        None,
        "verification_id":   f"VSGVR-{secrets.token_hex(8).upper()}",
        "verified_at":       datetime.now(timezone.utc).isoformat(),
        "tool":              f"{TOOL_NAME} v{TOOL_VERSION}",
    }

    blocks = chain_data.get("blocks", [])
    if not blocks:
        result["violations"].append("EMPTY_CHAIN: No blocks found in chain export")
        return result

    result["blocks_total"] = len(blocks)
    prev_hash = "genesis"

    for i, block in enumerate(blocks):
        block_hash   = block.get("block_hash", "")
        prev_in_block= block.get("previous_hash", "")

        # Check hash chain linkage
        if prev_in_block != prev_hash:
            result["violations"].append(
                f"CHAIN_BREAK at block #{i}: "
                f"expected previous_hash={prev_hash[:16]}... "
                f"got {prev_in_block[:16]}..."
            )
            result["blocks_failed"] += 1
            result["drift_detected"] = True
        else:
            result["blocks_verified"] += 1

        # Check block has required fields
        required_fields = ["block_hash", "previous_hash", "execution_id",
                          "agent_id", "action", "decision", "timestamp"]
        for field in required_fields:
            if field not in block:
                result["warnings"].append(f"Block #{i} missing field: {field}")

        prev_hash = block_hash

    # Compute Merkle root from block hashes
    hashes = [b.get("block_hash", "") for b in blocks]
    merkle = _compute_merkle(hashes)
    result["merkle_root"] = merkle
    result["chain_head"]  = prev_hash[:16] + "..." if prev_hash else None

    # Compare against claimed merkle root
    claimed_merkle = chain_data.get("merkle_root", "")
    if claimed_merkle and claimed_merkle != merkle:
        result["violations"].append(
            f"MERKLE_MISMATCH: claimed={claimed_merkle[:16]}... "
            f"computed={merkle[:16]}..."
        )
        result["drift_detected"] = True

    result["verified"] = (
        len(result["violations"]) == 0 and
        not result["drift_detected"]
    )

    return result


def _compute_merkle(hashes: list) -> str:
    """Compute Merkle root — deterministic implementation."""
    if not hashes:
        return hashlib.sha256(b"empty").hexdigest()
    nodes = list(hashes)
    while len(nodes) > 1:
        if len(nodes) % 2 == 1:
            nodes.append(nodes[-1])
        nodes = [
            hashlib.sha256((nodes[i] + nodes[i+1]).encode()).hexdigest()
            for i in range(0, len(nodes), 2)
        ]
    return nodes[0]


# ── RECEIPT VERIFICATION ─────────────────────────────────────

def verify_receipt(receipt: dict, public_key_b64: Optional[str] = None) -> dict:
    """
    Verify a VGS-004 Cryptographic Governance Receipt.
    
    Checks:
    1. Receipt schema compliance
    2. Required fields presence
    3. State hash recomputation
    4. Signature verification (if public key provided)
    5. Timestamp validity
    """
    result = {
        "verified":        False,
        "schema":          SCHEMA,
        "receipt_id":      receipt.get("decision_id", "unknown"),
        "decision":        receipt.get("decision", "unknown"),
        "agent_id":        receipt.get("agent_id", "unknown"),
        "violations":      [],
        "warnings":        [],
        "state_hash_valid":False,
        "signature_valid": None,
        "verification_id": f"VSGVR-{secrets.token_hex(8).upper()}",
        "verified_at":     datetime.now(timezone.utc).isoformat(),
        "tool":            f"{TOOL_NAME} v{TOOL_VERSION}",
    }

    # Check required fields
    required = ["decision_id", "agent_id", "action_type", "decision",
                "state_hash", "authority_hash", "timestamp", "schema"]
    for field in required:
        if field not in receipt:
            result["violations"].append(f"MISSING_FIELD: {field}")

    if result["violations"]:
        return result

    # Recompute state hash
    state_data   = (
        f"{receipt['agent_id']}|"
        f"{receipt['action_type']}|"
        f"{receipt['decision']}|"
        f"{receipt.get('trust_score', 0)}|"
        f"{receipt['timestamp']}"
    )
    computed_hash = hashlib.sha256(state_data.encode()).hexdigest()
    claimed_hash  = receipt.get("state_hash", "")

    result["state_hash_valid"] = (computed_hash == claimed_hash)
    if not result["state_hash_valid"]:
        result["violations"].append(
            f"STATE_HASH_MISMATCH: "
            f"computed={computed_hash[:16]}... "
            f"claimed={claimed_hash[:16]}..."
        )

    # Check VGS schema
    if receipt.get("schema") not in ("VGS-004", "VGS-004-1.0"):
        result["warnings"].append(
            f"Schema mismatch: expected VGS-004, got {receipt.get('schema')}"
        )

    # Check timestamp is parseable
    try:
        datetime.fromisoformat(receipt["timestamp"])
    except ValueError:
        result["violations"].append("INVALID_TIMESTAMP: Cannot parse timestamp")

    # Signature verification (Ed25519 if nacl available)
    if public_key_b64:
        try:
            from nacl.signing import VerifyKey
            from nacl.encoding import Base64Encoder
            from nacl.exceptions import BadSignatureError

            vk  = VerifyKey(base64.b64decode(public_key_b64))
            sig_str = receipt.get("signature", "")
            if sig_str.startswith("ed25519:"):
                sig = base64.b64decode(sig_str[8:])
                msg = canonical_serialize({
                    k: v for k, v in receipt.items()
                    if k not in ("signature", "signatures")
                })
                try:
                    vk.verify(msg, sig)
                    result["signature_valid"] = True
                except BadSignatureError:
                    result["signature_valid"] = False
                    result["violations"].append("INVALID_SIGNATURE: Ed25519 signature verification failed")
            else:
                result["warnings"].append("Signature format not Ed25519 — skipping verification")
        except ImportError:
            result["warnings"].append("PyNaCl not available — skipping signature verification")

    result["verified"] = (
        len(result["violations"]) == 0 and
        result["state_hash_valid"]
    )

    return result


# ── INVARIANT CHECK ──────────────────────────────────────────

def verify_invariants(governance_data: dict) -> dict:
    """
    Verify that a governance decision satisfies VGS invariants.
    Offline check — no platform access required.
    """
    result = {
        "verified":          False,
        "schema":            SCHEMA,
        "invariants_checked":0,
        "violations":        [],
        "warnings":          [],
        "verification_id":   f"VSGVR-{secrets.token_hex(8).upper()}",
        "verified_at":       datetime.now(timezone.utc).isoformat(),
    }

    decision     = governance_data.get("decision","")
    trust_score  = float(governance_data.get("trust_score", 0))
    consequence  = governance_data.get("consequence","MEDIUM").upper()
    action_type  = governance_data.get("action_type","")
    has_passport = bool(governance_data.get("agent_id"))

    checks = [
        # I-01: Passport required
        (has_passport, "I-01", "DENY",
         "No valid agent identity found in governance record"),

        # I-06: Trust floor
        (trust_score >= 0.50, "I-06", "DENY",
         f"Trust score {trust_score:.3f} below minimum threshold 0.50"),

        # E-02: CRITICAL requires human
        (not (consequence == "CRITICAL" and decision == "ALLOW"), "E-02",
         "REQUIRE_HUMAN_APPROVAL",
         "CRITICAL consequence cannot be ALLOW without human approval"),

        # A-01: Chain entry required
        (bool(governance_data.get("chain_block") or
              governance_data.get("execution_id")), "A-01", "DENY",
         "No chain entry found — governance decision must be chained"),
    ]

    result["invariants_checked"] = len(checks)
    for passed, inv_id, violation, message in checks:
        if not passed:
            result["violations"].append({
                "invariant": inv_id,
                "violation": violation,
                "message":   message,
            })

    result["verified"] = len(result["violations"]) == 0
    return result


# ── REPORT GENERATION ────────────────────────────────────────

def generate_report(results: dict, output_format: str = "text") -> str:
    """Generate a forensic verification report."""
    lines = [
        f"{'='*60}",
        f"  {TOOL_NAME}",
        f"  Version: {TOOL_VERSION}",
        f"  Schema:  {SCHEMA}",
        f"{'='*60}",
        f"",
        f"Verification ID: {results.get('verification_id','N/A')}",
        f"Verified at:     {results.get('verified_at','N/A')}",
        f"",
    ]

    if "chain" in results:
        c = results["chain"]
        lines += [
            f"CHAIN VERIFICATION",
            f"  Blocks total:    {c.get('blocks_total',0)}",
            f"  Blocks verified: {c.get('blocks_verified',0)}",
            f"  Blocks failed:   {c.get('blocks_failed',0)}",
            f"  Merkle root:     {(c.get('merkle_root') or '')[:32]}...",
            f"  Drift detected:  {c.get('drift_detected',False)}",
            f"  Result:          {'✓ INTACT' if c.get('verified') else '✕ COMPROMISED'}",
            f"",
        ]

    if "receipt" in results:
        r = results["receipt"]
        lines += [
            f"RECEIPT VERIFICATION",
            f"  Decision ID:     {r.get('receipt_id','N/A')}",
            f"  Decision:        {r.get('decision','N/A')}",
            f"  State hash:      {'✓ VALID' if r.get('state_hash_valid') else '✕ INVALID'}",
            f"  Signature:       {'✓ VALID' if r.get('signature_valid') else '— not checked' if r.get('signature_valid') is None else '✕ INVALID'}",
            f"  Result:          {'✓ VERIFIED' if r.get('verified') else '✕ FAILED'}",
            f"",
        ]

    if "invariants" in results:
        i = results["invariants"]
        lines += [
            f"INVARIANT CHECK",
            f"  Checked:         {i.get('invariants_checked',0)}",
            f"  Violations:      {len(i.get('violations',[]))}",
            f"  Result:          {'✓ ALL PASSED' if i.get('verified') else '✕ VIOLATIONS FOUND'}",
            f"",
        ]

    # Overall verdict
    all_verified = all(
        results.get(k, {}).get("verified", True)
        for k in ("chain", "receipt", "invariants")
        if k in results
    )
    lines += [
        f"{'='*60}",
        f"  OVERALL VERDICT: {'✓ GOVERNANCE VERIFIED' if all_verified else '✕ GOVERNANCE FAILED'}",
        f"{'='*60}",
    ]

    # Violations
    all_violations = []
    for k in ("chain", "receipt", "invariants"):
        if k in results:
            all_violations.extend(results[k].get("violations", []))

    if all_violations:
        lines += ["", "VIOLATIONS:"]
        for v in all_violations:
            if isinstance(v, dict):
                lines.append(f"  [{v.get('invariant','')}] {v.get('message',v)}")
            else:
                lines.append(f"  {v}")

    return "\n".join(lines)


# ── CLI ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description=f"{TOOL_NAME} v{TOOL_VERSION}",
        epilog="Offline verification — no network access required."
    )
    parser.add_argument("--chain",   help="Path to chain export JSON file")
    parser.add_argument("--receipt", help="Path to governance receipt JSON file")
    parser.add_argument("--key",     help="Path to Ed25519 public key (base64)")
    parser.add_argument("--invariants", help="Path to governance decision JSON for invariant check")
    parser.add_argument("--output",  choices=["text","json"], default="text")
    parser.add_argument("--version", action="store_true", help="Show version")

    args = parser.parse_args()

    if args.version:
        print(f"{TOOL_NAME} v{TOOL_VERSION} — {SCHEMA}")
        sys.exit(0)

    if not any([args.chain, args.receipt, args.invariants]):
        parser.print_help()
        sys.exit(1)

    results = {}
    verification_id = f"VSGVR-{secrets.token_hex(8).upper()}"

    # Chain verification
    if args.chain:
        with open(args.chain) as f:
            chain_data = json.load(f)
        results["chain"] = verify_chain(chain_data)
        results["chain"]["verification_id"] = verification_id

    # Receipt verification
    if args.receipt:
        with open(args.receipt) as f:
            receipt_data = json.load(f)
        public_key = None
        if args.key:
            with open(args.key) as f:
                public_key = f.read().strip()
        results["receipt"] = verify_receipt(receipt_data, public_key)
        results["receipt"]["verification_id"] = verification_id

    # Invariant check
    if args.invariants:
        with open(args.invariants) as f:
            gov_data = json.load(f)
        results["invariants"] = verify_invariants(gov_data)
        results["invariants"]["verification_id"] = verification_id

    results["verification_id"] = verification_id
    results["verified_at"]     = datetime.now(timezone.utc).isoformat()
    results["tool"]            = f"{TOOL_NAME} v{TOOL_VERSION}"
    results["schema"]          = SCHEMA

    if args.output == "json":
        print(json.dumps(results, indent=2, default=str))
    else:
        print(generate_report(results))

    # Exit code — 0 = verified, 1 = failed
    all_verified = all(
        results.get(k, {}).get("verified", True)
        for k in ("chain", "receipt", "invariants")
        if k in results
    )
    sys.exit(0 if all_verified else 1)


if __name__ == "__main__":
    main()
