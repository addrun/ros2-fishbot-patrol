# SPDX-License-Identifier: Apache-2.0
"""Compatibility entry point for the explicitly opt-in online TTS backend."""
from autopartol_robot.speaker import main as speaker_main

def main(args=None):
    speaker_main(args=args, default_backend='edge')
