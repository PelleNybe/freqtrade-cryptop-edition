import re


with open("freqtrade/rpc/api_server/api_v1.py") as f:
    content = f.read()

# Modify /ping function
new_ping_logic = """
@router_public.get("/ping", response_model=Ping, tags=["Info"])
def ping():
    \"\"\"Advanced ping with DB health check\"\"\"
    try:
        from freqtrade.persistence import Trade
        from sqlalchemy import text
        # Simple DB check
        Trade.session.execute(text("SELECT 1"))
        return {"status": "pong"}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Database connection failed")
"""

content = re.sub(
    r'@router_public.get\("/ping", response_model=Ping, tags=\["Info"\]\)\ndef ping\(\):\n    """simple ping"""\n    return \{"status": "pong"\}',
    new_ping_logic.strip(),
    content,
    flags=re.DOTALL,
)

with open("freqtrade/rpc/api_server/api_v1.py", "w") as f:
    f.write(content)
