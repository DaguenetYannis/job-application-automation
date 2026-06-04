from __future__ import annotations

import sys

from src.cli import JobApplicationCLI


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else None

    if command == "new":
        JobApplicationCLI().new()
        return

    print("Usage: python main.py new")


if __name__ == "__main__":
    main()
