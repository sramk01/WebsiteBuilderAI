"""
env_loader.py
--------------
Loads a .env file (if present, next to this file) into environment
variables at startup -- so ANTHROPIC_API_KEY (and anything else) can
be set once in a file alongside the code instead of relying on the
OS's environment variable system (which on Windows requires closing
and reopening every terminal/IDE for `setx` changes to be picked up).

Safe to import even if python-dotenv isn't installed, or if no .env
file exists -- silently no-ops in either case, so nothing breaks for
people who prefer setting a real OS environment variable instead.
"""

import os


def load_env_file():
    """Loads .env from this project's root directory into os.environ.
    Returns True if a .env file was found and loaded, False otherwise.
    Never overrides a variable that's already set in the real OS
    environment -- an actual `setx`/`export` always wins over .env."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return False

    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        return False

    return load_dotenv(dotenv_path=env_path, override=False)
