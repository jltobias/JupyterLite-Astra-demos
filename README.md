# JupyterLite Astra Demos

Browser-executable Python notebooks inspired by selected cases from [magiccreator-ai/awesome-gpt-6-astra](https://github.com/magiccreator-ai/awesome-gpt-6-astra).

> **Scope and attribution.** These notebooks are original educational reinterpretations written for this repository. They do **not** reproduce the creators' source code, prompts, assets, or benchmark results. The upstream Awesome GPT-6 Astra repository describes itself as a community case directory and notes that listed projects have not necessarily been independently reproduced or tested.

## Live sites

- **JupyterBook:** https://jltobias.github.io/JupyterLite-Astra-demos/
- **JupyterLite Lab:** https://jltobias.github.io/JupyterLite-Astra-demos/lite/lab/index.html

## Demos

| Notebook | Inspiration | Run in JupyterLite | Source citation |
|---|---|---|---|
| Aquarium motion model | Reference-Image Aquarium Game | [Open notebook](https://jltobias.github.io/JupyterLite-Astra-demos/lite/lab/index.html?path=01_aquarium_motion.ipynb) | Tim Jayas, [original post](https://x.com/TimJayas/status/2095611134992945385); [Awesome Astra entry](https://github.com/magiccreator-ai/awesome-gpt-6-astra#reference-image-aquarium-game) |
| Robot duel dynamics | Universe Duel | [Open notebook](https://jltobias.github.io/JupyterLite-Astra-demos/lite/lab/index.html?path=02_robot_duel.ipynb) | ハヤシモン, [original post](https://x.com/hayashimon1/status/2096255665778069957); [creator live demo](https://universe-duel.vercel.app); [Awesome Astra entry](https://github.com/magiccreator-ai/awesome-gpt-6-astra#universe-duel) |
| Procedural train assembly | Procedural Train Assemblies | [Open notebook](https://jltobias.github.io/JupyterLite-Astra-demos/lite/lab/index.html?path=03_procedural_train.ipynb) | Tom Krcha, [original post](https://x.com/tomkrcha/status/2096082580554777041); [Awesome Astra entry](https://github.com/magiccreator-ai/awesome-gpt-6-astra#procedural-train-assemblies) |
| Glass drying model | Glass-Drying Physics Simulation | [Open notebook](https://jltobias.github.io/JupyterLite-Astra-demos/lite/lab/index.html?path=04_glass_drying.ipynb) | Barron Roth, [original post](https://x.com/iamBarronRoth/status/2096407730030530762); [Awesome Astra entry](https://github.com/magiccreator-ai/awesome-gpt-6-astra#glass-drying-physics-simulation) |
| Model railroad scheduler | Interactive Model Railroad | [Open notebook](https://jltobias.github.io/JupyterLite-Astra-demos/lite/lab/index.html?path=05_model_railroad.ipynb) | Probably Nick, [original post](https://x.com/nickfromlater/status/2097355845524726084); [creator live demo](https://alder-valley-rail-atelier.nickfromlater.chatgpt.site/); [Awesome Astra entry](https://github.com/magiccreator-ai/awesome-gpt-6-astra#interactive-model-railroad) |

## What the notebooks demonstrate

Each notebook uses small, transparent mathematical models that run fully in the browser with the Pyodide kernel. The goal is to explore the *idea* behind each cited demo with reproducible Python: motion, state updates, procedural geometry, first-order drying dynamics, and discrete-event scheduling.

## Build locally

```bash
python -m pip install -r requirements.txt
BASE_URL=/JupyterLite-Astra-demos jupyter book build --html
jupyter lite build --contents content/notebooks --output-dir _build/html/lite
```

The GitHub Actions workflow publishes the JupyterBook at the Pages root and JupyterLite beneath `/lite/`.

## Sources

Primary inspiration directory: **MagicCreator AI, “Awesome GPT-6 Astra Demos,”** https://github.com/magiccreator-ai/awesome-gpt-6-astra (accessed September 11, 2026). Individual creator citations are listed in the table above and repeated inside each notebook.
