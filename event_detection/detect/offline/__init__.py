"""Offline methods for event detection in molecular simulations."""

from .costs import CostLinearFit
from .detect import (
    SweepDetector,
    kneedle_elbow_detection,
    two_pass_elbow_detection,
)
