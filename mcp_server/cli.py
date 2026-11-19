"""Console entry point ``cadapter-mcp`` (added by manydominos, 2026).

Runs the same server as ``python mcp_server/mcp_solidworks.py`` (stdio), from an
installed package. The signature index (``sw_api_signature`` and the by-ref typing
of ``sw_call``) is derived from the SolidWorks typelib registered on THIS machine
and is never shipped; it lives in ``CADAPTER_SIGNATURES`` (default
``%LOCALAPPDATA%\CADapter\api_signatures.json``) and is built here on the first
start when it is missing. SolidWorks does not need to be running for that, only
installed. A failed build is logged and the server starts anyway; only the two
signature-based features then report that the index is missing.

Nothing is ever written to stdout before the server runs: stdout is the MCP
stdio channel.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _default_index() -> Path:
    base = os.environ.get("LOCALAPPDATA") or str(Path.home())
    return Path(base) / "CADapter" / "api_signatures.json"


def _ensure_index() -> None:
    path = Path(os.environ.setdefault("CADAPTER_SIGNATURES", str(_default_index())))
    if path.is_file():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    builder = Path(__file__).with_name("build_api_signatures_typelib.py")
    print(f"CADapter: building the signature index at {path} ...", file=sys.stderr)
    result = subprocess.run(
        [sys.executable, str(builder), "--out", str(path)],
        stdout=sys.stderr, stderr=sys.stderr, stdin=subprocess.DEVNULL, check=False,
    )
    if result.returncode != 0 or not path.is_file():
        print(
            "CADapter: the signature index could not be built (is SolidWorks installed?). "
            "The server starts; sw_api_signature reports the missing index.",
            file=sys.stderr,
        )


def main() -> None:
    _ensure_index()
    from mcp_server import knowledge, mcp_solidworks

    knowledge.warmup()
    mcp_solidworks.mcp.run()


if __name__ == "__main__":
    main()
