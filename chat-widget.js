/**
 * VeriSigil AI — Compliance Chat Widget v1.0
 * Add to any page with: <script src="/chat-widget.js"></script>
 * API key stored securely in Supabase Edge Function
 */
(function() {
  const EDGE_URL = 'https://ixiwsdjuduwwzbdfgunm.supabase.co/functions/v1/claude-chat';

  // ── STYLES ──────────────────────────────────────────────
  const css = `
    #vs-chat-btn {
      position:fixed;bottom:90px;right:24px;
      width:52px;height:52px;border-radius:50%;
      background:#00D4F5;color:#050E2B;
      border:none;cursor:pointer;font-size:20px;
      box-shadow:0 0 28px rgba(0,212,245,0.5);
      display:flex;align-items:center;justify-content:center;
      z-index:9996;transition:all 0.2s;
      font-family:'Segoe UI',sans-serif;
    }
    #vs-chat-btn:hover{transform:scale(1.08);box-shadow:0 0 44px rgba(0,212,245,0.7);}
    #vs-chat-notif{
      position:absolute;top:-2px;right:-2px;
      width:13px;height:13px;border-radius:50%;
      background:#22C55E;border:2px solid #050E2B;
      animation:vs-pulse 2s infinite;
    }
    @keyframes vs-pulse{0%,100%{box-shadow:0 0 0 0 rgba(34,197,94,0.4)}50%{box-shadow:0 0 0 5px rgba(34,197,94,0)}}
    #vs-chat-panel{
      position:fixed;bottom:154px;right:24px;
      width:360px;max-height:520px;
      background:#0D1A3A;border:1px solid rgba(30,58,110,0.6);
      border-radius:16px;overflow:hidden;
      box-shadow:0 24px 64px rgba(0,0,0,0.7);
      display:none;flex-direction:column;
      z-index:9995;
    }
    #vs-chat-panel.vs-open{display:flex;animation:vs-up 0.2s ease;}
    @keyframes vs-up{from{opacity:0;transform:translateY(16px);}to{opacity:1;transform:translateY(0);}}
    .vs-hdr{
      background:linear-gradient(135deg,#0A1628,#0D1A3A);
      border-bottom:1px solid rgba(30,58,110,0.6);
      padding:12px 14px;display:flex;align-items:center;gap:10px;
    }
    .vs-hdr-av{
      width:34px;height:34px;border-radius:50%;flex-shrink:0;
      background:linear-gradient(135deg,#00D4F5,#7C3AED);
      display:flex;align-items:center;justify-content:center;font-size:15px;
    }
    .vs-hdr-title{font-size:13px;font-weight:700;color:#fff;font-family:'Segoe UI',sans-serif;}
    .vs-hdr-status{font-size:10px;color:#22C55E;display:flex;align-items:center;gap:4px;font-family:'Segoe UI',sans-serif;}
    .vs-hdr-dot{width:5px;height:5px;border-radius:50%;background:#22C55E;}
    .vs-close{margin-left:auto;background:none;border:none;color:#94A3B8;cursor:pointer;font-size:16px;padding:2px 6px;border-radius:4px;}
    .vs-close:hover{color:#fff;background:rgba(255,255,255,0.05);}
    .vs-msgs{
      flex:1;overflow-y:auto;padding:14px;
      display:flex;flex-direction:column;gap:10px;
      max-height:300px;
    }
    .vs-msgs::-webkit-scrollbar{width:3px;}
    .vs-msgs::-webkit-scrollbar-thumb{background:rgba(30,58,110,0.6);border-radius:2px;}
    .vs-msg{display:flex;gap:8px;align-items:flex-start;}
    .vs-msg.vs-user{flex-direction:row-reverse;}
    .vs-msg-av{
      width:26px;height:26px;border-radius:50%;flex-shrink:0;
      display:flex;align-items:center;justify-content:center;font-size:11px;
    }
    .vs-msg.vs-ai .vs-msg-av{background:linear-gradient(135deg,#00D4F5,#7C3AED);}
    .vs-msg.vs-user .vs-msg-av{background:#0A1628;border:1px solid rgba(30,58,110,0.6);color:#94A3B8;}
    .vs-bubble{
      max-width:240px;padding:9px 12px;border-radius:10px;
      font-size:12.5px;line-height:1.6;font-family:'Segoe UI',sans-serif;
    }
    .vs-msg.vs-ai .vs-bubble{
      background:#0A1628;border:1px solid rgba(30,58,110,0.6);
      color:#E2E8F0;border-radius:4px 10px 10px 10px;
    }
    .vs-msg.vs-user .vs-bubble{
      background:rgba(0,212,245,0.1);border:1px solid rgba(0,212,245,0.2);
      color:#E2E8F0;border-radius:10px 4px 10px 10px;
    }
    .vs-cta-btn{
      display:inline-flex;align-items:center;gap:5px;
      background:#00D4F5;color:#050E2B;
      padding:6px 12px;border-radius:6px;
      font-size:11px;font-weight:700;
      text-decoration:none;margin-top:7px;
      font-family:'Segoe UI',sans-serif;
    }
    .vs-typing{display:flex;gap:4px;align-items:center;padding:9px 12px;}
    .vs-typing span{
      width:5px;height:5px;border-radius:50%;background:#94A3B8;
      animation:vs-type 1.2s infinite;
    }
    .vs-typing span:nth-child(2){animation-delay:0.2s;}
    .vs-typing span:nth-child(3){animation-delay:0.4s;}
    @keyframes vs-type{0%,60%,100%{opacity:0.3;transform:scale(0.8);}30%{opacity:1;transform:scale(1);}}
    .vs-qp{
      padding:8px 12px;display:flex;gap:5px;flex-wrap:wrap;
      border-top:1px solid rgba(30,58,110,0.6);
    }
    .vs-qp-btn{
      font-size:10px;font-family:'Courier New',monospace;
      padding:3px 9px;border-radius:20px;
      background:rgba(0,212,245,0.06);border:1px solid rgba(0,212,245,0.18);
      color:#00D4F5;cursor:pointer;white-space:nowrap;transition:all 0.15s;
    }
    .vs-qp-btn:hover{background:rgba(0,212,245,0.12);}
    .vs-inp-wrap{
      padding:10px 12px;border-top:1px solid rgba(30,58,110,0.6);
      display:flex;gap:7px;align-items:center;
    }
    .vs-inp{
      flex:1;background:#0A1628;border:1px solid rgba(30,58,110,0.6);
      border-radius:7px;padding:8px 10px;
      font-size:12.5px;font-family:'Segoe UI',sans-serif;color:#fff;
      outline:none;resize:none;transition:border-color 0.15s;
    }
    .vs-inp::placeholder{color:#94A3B8;}
    .vs-inp:focus{border-color:rgba(0,212,245,0.35);}
    .vs-send{
      width:32px;height:32px;border-radius:7px;
      background:#00D4F5;color:#050E2B;
      border:none;cursor:pointer;font-size:13px;
      display:flex;align-items:center;justify-content:center;
      flex-shrink:0;transition:opacity 0.15s;
    }
    .vs-send:hover{opacity:0.88;}
    .vs-send:disabled{opacity:0.4;cursor:not-allowed;}
  `;

  // ── INJECT STYLES ────────────────────────────────────────
  const style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  // ── INJECT HTML ──────────────────────────────────────────
  const html = `
    <button id="vs-chat-btn" onclick="vsToggle()">
      <span id="vs-chat-icon">⬡</span>
      <span id="vs-chat-notif"></span>
    </button>

    <div id="vs-chat-panel">
      <div class="vs-hdr">
        <div class="vs-hdr-av">⬡</div>
        <div>
          <div class="vs-hdr-title">VeriSigil Compliance AI</div>
          <div class="vs-hdr-status"><div class="vs-hdr-dot"></div>EU AI Act Expert · Online</div>
        </div>
        <button class="vs-close" onclick="vsToggle()">✕</button>
      </div>
      <div class="vs-msgs" id="vs-msgs"></div>
      <div class="vs-qp">
        <button class="vs-qp-btn" onclick="vsQuick('Is my fintech agent HIGH_RISK?')">Fintech risk?</button>
        <button class="vs-qp-btn" onclick="vsQuick('What is Article 14?')">Article 14</button>
        <button class="vs-qp-btn" onclick="vsQuick('When is the EU AI Act deadline?')">Deadline?</button>
        <button class="vs-qp-btn" onclick="vsQuick('What does VeriSigil do?')">What is VeriSigil?</button>
      </div>
      <div class="vs-inp-wrap">
        <textarea class="vs-inp" id="vs-inp" placeholder="Ask about EU AI Act compliance..." rows="1"
          onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();vsSend();}"></textarea>
        <button class="vs-send" id="vs-send" onclick="vsSend()">→</button>
      </div>
    </div>
  `;

  const div = document.createElement('div');
  div.innerHTML = html;
  document.body.appendChild(div);

  // ── STATE ────────────────────────────────────────────────
  let vsOpen = false;
  let vsTyping = false;
  let vsMsgs = [];
  let vsGreeted = false;

  // ── TOGGLE ───────────────────────────────────────────────
  window.vsToggle = function() {
    vsOpen = !vsOpen;
    document.getElementById('vs-chat-panel').classList.toggle('vs-open', vsOpen);
    document.getElementById('vs-chat-icon').textContent = vsOpen ? '✕' : '⬡';
    document.getElementById('vs-chat-notif').style.display = vsOpen ? 'none' : 'block';
    if (vsOpen) {
      if (!vsGreeted) { vsGreeted = true; vsAddMsg('ai', 'Hi! I\'m VeriSigil\'s compliance assistant. Ask me anything about EU AI Act requirements for your AI agent.'); }
      setTimeout(() => document.getElementById('vs-inp').focus(), 100);
    }
  };

  // ── QUICK PROMPT ─────────────────────────────────────────
  window.vsQuick = function(text) {
    document.getElementById('vs-inp').value = text;
    vsSend();
  };

  // ── SEND ─────────────────────────────────────────────────
  window.vsSend = async function() {
    const inp = document.getElementById('vs-inp');
    const text = inp.value.trim();
    if (!text || vsTyping) return;
    inp.value = '';
    vsAddMsg('user', text);
    vsMsgs.push({ role: 'user', content: text });
    await vsGetReply();
  };

  // ── ADD MESSAGE ──────────────────────────────────────────
  function vsAddMsg(role, content, isHTML) {
    const container = document.getElementById('vs-msgs');
    const div = document.createElement('div');
    div.className = `vs-msg vs-${role}`;
    const av = document.createElement('div');
    av.className = 'vs-msg-av';
    av.textContent = role === 'ai' ? '⬡' : '👤';
    const bubble = document.createElement('div');
    bubble.className = 'vs-bubble';
    if (isHTML) bubble.innerHTML = content;
    else bubble.textContent = content;
    div.appendChild(av);
    div.appendChild(bubble);
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  }

  // ── TYPING ───────────────────────────────────────────────
  function vsShowTyping() {
    const container = document.getElementById('vs-msgs');
    const div = document.createElement('div');
    div.className = 'vs-msg vs-ai'; div.id = 'vs-typing';
    const av = document.createElement('div');
    av.className = 'vs-msg-av'; av.textContent = '⬡';
    const bubble = document.createElement('div');
    bubble.className = 'vs-bubble vs-typing';
    bubble.innerHTML = '<span></span><span></span><span></span>';
    div.appendChild(av); div.appendChild(bubble);
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  }
  function vsHideTyping() {
    const el = document.getElementById('vs-typing');
    if (el) el.remove();
  }

  // ── GET AI REPLY ─────────────────────────────────────────
  async function vsGetReply() {
    vsTyping = true;
    document.getElementById('vs-send').disabled = true;
    vsShowTyping();
    try {
      const res = await fetch(EDGE_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: vsMsgs })
      });
      const data = await res.json();
      const reply = data.reply || "I'm having trouble connecting. Email raheem@verisigilai.com for help.";
      vsHideTyping();
      vsMsgs.push({ role: 'assistant', content: reply });
      const hasCTA = /sprint|complian|499|get started/i.test(reply);
      if (hasCTA) {
        vsAddMsg('ai', reply + `<br><a href="https://verisigilai.com/eu-ai-act-sprint.html" class="vs-cta-btn" target="_blank">🚀 $499 Sprint →</a>`, true);
      } else {
        vsAddMsg('ai', reply);
      }
    } catch(e) {
      vsHideTyping();
      vsAddMsg('ai', "I'm having trouble connecting right now. Email raheem@verisigilai.com for compliance help.");
    }
    vsTyping = false;
    document.getElementById('vs-send').disabled = false;
  }

})();
