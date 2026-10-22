import os

# Test-only dummy value, not a deployed credential.
os.environ.setdefault("SECRET_KEY", "test-only-not-for-deployment")
