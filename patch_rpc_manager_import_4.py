import re

with open('freqtrade/rpc/rpc_manager.py', 'r') as f:
    content = f.read()

import_patch = """from freqtrade.rpc.rpc import RPC, RPCHandler
from freqtrade.rpc.rpc_types import RPCSendMsg
from freqtrade.rpc.zk_proof import ZKTradeProver"""

content = re.sub(r'from freqtrade\.rpc\.rpc import RPC, RPCHandler\nfrom freqtrade\.rpc\.rpc_types import RPCSendMsg', import_patch, content)

with open('freqtrade/rpc/rpc_manager.py', 'w') as f:
    f.write(content)
