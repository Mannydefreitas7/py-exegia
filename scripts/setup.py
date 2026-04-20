#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# ///
"""Set up the project: install deps, start Supabase + Docker services, open Studio."""

import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT / "src"

STUDIO_URL = "http://localhost:54323"
API_HEALTH_URL = "http://localhost:8000/health"


def run(args: list[str], *, cwd: Path = ROOT, label: str | None = None) -> bool:
    display = label or " ".join(args)
    print(f"\n  $ {display}")
    result = subprocess.run(args, cwd=cwd)
    if result.returncode != 0:
        print(f"  FAILED (exit {result.returncode})", file=sys.stderr)
        return False
    return True


def wait_for(url: str, timeout: int = 120, label: str = "") -> bool:
    print(f"  waiting for {label or url}", end="", flush=True)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(url, timeout=2)
            print(" ready")
            return True
        except Exception:
            print(".", end="", flush=True)
            time.sleep(2)
    print(" timed out", file=sys.stderr)
    return False


def main() -> None:
    print("Setting up Exegia API...\n")

    # 1. Install all workspace dependencies
    print("==> Installing dependencies")
    if not run(["uv", "sync"], label="uv sync"):
        sys.exit(1)

    # 2. Start local Supabase (runs from src/ so CLI finds src/supabase/config.toml)
    print("\n==> Starting Supabase (local)")
    if not run(["supabase", "start"], cwd=SRC, label="supabase start"):
        print("  warning: supabase start failed — is the Supabase CLI installed?",
              file=sys.stderr)

    # 3. Start Docker Compose services
    print("\n==> Starting Docker services")
    if not run(["docker", "compose", "up", "-d", "--build"]):
        sys.exit(1)

    # 4. Wait for the API to be healthy
    print("\n==> Waiting for services")
    wait_for(API_HEALTH_URL, timeout=120, label="API (http://localhost:8000)")

    # 5. Open Supabase Studio in the default browser
    print(f"\n==> Opening Supabase Studio at {STUDIO_URL}")
    webbrowser.open(STUDIO_URL)

    print("\nDone. Services running:")
    print(f"  API         http://localhost:8000")
    print(f"  GraphiQL    http://localhost:8000/graphql")
    print(f"  Studio      {STUDIO_URL}")
    print(f"  DB          localhost:54322")


if __name__ == "__main__":
    main()
