from __future__ import annotations

import json

from baseline.run_baseline import run_baseline


def main() -> None:
    print(json.dumps(run_baseline(), indent=2))


if __name__ == "__main__":
    main()
