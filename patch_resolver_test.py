with open("freqtrade/resolvers/iresolver.py") as f:
    content = f.read()
# We don't need to patch iresolver. The test fails because stable_baselines3 is not installed, which is expected on edge environments.
