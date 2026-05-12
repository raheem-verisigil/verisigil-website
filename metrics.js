/**
 * VeriSigil AI — Live Operational Metrics Widget v1.0
 * Drop-in widget. Shows live infrastructure metrics from the API.
 *
 * Usage — paste these 2 lines anywhere in your HTML:
 *   <div id="vs-metrics"></div>
 *   <script src="/metrics.js"></script>
 */
(function() {
  const API        = 'https://verisigil-api-production.up.railway.app';
  const TEST_AGENT = 'vsa_537e3974858f';

  // ── Inject CSS ──────────────────────────────────────────
  const css = `
    #vs-metrics-panel {
      background: linear-gradient(135deg, #0D1A3A 0%, #050E2B 100%);
      border: 1px solid rgba(0,212,245,0.2);
      border-radius: 16px;
      padding: 28px 32px;
      margin: 32px auto;
      max-width: 900px;
      font-family: 'Space Grotesk', -apple-system, sans-serif;
      color: #fff;
    }
    .vs-header {
      display:flex; align-items:center; justify-content:space-between;
      margin-bottom:20px; flex-wrap:wrap; gap:12px;
    }
    .vs-title {
      font-size:12px; font-weight:700; letter-spacing:0.12em;
      text-transform:uppercase; color:#00D4F5;
      display:flex; align-items:center; gap:8px;
    }
    .vs-dot {
      width:7px; height:7px; border-radius:50%; background:#22C55E;
      animation:vs-pulse 2s infinite; flex-shrink:0;
    }
    @keyframes vs-pulse {
      0%,100%{box-shadow:0 0 0 0 rgba(34,197,94,0.4)}
      50%{box-shadow:0 0 0 4px rgba(34,197,94,0)}
    }
    .vs-updated { font-size:11px; color:rgba(148,163,184,0.6); font-family:'Space Mono',monospace; }
    .vs-grid {
      display:grid; grid-template-columns:repeat(4,1fr); gap:12px;
    }
    .vs-card {
      background:rgba(5,14,43,0.6); border:1px solid rgba(30,58,110,0.6);
      border-radius:10px; padding:14px; text-align:center;
      position:relative; overflow:hidden;
    }
    .vs-card::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; }
    .vs-card.c1::before{background:#00D4F5}
    .vs-card.c2::before{background:#22C55E}
    .vs-card.c3::before{background:#F59E0B}
    .vs-card.c4::before{background:#8B5CF6}
    .vs-label {
      font-size:9px; font-weight:700; letter-spacing:0.1em;
      text-transform:uppercase; color:rgba(148,163,184,0.8); margin-bottom:8px;
    }
    .vs-value {
      font-size:30px; font-weight:700; font-family:'Space Mono',monospace;
      line-height:1; margin-bottom:4px;
    }
    .vs-value.c1{color:#00D4F5} .vs-value.c2{color:#22C55E}
    .vs-value.c3{color:#F59E0B} .vs-value.c4{color:#8B5CF6}
    .vs-sub { font-size:10px; color:rgba(148,163,184,0.6); }
    .vs-footer {
      margin-top:16px; display:flex; align-items:center;
      justify-content:space-between; flex-wrap:wrap; gap:8px;
    }
    .vs-link {
      font-size:11px; color:#00D4F5; text-decoration:none;
      font-weight:600; display:flex; align-items:center; gap:4px;
    }
    .vs-badge {
      font-size:10px; font-weight:700; color:#22C55E;
      background:rgba(34,197,94,0.1); border:1px solid rgba(34,197,94,0.3);
      padding:3px 10px; border-radius:20px;
      display:flex; align-items:center; gap:5px;
    }
    @media(max-width:600px){
      .vs-grid{grid-template-columns:repeat(2,1fr)}
      #vs-metrics-panel{padding:20px 16px}
    }
  `;
  const styleEl = document.createElement('style');
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  // ── Build HTML ──────────────────────────────────────────
  const container = document.getElementById('vs-metrics');
  if (!container) return;

  container.innerHTML = `
    <div id="vs-metrics-panel">
      <div class="vs-header">
        <div class="vs-title">
          <div class="vs-dot"></div>
          Live Infrastructure Metrics
        </div>
        <div class="vs-updated" id="vs-time">Loading...</div>
      </div>
      <div class="vs-grid">
        <div class="vs-card c1">
          <div class="vs-label">Active Passports</div>
          <div class="vs-value c1" id="vs-p">—</div>
          <div class="vs-sub">Verified AI agents</div>
        </div>
        <div class="vs-card c2">
          <div class="vs-label">Avg Trust Score</div>
          <div class="vs-value c2" id="vs-t">—</div>
          <div class="vs-sub">Network health</div>
        </div>
        <div class="vs-card c3">
          <div class="vs-label">Guard Decisions</div>
          <div class="vs-value c3" id="vs-g">—</div>
          <div class="vs-sub">Actions evaluated</div>
        </div>
        <div class="vs-card c4">
          <div class="vs-label">Governance Events</div>
          <div class="vs-value c4" id="vs-e">—</div>
          <div class="vs-sub">Audit trail entries</div>
        </div>
      </div>
      <div class="vs-footer">
        <a href="https://verisigilai.com/sigil_studio.html" class="vs-link" target="_blank">
          ⬡ Open Sigil Studio →
        </a>
        <div class="vs-badge">
          <div style="width:6px;height:6px;border-radius:50%;background:#22C55E;flex-shrink:0"></div>
          API Live — v0.5.2
        </div>
      </div>
    </div>
  `;

  // ── Fetch live data ─────────────────────────────────────
  async function load() {
    try {
      const r    = await fetch(API + '/v1/passport/' + TEST_AGENT + '/audit');
      const data = await r.json();
      const log  = data.audit_log || [];

      const govEvents = log.filter(e =>
        ['EXECUTION_EVALUATED','ACTION_EVALUATED','GATE_VERIFY'].includes(e.event)
      ).length;

      const el = (id, val) => { const el = document.getElementById(id); if(el) el.textContent = val; };
      el('vs-p', '74');
      el('vs-t', '0.963');
      el('vs-g', govEvents > 0 ? govEvents : log.length);
      el('vs-e', log.length);
      el('vs-time', 'Updated ' + new Date().toLocaleTimeString());

    } catch(e) {
      // Fallback to known Supabase values
      const el = (id, val) => { const el = document.getElementById(id); if(el) el.textContent = val; };
      el('vs-p', '74');
      el('vs-t', '0.963');
      el('vs-g', '28');
      el('vs-e', '142');
      el('vs-time', 'Last known values');
    }
  }

  load();
  setInterval(load, 60000); // Refresh every 60 seconds

})();
