# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
import ast
import re
import xml.etree.ElementTree as ET
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'

def test_expected_packages():
    names = {ET.parse(p).getroot().findtext('name') for p in SRC.glob('*/package.xml')}
    assert names == {'fishbot_description', 'fishbot_navigation2', 'fishbot_application',
                     'autopartol_robot', 'autopatrol_interfaces'}

def test_sources_parse():
    for path in SRC.rglob('*.py'):
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    for suffix in ('*.xacro', '*.urdf', '*.sdf', 'package.xml'):
        for path in SRC.rglob(suffix):
            ET.parse(path)

def test_world_has_no_saved_duplicate_or_external_mesh():
    world = ET.parse(SRC / 'fishbot_description/world/room/custom_room.sdf').getroot().find('world')
    assert world is not None
    assert world.find("model[@name='fishbot']") is None
    assert not world.findall('.//mesh')
    assert not world.findall('.//include')

def test_map_and_patrol_config_are_shipped():
    maps = SRC / 'fishbot_navigation2/maps'
    config = yaml.safe_load((maps / 'room.yaml').read_text())
    pgm = maps / config['image']
    assert pgm.exists()
    assert pgm.read_bytes().startswith(b'P5')
    for name in ('patrol_config.yaml', 'patrol_once.yaml'):
        params = yaml.safe_load((SRC / 'autopartol_robot/config' / name).read_text())['/patrol_node']['ros__parameters']
        assert len(params['initial_point']) == 3
        assert len(params['target_points']) % 3 == 0

def test_no_personal_absolute_paths():
    for path in SRC.rglob('*'):
        if path.is_file() and path.suffix in {'.py', '.yaml', '.sdf', '.xacro', '.xml', '.rviz'}:
            assert not re.search(r'/(?:home|Users)/', path.read_text()), str(path)

def test_local_xacro_includes_resolve():
    for path in (SRC / 'fishbot_description/urdf').rglob('*.xacro'):
        for reference in re.findall(r'\$\(find fishbot_description\)([^"<\s]+)', path.read_text()):
            assert (SRC / 'fishbot_description' / reference.lstrip('/')).exists(), reference
