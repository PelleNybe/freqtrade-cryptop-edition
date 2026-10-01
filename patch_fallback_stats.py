with open("freqtrade/rpc/api_server/ui/fallback_file.html") as f:
    content = f.read()

# Add styles for the stats
styles = """
    .sysinfo-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 1rem;
      margin-top: 1rem;
    }
    .stat-box {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--bg-glass-border);
      border-radius: 8px;
      padding: 0.8rem;
      text-align: center;
      transition: all 0.3s ease;
    }
    .stat-box:hover {
      background: rgba(255, 255, 255, 0.08);
      border-color: var(--accent-2);
      box-shadow: 0 0 15px rgba(0, 240, 255, 0.2);
    }
    .stat-value {
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--text-main);
      font-family: 'JetBrains Mono', monospace;
    }
    .stat-label {
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 1px;
    }
"""
content = content.replace("</style>", styles + "</style>")

# Add the UI Card
card = """
      <div class="card glass">
        <h3>📊 System Resources</h3>
        <p>Live metrics from the Crypto P core server.</p>
        <div class="sysinfo-grid" id="sysinfo-container">
          <div class="stat-box"><div class="stat-value" id="stat-cpu">--%</div><div class="stat-label">CPU</div></div>
          <div class="stat-box"><div class="stat-value" id="stat-ram">--%</div><div class="stat-label">Memory</div></div>
          <div class="stat-box"><div class="stat-value" id="stat-up">--</div><div class="stat-label">Uptime</div></div>
          <div class="stat-box"><div class="stat-value" id="stat-ver">--</div><div class="stat-label">Freqtrade Version</div></div>
        </div>
      </div>
"""
content = content.replace(
    '<div class="terminal-section">', card + '\n      <div class="terminal-section">'
)

# Add JS logic
js = """
    async function fetchSysInfo() {
      try {
        const res = await fetch('/api/v1/sysinfo');
        if (res.ok) {
          const data = await res.json();
          const cpuAvg = data.cpu_pct.reduce((a, b) => a + b, 0) / data.cpu_pct.length;
          document.getElementById('stat-cpu').innerText = cpuAvg.toFixed(1) + '%';
          document.getElementById('stat-ram').innerText = data.ram_pct.toFixed(1) + '%';

          let up = data.uptime_seconds;
          let upStr = '--';
          if (up) {
             const d = Math.floor(up / 86400);
             const h = Math.floor((up % 86400) / 3600);
             const m = Math.floor((up % 3600) / 60);
             upStr = d > 0 ? `${d}d ${h}h` : `${h}h ${m}m`;
          }
          document.getElementById('stat-up').innerText = upStr;
          document.getElementById('stat-ver').innerText = data.freqtrade_version || '--';
        }
      } catch(e) {
        // fail silently
      }
    }

    // Initial fetch and interval
    fetchSysInfo();
    setInterval(fetchSysInfo, 5000);
"""
content = content.replace(
    "document.getElementById('refresh-btn').addEventListener('click', () => checkStatus(true));",
    "document.getElementById('refresh-btn').addEventListener('click', () => checkStatus(true));\n"
    + js,
)


with open("freqtrade/rpc/api_server/ui/fallback_file.html", "w") as f:
    f.write(content)
