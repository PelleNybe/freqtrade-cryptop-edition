import re

with open("freqtrade/data/converter/converter.py", "r") as f:
    content = f.read()

# Make reduce_dataframe_footprint more aggressive
new_func = """def reduce_dataframe_footprint(df: DataFrame) -> DataFrame:
    \"\"\"
    Ensure all values are float32 in the incoming dataframe.
    :param df: Dataframe to be converted to float/int 32s
    :return: Dataframe converted to float/int 32s
    \"\"\"

    logger.debug(f"Memory usage of dataframe before downcast: {df.memory_usage().sum() / 1024**2:.2f} MB")

    df_dtypes = df.dtypes
    for column, dtype in df_dtypes.items():
        if column == "date":
            continue
        if dtype == np.float64:
            df_dtypes[column] = np.float32
        elif dtype == np.int64:
            df_dtypes[column] = np.int32
    df = df.astype(df_dtypes)

    logger.debug(f"Memory usage after downcast: {df.memory_usage().sum() / 1024**2:.2f} MB")

    return df
"""

content = re.sub(r'def reduce_dataframe_footprint\(df: DataFrame\) -> DataFrame:.*?return df', new_func, content, flags=re.DOTALL)

with open("freqtrade/data/converter/converter.py", "w") as f:
    f.write(content)
