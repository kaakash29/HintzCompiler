#!/usr/bin/env python3
"""Cache and extract the pinned Ubuntu SDK without modifying the host system."""
import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest = ROOT / "dev/llvm-packages.txt"
cache = ROOT / "tools/packages"
sdk = ROOT / "tools/llvm"
cache.mkdir(parents=True, exist_ok=True)
sdk.mkdir(parents=True, exist_ok=True)
stamp = sdk / ".packages.sha256"
fingerprint = hashlib.sha256(manifest.read_bytes()).hexdigest()


def metadata(path):
    result = subprocess.run(
        ["dpkg-deb", "-f", str(path), "Package", "Version", "Architecture"],
        check=True, text=True, capture_output=True,
    )
    return dict(line.split(": ", 1) for line in result.stdout.splitlines())


try:
    packages = {}
    for path in cache.glob("*.deb"):
        info = metadata(path)
        packages[(info["Package"], info["Version"], info["Architecture"])] = path
    selected = []
    for line in manifest.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        name, version = line.split("=", 1)
        key = (name, version, "amd64")
        if key not in packages:
            subprocess.run(["apt-get", "download", line], cwd=cache, check=True)
            for path in cache.glob(f"{name}_*.deb"):
                info = metadata(path)
                if (info["Package"], info["Version"], info["Architecture"]) == key:
                    packages[key] = path
            if key not in packages:
                raise RuntimeError(f"Downloaded package did not match {line}")
        selected.append(packages[key])
    if not stamp.exists() or stamp.read_text().strip() != fingerprint:
        # Only mark the SDK ready after every extraction completes successfully.
        for path in selected:
            subprocess.run(["dpkg-deb", "-x", str(path), str(sdk)], check=True)
        stamp.write_text(fingerprint + "\n")
    else:
        print("Reusing the extracted LLVM/MLIR SDK.", flush=True)
except (subprocess.CalledProcessError, RuntimeError) as exc:
    raise SystemExit(
        f"LLVM SDK setup failed: {exc}\n"
        "Check network access and Ubuntu package indexes (sudo apt-get update). "
        "If the pinned revision is unavailable, use --llvm-prefix with an installed "
        "LLVM/MLIR 19 SDK, or update dev/llvm-packages.txt and rerun the test gates."
    ) from exc
