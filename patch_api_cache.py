with open("freqtrade/rpc/api_server/deps.py") as f:
    content = f.read()

# Add a caching decorator
caching_code = """
import functools
from cachetools import TTLCache

def cached_response(ttl_seconds: int = 10):
    cache = TTLCache(maxsize=100, ttl=ttl_seconds)
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Try to build a cache key from args/kwargs
            key_parts = []
            for arg in args:
                if isinstance(arg, (str, int, float, bool)):
                    key_parts.append(str(arg))
            for k, v in sorted(kwargs.items()):
                 if isinstance(v, (str, int, float, bool)):
                    key_parts.append(f"{k}={v}")
            key = ":".join(key_parts)
            if not key:
                key = "default"

            if key in cache:
                return cache[key]
            result = func(*args, **kwargs)
            cache[key] = result
            return result
        return wrapper
    return decorator
"""

content = content + "\n" + caching_code

with open("freqtrade/rpc/api_server/deps.py", "w") as f:
    f.write(content)
