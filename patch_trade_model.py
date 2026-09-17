import re

with open("freqtrade/persistence/trade_model.py", "r") as f:
    content = f.read()

batch_commit = """    @staticmethod
    def commit():
        # Added a check if batch_commit is active, if not, commit.
        if getattr(Trade.session, '_ft_batch_commit_active', False):
            Trade.session.flush()
        else:
            Trade.session.commit()
"""
content = re.sub(r'    @staticmethod\n    def commit\(\):\n        Trade\.session\.commit\(\)', batch_commit, content)

batch_cm = """from contextlib import contextmanager

@contextmanager
def batched_commit():
    \"\"\"
    Context manager to batch database commits.
    Useful for heavy I/O operations like backtesting or fast data ingestion on edge devices.
    \"\"\"
    session = Trade.session
    original_state = getattr(session, '_ft_batch_commit_active', False)
    session._ft_batch_commit_active = True
    try:
        yield
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session._ft_batch_commit_active = original_state
"""

# add batch_cm to the end of the file
content += "\n" + batch_cm

with open("freqtrade/persistence/trade_model.py", "w") as f:
    f.write(content)
