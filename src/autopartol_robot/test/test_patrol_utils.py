# SPDX-License-Identifier: Apache-2.0
import pytest
from autopartol_robot.patrol_utils import image_path, parse_waypoints

def test_waypoint_triples():
    assert parse_waypoints([1, 2, 3, 4, 5, 6]) == [(1., 2., 3.), (4., 5., 6.)]

@pytest.mark.parametrize('values', [[], [1, 2], [1, 2, 3, 4], [0, 0, float('nan')], [0, 0, float('inf')]])
def test_rejects_invalid_points(values):
    with pytest.raises(ValueError):
        parse_waypoints(values)

def test_output_path_does_not_need_trailing_slash(tmp_path):
    path = image_path(str(tmp_path), 123, 1.234, -2)
    assert path.parent == tmp_path
    assert path.name == 'image_123_1.23_-2.00.png'

def test_capture_names_do_not_overwrite_previous_visits(tmp_path):
    assert image_path(tmp_path, 1, 0, 0) != image_path(tmp_path, 2, 0, 0)
