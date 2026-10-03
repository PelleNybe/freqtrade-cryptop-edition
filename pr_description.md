Title: "🧪 Add test for rapidjson.JSONDecodeError natively in json_to_dataframe"
Description:
* 🎯 **What:** The `json_to_dataframe` function in `freqtrade/misc.py` attempts to use `rapidjson.loads`, and falls back to `pd.read_json` if a `ValueError`, `KeyError`, or `rapidjson.JSONDecodeError` is raised. While there was a mock test, the behavior of passing an actual invalid JSON string was untested natively.
* 📊 **Coverage:** A new test `test_json_to_dataframe_invalid_json` has been added to `tests/test_misc.py`. This test passes an invalid JSON string which naturally triggers `rapidjson.JSONDecodeError` and verifies that it correctly falls back to `pd.read_json` (which raises ValueError).
* ✨ **Result:** The fallback behavior in `json_to_dataframe` when encountering a `rapidjson.JSONDecodeError` is now fully tested natively without mocks, further guaranteeing correctness during invalid responses.
