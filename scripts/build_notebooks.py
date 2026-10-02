"""Build reviewable notebooks from the percent-format lessons (no Jupytext needed)."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def convert(path):
    cells = []
    for match in re.finditer(r"^# %%([^\n]*)\n(.*?)(?=^# %%|\Z)", path.read_text(encoding="utf-8"), re.M | re.S):
        kind = "markdown" if "[markdown]" in match[1] else "code"
        source = match[2].strip("\n") + "\n"
        if kind == "markdown":
            source = "\n".join(line[2:] if line.startswith("# ") else line[1:] if line == "#" else line for line in source.splitlines()) + "\n"
        cell = {"cell_type": kind, "id": hashlib.sha256((path.stem + str(len(cells))).encode()).hexdigest()[:12], "metadata": {}, "source": source.splitlines(keepends=True)}
        if kind == "code":
            cell.update(execution_count=None, outputs=[])
        cells.append(cell)
    return {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python (Pyodide)", "language": "python", "name": "python"}, "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}


if __name__ == "__main__":
    for source in sorted((ROOT / "lessons").glob("*.py")):
        target = ROOT / "content/notebooks" / (source.stem + ".ipynb")
        generated = convert(source)
        if target.exists():
            existing = json.loads(target.read_text(encoding="utf-8"))
            cell_sources = lambda nb: [(c['cell_type'], ''.join(c['source'])) for c in nb['cells']]
            if cell_sources(existing) == cell_sources(generated):
                print(f'{target.name} (unchanged; outputs retained)')
                continue
        target.write_text(json.dumps(generated, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(target.name)
