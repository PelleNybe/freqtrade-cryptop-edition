import re

with open("freqtrade/optimize/hyperopt/hyperopt_optimizer.py", "r") as f:
    content = f.read()

import_patch = """import logging
import sys
import warnings
from datetime import datetime
from multiprocessing import Manager
from pathlib import Path
from typing import Any
import os

import optuna
from joblib import delayed, dump, load, wrap_non_picklable_objects"""

content = re.sub(
    r'import logging\nimport sys\nimport warnings\nfrom datetime import datetime\nfrom multiprocessing import Manager\nfrom pathlib import Path\nfrom typing import Any\n\nimport optuna\nfrom joblib import delayed, dump, load, wrap_non_picklable_objects',
    import_patch,
    content
)

study_patch = """        logger.info(f"Using optuna sampler {o_sampler}.")

        # EDGE OPTIMIZATION: Checkpoints for Resumable Hyperopt to NVMe
        if self.config.get("hyperopt_resume", False):
            storage_path = Path(self.config.get("user_data_dir", "user_data")) / "hyperopt_checkpoints"
            storage_path.mkdir(parents=True, exist_ok=True)
            db_url = f"sqlite:///{storage_path}/hyperopt_study.sqlite3"
            logger.info(f"[EDGE OPTIMIZATION] Resuming/Saving Optuna study to NVMe: {db_url}")
            return optuna.create_study(
                study_name="freqtrade_hyperopt",
                storage=db_url,
                load_if_exists=True,
                sampler=sampler,
                direction="minimize"
            )
        else:
            return optuna.create_study(sampler=sampler, direction="minimize")"""

content = re.sub(
    r'        logger\.info\(f"Using optuna sampler \{o_sampler\}\."\)\n        return optuna\.create_study\(sampler=sampler, direction="minimize"\)',
    study_patch,
    content
)

with open("freqtrade/optimize/hyperopt/hyperopt_optimizer.py", "w") as f:
    f.write(content)
