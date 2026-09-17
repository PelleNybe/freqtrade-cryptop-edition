import re

with open("freqtrade/persistence/models.py", "r") as f:
    content = f.read()

# Make the session objects aware of batch commits
content = content.replace(
    'Trade.session = scoped_session(\n        sessionmaker(bind=engine, autoflush=False), scopefunc=get_request_or_thread_id\n    )',
    'Trade.session = scoped_session(\n        sessionmaker(bind=engine, autoflush=False), scopefunc=get_request_or_thread_id\n    )\n    Trade.session._ft_batch_commit_active = False'
)

with open("freqtrade/persistence/models.py", "w") as f:
    f.write(content)
