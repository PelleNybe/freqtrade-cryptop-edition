import re

with open('freqtrade/rpc/rpc_manager.py', 'r') as f:
    content = f.read()

import_patch = """from freqtrade.rpc.rpc import RPC, RPCHandler
from freqtrade.rpc.rpc_types import RPCSendMsg
from freqtrade.rpc.zk_proof import ZKTradeProver
"""
content = content.replace("from freqtrade.rpc.rpc import RPC, RPCHandler\nfrom freqtrade.rpc.rpc_types import RPCSendMsg\n", import_patch)

init_patch = """        # Enable MQTT
        if config.get("mqtt", {}).get("enabled", False):
            logger.info("Enabling rpc.mqtt ...")
            from freqtrade.rpc.mqtt import MQTT

            self.registered_modules.append(MQTT(self._rpc, config))

        # Init ZK Prover
        self.zk_prover = ZKTradeProver(config)"""

# In Crypto P Edition, MQTT might already be initialized here, but let's just add the zk_prover.
# Instead of replacing MQTT, let's inject after registered_modules = []
init_zk = """        self.registered_modules: list[RPCHandler] = []
        self._rpc = RPC(freqtrade)

        # Init ZK Prover for trade proofs
        self.zk_prover = ZKTradeProver(freqtrade.config)"""

content = content.replace("        self.registered_modules: list[RPCHandler] = []\n        self._rpc = RPC(freqtrade)", init_zk)


# Patch send_msg to inject ZK Proofs for EXIT trades
send_msg_patch = """    def send_msg(self, msg: dict[str, Any]) -> None:
        \"\"\"
        Send given message to all registered rpc modules.
        A message consists of one or more key value pairs of strings.
        e.g.:
        {'status': 'stopping bot'}
        \"\"\"

        # Inject ZK Proofs for exit trades
        if msg.get("type") and msg.get("type").name == "EXIT" and self.zk_prover.enabled:
            trade = msg.get("trade")
            if trade:
                proof = self.zk_prover.generate_proof(trade)
                if proof:
                    msg["zk_proof"] = proof

        logger.info(f"Sending rpc message: {msg}")"""

content = re.sub(
    r'    def send_msg\(self, msg: dict\[str, Any\]\) -> None:\n.*?\n        logger\.info\(f"Sending rpc message: \{msg\}"\)',
    send_msg_patch,
    content,
    flags=re.DOTALL
)

with open('freqtrade/rpc/rpc_manager.py', 'w') as f:
    f.write(content)
