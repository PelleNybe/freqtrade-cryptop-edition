import re

with open("freqtrade/strategy/interface.py", "r") as f:
    content = f.read()

# Add import for profile_execution
content = re.sub(
    r'from freqtrade\.data\.dataprovider import DataProvider',
    'from freqtrade.data.dataprovider import DataProvider\nfrom freqtrade.utils.profiler import profile_execution',
    content
)

# Add decorators
content = re.sub(
    r'    def advise_indicators\(self, dataframe: DataFrame, metadata: dict\) -> DataFrame:',
    '    @profile_execution\n    def advise_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:',
    content
)
content = re.sub(
    r'    def advise_entry\(self, dataframe: DataFrame, metadata: dict\) -> DataFrame:',
    '    @profile_execution\n    def advise_entry(self, dataframe: DataFrame, metadata: dict) -> DataFrame:',
    content
)
content = re.sub(
    r'    def advise_exit\(self, dataframe: DataFrame, metadata: dict\) -> DataFrame:',
    '    @profile_execution\n    def advise_exit(self, dataframe: DataFrame, metadata: dict) -> DataFrame:',
    content
)

with open("freqtrade/strategy/interface.py", "w") as f:
    f.write(content)
