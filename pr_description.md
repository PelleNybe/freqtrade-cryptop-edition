Title: "🧪 Add test for rapidjson.JSONDecodeError in json_to_dataframe"
Description:
* 🎯 **What:** The `json_to_dataframe` function in `freqtrade/misc.py` attempts to use `rapidjson.loads`, and falls back to `pd.read_json` if a `ValueError`, `KeyError`, or `rapidjson.JSONDecodeError` is raised. However, the `JSONDecodeError` case was not covered by any tests.
* 📊 **Coverage:** A new test `test_json_to_dataframe_jsondecodeerror` has been added to `tests/test_misc.py`. This test uses `mocker` to force `rapidjson.loads` to raise `rapidjson.JSONDecodeError`, and verifies that the `json_to_dataframe` function successfully falls back to `pd.read_json` and returns the expected DataFrame.
* ✨ **Result:** The fallback behavior in `json_to_dataframe` when encountering a `rapidjson.JSONDecodeError` is now fully tested, preventing regressions in future updates and ensuring robust JSON deserialization.
