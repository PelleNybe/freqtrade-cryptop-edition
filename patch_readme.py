import re


with open("README.md") as f:
    content = f.read()

features = """- **Enhanced Branding & User Experience**: Step into the "Magical Server" with a unique, vibrant theme and the "Crypto P" persona guiding you.
- **Interactive Setup**: The fallback UI page includes copy-paste commands with toast notifications and confetti effects to make installation easier and more fun.
- **Visual Improvements**:
  - Canvas-based interactive particle network background.
  - Interactive Theme Switcher (Neon, Cyber, Matrix).
  - Enhanced hover glows and custom scrollbars.
  - Live system resource statistics dashboard.
  - Simulated terminal typing animation.
- **Technical Improvements**:
  - Detailed `/sysinfo` endpoint exposing CPU, RAM, Uptime, and Version details.
  - Deep API Response Caching on heavy data endpoints (using a custom `@cached_response` decorator).
  - Advanced Auth Security with a strict 15-minute lockout policy against brute force attacks.
  - Active Database Health-checking in the `/ping` endpoint.
  - Aggressive and safe DataFrame memory downcasting optimizations in data processing.
"""

content = re.sub(
    r'- \*\*Enhanced Branding & User Experience\*\*: Step into the "Magical Server".*?- \*\*Interactive Setup\*\*: The fallback UI page includes copy-paste commands with toast notifications and confetti effects to make installation easier and more fun.',
    features.strip(),
    content,
    flags=re.DOTALL,
)

with open("README.md", "w") as f:
    f.write(content)
