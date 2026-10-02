# Performance optimization

The requested optimization `if crypto_symbol in coingecko_mapping:` rather than `if crypto_symbol in coingecko_mapping.keys():` was already present in the codebase.
The file `freqtrade/rpc/fiat_convert.py` on line 91 already had `if crypto_symbol in coingecko_mapping:`.
Since the optimization is already present, no actual code modifications were made.
