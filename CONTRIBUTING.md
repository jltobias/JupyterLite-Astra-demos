# Maintain the learning gallery

Edit the percent-format Python sources in `lessons/`, then run:

```bash
python scripts/build_notebooks.py
python scripts/execute_notebooks.py
python -m pytest -q
```

Commit the source, generated notebook and generated preview together. Do not edit a notebook's
cells directly: regeneration would overwrite that change. `astra_utils.py` contains presentation
helpers; keep scientific formulas visible in lessons. Seeds, modest arrays and no network data
dependencies keep execution reproducible in browser Python.

For a new lesson, include a learning objective, prediction question, linked visual representations,
parameter experiment, limitations and a meaningful numerical check. State units and coordinate
conventions. Separate sampled data, fitted values and invented geometry. Credit the creator and
catalog entry; a teaching adaptation does not reproduce a creator's code or verify general capability.

Add the notebook to `myst.yml`, the README gallery and a learning path. Generate its preview from
actual code. Keep animations paused by default, support keyboards and retain useful static plots.
Link to the appropriate World Lab scene when available.

For World Lab changes, edit `demos/worlds.js`, `worlds.css` and `index.html`. Build the site, run
`python scripts/check_browser.py --root _build/html`, inspect desktop and narrow screenshots, and
exercise parameters at both ends of their ranges. Keep vendor dependencies local and licensed.

CI runs notebook execution, mathematical edge cases, the JupyterBook/JupyterLite builds and browser
scene checks. Pull requests never deploy. A push to `main` publishes the book at the project root,
JupyterLite at `/lite/` and the World Lab at `/demos/`.

`python scripts/check_jupyterlite.py --root _build/html` also executes representative notebooks
in the real browser kernel. Keep NumPy and Matplotlib imports in each notebook's first code cell:
Pyodide's package scan does not follow imports inside the local presentation helper.

JupyterLite persists files in browser storage. A returning reader may have an older saved notebook;
download important edits before restoring a fresh copy. If local files cannot be imported, check
that service workers are allowed, use HTTPS or localhost, and see the JupyterLite filesystem
documentation linked in the README.
