import re

with open('freqtrade/rpc/rpc_manager.py', 'r') as f:
    content = f.read()

import_patch = """from freqtrade.rpc.rpc import RPC, RPCHandler
from freqtrade.rpc.rpc_types import RPCSendMsg
from freqtrade.rpc.zk_proof import ZKTradeProver
"""

content = content.replace("from freqtrade.rpc.rpc import RPC, RPCHandler\nfrom freqtrade.rpc.rpc_types import RPCSendMsg\n", import_patch)

with open('freqtrade/rpc/rpc_manager.py', 'w') as f:
    f.write(content)
