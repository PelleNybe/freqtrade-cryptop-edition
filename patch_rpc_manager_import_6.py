import re

with open('freqtrade/rpc/rpc_manager.py', 'r') as f:
    content = f.read()

import_patch = """from freqtrade.rpc import RPC, RPCHandler
from freqtrade.rpc.rpc_types import RPCSendMsg
from freqtrade.rpc.zk_proof import ZKTradeProver"""

content = re.sub(r'from freqtrade\.rpc import RPC, RPCHandler\nfrom freqtrade\.rpc\.rpc_types import RPCSendMsg', import_patch, content)

with open('freqtrade/rpc/rpc_manager.py', 'w') as f:
    f.write(content)

with open('freqtrade/rpc/zk_proof.py', 'r') as f:
    content = f.read()

content = content.replace("with open(self.secret_key_path, \"w\") as f:", "with self.secret_key_path.open(\"w\") as f:")
content = content.replace("with open(self.secret_key_path) as f:", "with self.secret_key_path.open() as f:")

with open('freqtrade/rpc/zk_proof.py', 'w') as f:
    f.write(content)
