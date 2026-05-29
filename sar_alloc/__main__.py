"""
Package command-line entry.

This file allows the project to be started with:

    python -m sar_alloc

The actual command-line logic is kept in runner.py.
"""

from .runner import main


if __name__ == "__main__":
    main()