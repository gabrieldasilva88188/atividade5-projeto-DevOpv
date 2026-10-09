"""Gera um resumo em Markdown (para o GITHUB_STEP_SUMMARY) a partir dos relatórios.

Uso:
  python scripts/summarize_results.py junit  reports/unit/junit.xml "Testes unitários"
  python scripts/summarize_results.py locust reports/performance/locust_stats.csv "Testes de performance"
"""
import csv
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def summarize_junit(path: Path, title: str) -> str:
    if not path.exists():
        return f"## {title}\n\nRelatório não encontrado: `{path}`\n"
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    tests = sum(int(s.get("tests", 0)) for s in suites)
    failures = sum(int(s.get("failures", 0)) for s in suites)
    errors = sum(int(s.get("errors", 0)) for s in suites)
    skipped = sum(int(s.get("skipped", 0)) for s in suites)
    time_s = sum(float(s.get("time", 0)) for s in suites)
    passed = tests - failures - errors - skipped
    status = "✅ Aprovado" if failures + errors == 0 else "❌ Falhou"
    lines = [
        f"## {title} — {status}",
        "",
        "| Total | Passaram | Falharam | Erros | Ignorados | Tempo |",
        "|---:|---:|---:|---:|---:|---:|",
        f"| {tests} | {passed} | {failures} | {errors} | {skipped} | {time_s:.2f}s |",
        "",
    ]
    bad = [
        (c.get("classname", ""), c.get("name", ""))
        for c in root.iter("testcase")
        if c.find("failure") is not None or c.find("error") is not None
    ]
    if bad:
        lines.append("**Testes com problema:**")
        lines += [f"- `{cls}::{name}`" for cls, name in bad]
        lines.append("")
    return "\n".join(lines)


def summarize_locust(path: Path, title: str) -> str:
    if not path.exists():
        return f"## {title}\n\nRelatório não encontrado: `{path}`\n"
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    lines = [
        f"## {title}",
        "",
        "| Endpoint | Requisições | Falhas | Média (ms) | P50 (ms) | P95 (ms) | P99 (ms) | Req/s |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        label = "**Total**" if r["Name"] == "Aggregated" else f"`{r['Name']}`"
        lines.append(
            f"| {label} | {r['Request Count']} | {r['Failure Count']} | "
            f"{float(r['Average Response Time']):.0f} | {r['50%']} | {r['95%']} | {r['99%']} | "
            f"{float(r['Requests/s']):.1f} |"
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    kind, file_path, title = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
    print(summarize_junit(file_path, title) if kind == "junit" else summarize_locust(file_path, title))
