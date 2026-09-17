import re

with open("freqtrade/persistence/models.py", "r") as f:
    content = f.read()

import_patch = """from sqlalchemy import create_engine, inspect, event
from sqlalchemy.engine import Engine"""

content = re.sub(r'from sqlalchemy import create_engine, inspect', import_patch, content)

engine_patch = """    try:
        engine = create_engine(db_url, future=True, **kwargs)

        # EDGE OPTIMIZATION: SQLite NVMe PRAGMA Tuning
        if db_url.startswith("sqlite"):
            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.close()

    except NoSuchModuleError:"""

content = re.sub(
    r'    try:\n        engine = create_engine\(db_url, future=True, \*\*kwargs\)\n    except NoSuchModuleError:',
    engine_patch,
    content
)

with open("freqtrade/persistence/models.py", "w") as f:
    f.write(content)
