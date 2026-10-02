"""Execute every notebook in an isolated temporary folder and keep visible outputs.

The lessons' GeoJSON export stays in the temporary working directory. On success,
copy executed notebooks back and save a representative PNG per lesson for the gallery.
"""
from pathlib import Path
import argparse
import base64
import os
import shutil
import tempfile
import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Execute without updating notebook outputs or previews')
    args = parser.parse_args()
    os.environ.setdefault('MPLBACKEND', 'module://matplotlib_inline.backend_inline')
    notebooks = sorted((ROOT / 'content/notebooks').glob('*.ipynb'))
    with tempfile.TemporaryDirectory(prefix='astra-notebooks-') as folder:
        shutil.copy(ROOT / 'content/notebooks/astra_utils.py', folder)
        shutil.copytree(ROOT / 'content/notebooks/data', Path(folder) / 'data')
        executed = []
        for path in notebooks:
            nb = nbformat.read(path, as_version=4)
            nbformat.validate(nb)
            NotebookClient(nb, timeout=180, kernel_name='python3', resources={'metadata': {'path': folder}}).execute()
            executed.append((path, nb))
            print(f'PASS {path.name}', flush=True)
        if not args.check:
            previews = ROOT / 'assets/previews'
            previews.mkdir(parents=True, exist_ok=True)
            for path, nb in executed:
                nbformat.write(nb, path)
                pngs = [output['data']['image/png'] for cell in nb.cells if cell.cell_type == 'code'
                        for output in cell.outputs if 'image/png' in output.get('data', {})]
                if pngs:
                    (previews / (path.stem + '.png')).write_bytes(base64.b64decode(pngs[0]))
    print(f'Executed {len(notebooks)} notebooks successfully.')


if __name__ == '__main__':
    main()
