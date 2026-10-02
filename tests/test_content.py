"""Source synchronization and mathematical edge cases, without network access."""
from pathlib import Path
import ast
import importlib.util
import json
import sys
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'content/notebooks'))
sys.path.insert(0,str(ROOT/'scripts'))
from build_notebooks import convert
from astra_utils import animate_tracks


def function_from_lesson(stem, names, extra=None):
    """Load actual lesson functions without executing plots or exports."""
    source=(ROOT/'lessons'/f'{stem}.py').read_text(encoding='utf-8')
    tree=ast.parse(source)
    functions=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in names]
    scope={'np':np,**(extra or {})}
    exec(compile(ast.Module(body=functions,type_ignores=[]),str(stem),'exec'),scope)
    return scope


def test_notebooks_match_sources_and_navigation():
    readme=(ROOT/'README.md').read_text(encoding='utf-8')
    toc=(ROOT/'myst.yml').read_text(encoding='utf-8')
    paths=sorted((ROOT/'lessons').glob('*.py'))
    assert len(paths)==16
    for source in paths:
        path=ROOT/'content/notebooks'/f'{source.stem}.ipynb'
        actual=json.loads(path.read_text(encoding='utf-8'))
        expected=convert(source)
        assert [(c['cell_type'],''.join(c['source'])) for c in actual['cells']] == [(c['cell_type'],''.join(c['source'])) for c in expected['cells']]
        assert path.name in readme and path.name in toc
        assert any(c['cell_type']=='code' for c in actual['cells'])
        first_code=next(''.join(c['source']) for c in actual['cells'] if c['cell_type']=='code')
        # Pyodide scans this cell for packages, not imports inside local helpers.
        assert 'import numpy' in first_code and 'import matplotlib' in first_code


def test_globe_endpoints_and_degenerate_routes():
    ns=function_from_lesson('06_globe_projections',['xyz','great_circle','equal_earth'])
    a,b=ns['xyz'](0,0),ns['xyz'](90,0)
    route=ns['great_circle'](a,b)
    assert np.allclose(route[[0,-1]],[a,b])
    assert np.allclose(np.linalg.norm(route,axis=1),1)
    assert np.allclose(ns['great_circle'](a,a),a)
    with pytest.raises(ValueError):ns['great_circle'](a,-a)
    assert np.allclose(ns['equal_earth'](0,0),(0,0))


def test_water_excludes_enclosed_basin_until_pass_opens():
    from collections import deque
    flood=function_from_lesson('07_terrain_water',['connected_water'],{'deque':deque})['connected_water']
    terrain=np.zeros((5,5));terrain[1:4,1:4]=10;terrain[2,2]=-5
    assert not flood(terrain,0)[2,2]
    terrain[1,2]=0
    assert flood(terrain,0)[2,2]
    assert not flood(terrain,-10).any()
    assert flood(terrain,10).all()


def test_routing_uses_weights_and_handles_unreachable_nodes():
    import heapq
    nodes=['a','b','c','isolated']
    route=function_from_lesson('09_route_networks',['shortest_paths'],{'heapq':heapq,'nodes':nodes})['shortest_paths']
    dist,parent=route('a',[('a','c',10),('a','b',2),('b','c',1)])
    assert dist['c']==3 and parent['c']=='b' and 'isolated' not in dist
    with pytest.raises(ValueError):route('a',[('a','b',-1)])


def test_interpolation_exact_samples_and_constant_field():
    idw=function_from_lesson('14_spatial_interpolation',['idw'])['idw']
    stations=np.array([[0,0],[1,1],[1,0]])
    assert np.allclose(idw(stations,stations,np.array([3,4,8]))[0],[3,4,8])
    assert np.allclose(idw(np.array([[5,9],[.5,.5]]),stations,np.ones(3)*7)[0],7)


def test_shadow_direction_and_limits():
    shadow=function_from_lesson('15_sunlight_shadows',['shadow_offset'])['shadow_offset']
    assert np.allclose(shadow(10,45,90),[-10,0])
    assert np.allclose(shadow(10,90,0),[0,0],atol=1e-12)
    with pytest.raises(ValueError):shadow(10,0,90)


def test_animation_is_self_contained_and_escapes_labels():
    animation=animate_tracks(np.zeros((2,1,2)),(0,1,0,1),title='<unsafe>',labels=['</script>']).data
    assert 'sandbox="allow-scripts"' in animation
    assert 'src="http' not in animation
    assert '<unsafe>' not in animation
    with pytest.raises(ValueError):animate_tracks(np.zeros((1,1,2)),(0,1,0,1))


def test_bundled_land_provenance_and_coordinates():
    import hashlib
    source=(ROOT/'content/notebooks/data/ne_110m_land.geojson').read_bytes()
    assert hashlib.sha256(source).hexdigest()=='9e0729ee253ca7d7a5c4ae9395fb1902264c5377c52e224d13dd85010e2835d9'
    assert source==(ROOT/'demos/data/ne_110m_land.geojson').read_bytes()
    data=json.loads(source)
    assert data['type']=='FeatureCollection' and len(data['features'])>100
