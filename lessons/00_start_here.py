# %% [markdown]
# # Start here: from a map to a world
#
# **An interactive field guide to spatial thinking.** These original experiments extend ideas in
# [Awesome GPT-6 Astra](https://github.com/magiccreator-ai/awesome-gpt-6-astra).
# They explore AI-assisted creation through inspectable code, not a benchmark of model capability.
#
# **Run:** select the Python (Pyodide) kernel, then **Run → Run All Cells**. First startup downloads
# the runtime and packages. Allow the kernel to finish loading. No API key, account, map service,
# or Python installation is needed. Keep `astra_utils.py` beside these notebooks.
#
# **Observe → predict → change → explain.** Start with a picture. Predict what changing one
# parameter will do. Run the experiment, then explain any mismatch in your own words.
# Paused animation players can be scrubbed with the keyboard; all lessons also have static plots.
#
# | Learning path | Notebooks | What to look for |
# |---|---|---|
# | Motion and systems | 01–05 | Paths, state, components, rates, conflicts |
# | Spatial thinking | 06–09 | Projection, relief, coordinates, travel cost |
# | World creation | 10–12, 15 | Flow, geometry repair, voxels, light |
# | Patterns and uncertainty | 13–14 | Chaos, interpolation, evidence |
#
# [Open the interactive 3D World Lab](https://jltobias.github.io/JupyterLite-Astra-demos/demos/)
# to orbit six scenes without starting a notebook. Scenes are synthetic and use local assets.
# %%
import numpy as np
import matplotlib.pyplot as plt
from astra_utils import style
style()
x = np.linspace(-3, 3, 50)
X, Y = np.meshgrid(x, x)
Z = 2 * np.exp(-((X + .8)**2 + Y**2)) + np.exp(-((X - 1.3)**2 + (Y - .6)**2))
fig = plt.figure(figsize=(12, 4))
ax = fig.add_subplot(131)
ax.imshow(Z, origin='lower', extent=(-3, 3, -3, 3), cmap='terrain')
ax.set(title='1 / Sample a field', xlabel='East', ylabel='North')
ax = fig.add_subplot(132)
ax.contour(X, Y, Z, levels=10, cmap='viridis')
ax.set(title='2 / Read its contours', xlabel='East', aspect='equal')
ax = fig.add_subplot(133, projection='3d')
ax.plot_surface(X, Y, Z, cmap='terrain', linewidth=0)
ax.set(title='3 / Build a surface', xlabel='East', ylabel='North', zlabel='Height')
fig.tight_layout()
plt.show()
# %% [markdown]
# The three views encode **the same array**. Color makes height easy to scan; contours make slope
# visible through spacing; perspective makes shape easier to imagine but can hide the far side.
# A useful visualization changes the question you can answer, not the evidence underneath it.
#
# **Predict:** if the grid doubles in both directions, how many samples are needed?
# **Check:** four times as many. More samples improve surface detail but cost memory and rendering time.
#
# **Keep the evidence straight.** Local x/y distances use the labeled units; longitude/latitude use
# degrees. Generated cities, terrain and sensor readings are synthetic. Changing their parameters
# demonstrates a relationship; it does not measure a real city, flood, current or climate.
#
# If an animation is blank in a saved preview, run its cell in JupyterLite. On a small device, start
# with static figures. If your browser blocks WebGL, every World Lab topic has a notebook fallback.
