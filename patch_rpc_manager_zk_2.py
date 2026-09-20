import re

with open('freqtrade/rpc/rpc_manager.py', 'r') as f:
    content = f.read()

send_msg_patch = """    def send_msg(self, msg: RPCSendMsg) -> None:
        \"\"\"
        Send given message to all registered rpc modules.
        A message consists of one or more key value pairs of strings.
        \"\"\"

        # Inject ZK Proofs for exit trades
        if msg.get("type") and msg.get("type").name == "EXIT" and getattr(self, "zk_prover", None) and self.zk_prover.enabled:
            trade = msg.get("trade")
            if trade:
                proof = self.zk_prover.generate_proof(trade)
                if proof:
                    msg["zk_proof"] = proof

        if msg.get("type") not in NO_ECHO_MESSAGES:
            logger.info("Sending rpc message: %s", msg)"""

content = re.sub(
    r'    def send_msg\(self, msg: RPCSendMsg\) -> None:.*?logger\.info\("Sending rpc message: %s", msg\)',
    send_msg_patch,
    content,
    flags=re.DOTALL
)

with open('freqtrade/rpc/rpc_manager.py', 'w') as f:
    f.write(content)
