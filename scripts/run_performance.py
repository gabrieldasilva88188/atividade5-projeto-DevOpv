"""Sobe a API real (waitress), executa o Locust em modo headless e encerra o servidor.

Uso: python scripts/run_performance.py
Variáveis opcionais: USERS, SPAWN_RATE, RUN_TIME, PORT, P95_MS, MAX_FAIL_RATIO, MIN_RPS
"""
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "reports" / "performance"
PORT = os.environ.get("PORT", "5055")
HOST = f"http://127.0.0.1:{PORT}"


def wait_for_server(timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{HOST}/health", timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "DB_PATH": str(Path(tmp) / "perf.db"), "PORT": PORT, "PYTHONPATH": str(ROOT)}
        server = subprocess.Popen([sys.executable, "-m", "app.server"], cwd=ROOT, env=env)
        try:
            if not wait_for_server():
                print("Servidor não respondeu em /health", file=sys.stderr)
                return 1
            cmd = [
                sys.executable, "-m", "locust",
                "-f", str(ROOT / "tests" / "performance" / "locustfile.py"),
                "--headless",
                "--host", HOST,
                "--users", os.environ.get("USERS", "20"),
                "--spawn-rate", os.environ.get("SPAWN_RATE", "5"),
                "--run-time", os.environ.get("RUN_TIME", "20s"),
                "--csv", str(REPORT_DIR / "locust"),
                "--html", str(REPORT_DIR / "report.html"),
                "--only-summary",
            ]
            return subprocess.call(cmd, cwd=ROOT, env=env)
        finally:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()


if __name__ == "__main__":
    sys.exit(main())
