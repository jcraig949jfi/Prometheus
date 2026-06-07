def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests that run the real ~55s battery pipeline")
