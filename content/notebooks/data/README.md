# Natural Earth land outlines

`ne_110m_land.geojson` contains Natural Earth's generalized 1:110 million land polygons.
Coordinates are longitude/latitude in degrees (WGS84). The notebook and World Lab render polygon
rings as outlines. This is real generalized geography, not local survey or navigation data.

- Authors: Natural Earth contributors, including Tom Patterson and Nathaniel Vaughn Kelso.
- Source: https://github.com/nvkelso/natural-earth-vector/blob/693f11422f4e08d2da4566b854dda53eb7c39fb3/geojson/ne_110m_land.geojson
- License: public domain; https://www.naturalearthdata.com/about/terms-of-use/
- Retrieved: October 2, 2026. No coordinate changes or simplification were applied.
- SHA-256: `9e0729ee253ca7d7a5c4ae9395fb1902264c5377c52e224d13dd85010e2835d9`

An identical copy in `demos/data/` makes the standalone scene self-contained.
Tests verify both copies and their checksum. Made with Natural Earth.
