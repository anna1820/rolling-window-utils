# rolling-window-utils

A bounded rolling window over a stream of numbers with O(1) running mean and O(window-size) peak / trough. Standard library only — no dependencies.

```python
from rolling_window_utils import RollingWindow

w = RollingWindow(capacity=3)
w.push(10)
w.push(20)
w.push(30)
w.push(40)   # evicts 10

w.mean()    # 30.0
w.peak()    # 40.0
w.trough()  # 20.0
w.values()  # [20.0, 30.0, 40.0]
```

The `mean` method maintains a running sum so it stays O(1) per push regardless of window size. `peak` and `trough` scan the buffer on each call. A monotonic-deque could make those O(1) too, but the added complexity is not worth it until a caller shows a real bottleneck — the current code is short and obviously correct.

### Edge cases and decisions

- **Empty window**: `mean`, `peak`, and `trough` all return `None` when the window has no values, so you can distinguish "no data yet" from a genuine zero.
- **NaN and infinities**: `push` rejects `float("nan")`, `float("inf")`, and `float("-inf")`. NaN would silently corrupt every statistic (mean, peak, trough all become NaN), and infinities make the running sum meaningless. Raise early instead.
- **Booleans**: `push(True)` is rejected. In Python `bool` is a subclass of `int` and `True == 1`, but accepting booleans into a numeric stream is a common source of silent bugs. `RollingWindow(True)` for capacity is also rejected for the same reason.
- **Float comparison**: the running sum is a `float`; `mean()` returns a `float`. Tests use `assertAlmostEqual` / exact integer-valued float equality, never raw `==` on fractional results.
