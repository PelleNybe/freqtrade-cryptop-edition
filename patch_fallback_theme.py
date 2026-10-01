with open("freqtrade/rpc/api_server/ui/fallback_file.html") as f:
    content = f.read()

styles = """
    .theme-switcher {
      display: flex;
      gap: 0.5rem;
      margin-left: 1rem;
    }
    .theme-btn {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      border: 2px solid var(--bg-glass-border);
      cursor: pointer;
      transition: transform 0.2s;
    }
    .theme-btn:hover {
      transform: scale(1.2);
    }
    .theme-neon { background: #ff2a85; }
    .theme-cyber { background: #00f0ff; }
    .theme-matrix { background: #00ff00; }
"""
content = content.replace("</style>", styles + "</style>")

# Add UI Control
ui_control = """
        <a href="https://github.com/freqtrade/freqtrade" target="_blank" rel="noopener">GitHub <svg class="external-icon" viewBox="0 0 24 24"><path d="M14,3V5H17.59L7.76,14.83L9.17,16.24L19,6.41V10H21V3M19,19H5V5H12V3H5C3.89,3 3,3.9 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V12H19V19Z" /></svg></a>
        <div class="theme-switcher">
          <button class="theme-btn theme-neon" onclick="setTheme('#ff2a85', '#8a2be2')" aria-label="Neon Theme"></button>
          <button class="theme-btn theme-cyber" onclick="setTheme('#00f0ff', '#8a2be2')" aria-label="Cyber Theme"></button>
          <button class="theme-btn theme-matrix" onclick="setTheme('#00ff00', '#004400')" aria-label="Matrix Theme"></button>
        </div>
"""
content = content.replace(
    '<a href="https://github.com/freqtrade/freqtrade" target="_blank" rel="noopener">GitHub <svg class="external-icon" viewBox="0 0 24 24"><path d="M14,3V5H17.59L7.76,14.83L9.17,16.24L19,6.41V10H21V3M19,19H5V5H12V3H5C3.89,3 3,3.9 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V12H19V19Z" /></svg></a>',
    ui_control,
)

# Add JS logic
js = """
    function setTheme(accent1, accent3) {
      document.documentElement.style.setProperty('--accent-1', accent1);
      document.documentElement.style.setProperty('--accent-3', accent3);
      if(accent1 === '#00ff00') {
         document.documentElement.style.setProperty('--accent-2', '#aaff00');
      } else if (accent1 === '#00f0ff') {
         document.documentElement.style.setProperty('--accent-2', '#0088ff');
      } else {
         document.documentElement.style.setProperty('--accent-2', '#00f0ff');
      }
    }
"""
content = content.replace("</script>", js + "\n</script>")


with open("freqtrade/rpc/api_server/ui/fallback_file.html", "w") as f:
    f.write(content)
