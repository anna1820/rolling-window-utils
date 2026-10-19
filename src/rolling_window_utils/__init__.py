"""rolling-window-utils: bounded rolling window statistics.

Exported names:
    RollingWindow  -- bounded FIFO window with running mean, peak, and trough.
    InvalidWindowError  -- raised on misuse of the window.
"""

from .core import RollingWindow, InvalidWindowError

__all__ = ["RollingWindow", "InvalidWindowError"]
