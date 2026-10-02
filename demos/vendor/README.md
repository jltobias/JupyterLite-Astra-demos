# Vendored renderer

Three.js **0.160.1** (`three.module.min.js`) is served locally so World Lab scenes
do not depend on a runtime CDN. Source: https://github.com/mrdoob/three.js/tree/r160
and https://www.npmjs.com/package/three/v/0.160.1.

Downloaded from `https://cdn.jsdelivr.net/npm/three@0.160.1/build/three.module.min.js`.
The MIT license is reproduced in [THREE-LICENSE.txt](THREE-LICENSE.txt).
All scene code in `../worlds.js` is original to this repository.

When updating the renderer, retain its license, update this version record, and run
the browser smoke tests. No third-party textures, map tiles or creator assets are bundled.
