"""Core rolling-window implementation.

The :class:`RollingWindow` maintains a bounded FIFO buffer over a stream of
numbers. It exposes O(1) running mean, and O(window-size) peak / trough. The
peak and trough could be made O(1) with a monotonic-deque, but the extra
complexity is not justified until a caller demonstrates a real performance
problem — keeping the code short and obviously correct is the priority here.
"""

from __future__ import annotations

from collections import deque
from typing import Deque


class InvalidWindowError(ValueError):
    """Raised when the window is constructed or used with invalid parameters."""


class RollingWindow:
    """A bounded rolling window over a stream of numeric values.

    The window holds at most ``capacity`` values. When full, each call to
    :meth:`push` discards the oldest value before appending the new one, so
    the window size never exceeds ``capacity``.

    ``mean`` returns ``None`` when the window is empty so that callers can
    distinguish "no data yet" from a genuine zero. ``peak`` and ``trough``
    follow the same convention.
    """

    __slots__ = ("_capacity", "_buf", "_sum")

    def __init__(self, capacity: int):
        if not isinstance(capacity, int) or isinstance(capacity, bool):
            raise InvalidWindowError("capacity must be an int")
        if capacity <= 0:
            raise InvalidWindowError("capacity must be a positive int")
        self._capacity = capacity
        self._buf: Deque[float] = deque(maxlen=capacity)
        self._sum: float = 0.0

    @property
    def capacity(self) -> int:
        return self._capacity

    def __len__(self) -> int:
        return len(self._buf)

    def push(self, value: float) -> None:
        """Append ``value`` to the window, evicting the oldest entry if full.

        ``deque(maxlen=...)`` handles eviction automatically, but it does not
        tell us *which* element it dropped. We therefore check the current
        length against capacity before the append: if the deque is full, the
        element at ``self._buf[0]`` is the one about to be evicted, and we
        subtract it from the running sum before the append happens.
        """
        if isinstance(value, bool):
            raise InvalidWindowError("bool is not a valid numeric value")
        if not isinstance(value, (int, float)):
            raise InvalidWindowError("value must be int or float")
        if value != value:  # NaN check without importing math
            raise InvalidWindowError("value must be a finite number (NaN rejected)")
        if value == float("inf") or value == float("-inf"):
            raise InvalidWindowError("value must be a finite number (inf rejected)")
        if len(self._buf) == self._capacity:
            self._sum -= self._buf[0]
        self._buf.append(float(value))
        self._sum += value

    def mean(self) -> float | None:
        """Return the arithmetic mean of the window, or ``None`` if empty."""
        n = len(self._buf)
        if n == 0:
            return None
        return self._sum / n

    def peak(self) -> float | None:
        """Return the maximum value in the window, or ``None`` if empty."""
        if not self._buf:
            return None
        return max(self._buf)

    def trough(self) -> float | None:
        """Return the minimum value in the window, or ``None`` if empty."""
        if not self._buf:
            return None
        return min(self._buf)

    def values(self) -> list:
        """Return a snapshot of the window contents in insertion order."""
        return list(self._buf)
