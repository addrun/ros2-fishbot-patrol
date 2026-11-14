# SPDX-License-Identifier: Apache-2.0
import importlib
import pytest

@pytest.mark.parametrize('module', ['get_robot_pose', 'init_robot_pose', 'nav_to_pose', 'waypoint_follower'])
def test_application_entry_points_import(module):
    assert callable(importlib.import_module('fishbot_application.' + module).main)
