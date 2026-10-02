"""Copy the standalone World Lab and README assets into the JupyterBook output."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
site = ROOT / '_build/html'
if not site.is_dir():
    raise SystemExit('Build JupyterBook before copying assets.')
for name in ['demos', 'assets']:
    shutil.copytree(ROOT / name, site / name, dirs_exist_ok=True)
(site / '.nojekyll').touch()
print('Copied World Lab, local Three.js, splash image and lesson previews.')
