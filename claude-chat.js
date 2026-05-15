// ============================================================
// VeriSigil AI — Claude Chat Edge Function
// Deploy to: Supabase Edge Functions
// Name: claude-chat
// ============================================================

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

const SYSTEM_PROMPT = `You are VeriSigil AI's compliance assistant — an expert on the EU AI Act, AI agent governance, and VeriSigil's products.

Your role:
- Answer questions about EU AI Act compliance clearly and concisely
- Help founders understand if their AI agent is HIGH_RISK or LIMITED_RISK
- Explain what Runtime Guard, cryptographic passports, and audit trails do
- Guide people toward VeriSigil's $499 Compliance Sprint when relevant

Key facts about VeriSigil:
- Runtime Guard: verifies every AI agent action before execution — returns ALLOW, DENY, or REQUIRE_HUMAN_APPROVAL in under 50ms
- Cryptographic passport: Ed25519 signed W3C DID standard identity for AI agents
- Compliance Sprint: $499 flat fee — fully automatic — passport + Runtime Guard + EU AI Act docs delivered in under 60 seconds
- EU AI Act enforcement: August 2, 2026 — about 79 days away
- HIGH_RISK industries: fintech, healthcare, legal, HR/recruitment, biometrics, law enforcement
- Article 14: requires human oversight for HIGH_RISK AI systems
- Article 50: transparency obligations — agents must be identifiable

Response style:
- Be helpful, direct, and technically accurate
- Keep responses under 120 words
- When someone describes a HIGH_RISK use case, mention the Compliance Sprint
- Never be pushy — inform first, suggest second
- End with a question or CTA only when natural

VeriSigil website: verisigilai.com
Compliance Sprint: verisigilai.com/eu-ai-act-sprint.html`;

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
  "Content-Type": "application/json",
};

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: CORS_HEADERS });
  }

  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405, headers: CORS_HEADERS
    });
  }

  try {
    const { messages } = await req.json();

    if (!messages || !Array.isArray(messages)) {
      return new Response(JSON.stringify({ error: "messages array required" }), {
        status: 400, headers: CORS_HEADERS
      });
    }

    // Get Claude API key from Supabase secrets
    const claudeKey = Deno.env.get("CLAUDE_API_KEY");
    if (!claudeKey) {
      return new Response(JSON.stringify({ error: "API key not configured" }), {
        status: 500, headers: CORS_HEADERS
      });
    }

    // Call Claude API
    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": claudeKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-20250514",
        max_tokens: 300,
        system: SYSTEM_PROMPT,
        messages: messages.slice(-10), // Keep last 10 messages max
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      console.error("[CLAUDE ERROR]", data);
      return new Response(JSON.stringify({ error: "Claude API error", detail: data }), {
        status: 500, headers: CORS_HEADERS
      });
    }

    const reply = data.content?.[0]?.text || "I'm having trouble responding. Please try again.";

    return new Response(JSON.stringify({ reply }), { headers: CORS_HEADERS });

  } catch (e) {
    console.error("[EDGE FUNCTION ERROR]", e);
    return new Response(JSON.stringify({ error: e.message }), {
      status: 500, headers: CORS_HEADERS
    });
  }
});
