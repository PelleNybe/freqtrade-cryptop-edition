import re

with open("freqtrade/freqtradebot.py", "r") as f:
    content = f.read()

import_patch = """from freqtrade.data.dataprovider import DataProvider
from freqtrade.data.defillama import risk_guard"""

content = re.sub(r'from freqtrade\.data\.dataprovider import DataProvider', import_patch, content)

startup_patch = """    def startup(self) -> None:
        \"\"\"
        Called on startup and after reloading the bot - triggers notifications and
        performs startup tasks
        \"\"\"
        # EDGE OPTIMIZATION: Start DefiLlama On-Chain Risk Guard
        risk_guard.start()

        migrate_live_content(self.config, self.exchange)"""

content = re.sub(
    r'    def startup\(self\) -> None:\n        """\n        Called on startup and after reloading the bot - triggers notifications and\n        performs startup tasks\n        """\n        migrate_live_content\(self\.config, self\.exchange\)',
    startup_patch,
    content
)

cleanup_patch = """    def cleanup(self) -> None:
        \"\"\"
        Cleanup pending resources on an already stopped bot
        :return: None
        \"\"\"
        logger.info("Cleaning up modules ...")

        # Stop DefiLlama worker
        risk_guard.stop()

        try:"""

content = re.sub(
    r'    def cleanup\(self\) -> None:\n        """\n        Cleanup pending resources on an already stopped bot\n        :return: None\n        """\n        logger\.info\("Cleaning up modules \.\.\."\)\n        try:',
    cleanup_patch,
    content
)

with open("freqtrade/freqtradebot.py", "w") as f:
    f.write(content)
