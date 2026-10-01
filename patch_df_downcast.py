import re


with open("freqtrade/data/converter/converter.py") as f:
    content = f.read()

new_logic = """def reduce_dataframe_footprint(df: DataFrame) -> DataFrame:
    \"\"\"
    Ensure all values are float32/int32 in the incoming dataframe.
    Uses pd.to_numeric downcasting for safer and more aggressive memory reduction.
    \"\"\"
    logger.debug(
        f"Memory usage of dataframe before downcast: {df.memory_usage().sum() / 1024**2:.2f} MB"
    )

    for column in df.columns:
        if column == "date":
            continue
        col_type = df[column].dtype
        if col_type == np.float64:
            df[column] = pd.to_numeric(df[column], downcast='float')
        elif col_type == np.int64:
            df[column] = pd.to_numeric(df[column], downcast='integer')

    logger.debug(f"Memory usage after downcast: {df.memory_usage().sum() / 1024**2:.2f} MB")
    return df"""

content = re.sub(
    r"def reduce_dataframe_footprint\(df: DataFrame\) -> DataFrame:.*?return df",
    new_logic,
    content,
    flags=re.DOTALL,
)

with open("freqtrade/data/converter/converter.py", "w") as f:
    f.write(content)
