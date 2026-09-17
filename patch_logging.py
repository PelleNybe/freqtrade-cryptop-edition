import re

with open("freqtrade/loggers/__init__.py", "r") as f:
    content = f.read()

# Add json support to FT_LOGGING_CONFIG
json_config = """    "formatters": {
        "basic": {"format": "%(message)s"},
        "standard": {
            "format": LOGFORMAT,
        },
        "json": {
            "class": "freqtrade.loggers.json_formatter.JsonFormatter",
        },
    },"""

content = re.sub(r'    "formatters": \{\n        "basic": \{"format": "%\(message\)s"\},\n        "standard": \{\n            "format": LOGFORMAT,\n        \},\n    \},', json_config, content)

# Enable JSON logging if config['logformat'] == 'json'
setup_logging_func = """def setup_logging(config: Config) -> None:
    \"\"\"
    Process -v/--verbose, --logfile options
    \"\"\"
    verbosity = config["verbosity"]
    if os.environ.get("PYTEST_VERSION") is None or config.get("ft_tests_force_logging"):
        log_config = _create_log_config(config)
        _set_log_levels(
            log_config, verbosity, config.get("api_server", {}).get("verbosity", "info")
        )

        if config.get("logformat") == "json":
            for handler in log_config["handlers"].values():
                if handler.get("formatter") == "standard":
                    handler["formatter"] = "json"

        logging.config.dictConfig(log_config)"""

content = re.sub(r'def setup_logging\(config: Config\) -> None:\n    """\n    Process -v/--verbose, --logfile options\n    """\n    verbosity = config\["verbosity"\]\n    if os\.environ\.get\("PYTEST_VERSION"\) is None or config\.get\("ft_tests_force_logging"\):\n        log_config = _create_log_config\(config\)\n        _set_log_levels\(\n            log_config, verbosity, config\.get\("api_server", \{\}\)\.get\("verbosity", "info"\)\n        \)\n\n        logging\.config\.dictConfig\(log_config\)', setup_logging_func, content)

with open("freqtrade/loggers/__init__.py", "w") as f:
    f.write(content)
