# SPDX-License-Identifier: Apache-2.0
"""ROS-independent validation and output-path helpers."""
import math
from pathlib import Path

def parse_waypoints(values):
    if not values or len(values) % 3:
        raise ValueError('Waypoints must be nonempty [x, y, yaw] triples.')
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError('Waypoint values must be finite.')
    return [tuple(float(v) for v in values[i:i + 3])
            for i in range(0, len(values), 3)]

def image_path(directory, timestamp_ns, x, y):
    return Path(directory).expanduser() / f'image_{timestamp_ns}_{x:.2f}_{y:.2f}.png'
