⚡ Performance Optimization: Unnecessary `.keys()` lookup removed

💡 **What:** The requested optimization to remove the `.keys()` call in dictionary membership checks (`if crypto_symbol in coingecko_mapping:` instead of `if crypto_symbol in coingecko_mapping.keys():`) was analyzed.

🎯 **Why:** Using `.keys()` creates an unnecessary list/view of all dictionary keys before checking membership, whereas checking directly against the dictionary uses its O(1) hash table lookup directly.

📊 **Measured Improvement:** No performance tests were implemented because the optimization was already present in the codebase. Upon inspecting `freqtrade/rpc/fiat_convert.py` at line 91, the code is already written as `if crypto_symbol in coingecko_mapping:`. Thus, there is no measurable performance difference to show, as the codebase is already optimized in this regard. No code modifications were made.
