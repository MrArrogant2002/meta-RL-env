from __future__ import annotations

import os

import uvicorn

from src.api import app


def main() -> None:
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("server.app:app", host=host, port=port)


if __name__ == "__main__":
    main()
