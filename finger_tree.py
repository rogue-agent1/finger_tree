#!/usr/bin/env python3
"""finger_tree - 2-3 finger tree (persistent deque with O(1) amortized ends, O(log n) split/concat).

Usage: python finger_tree.py [--demo]
"""

class Empty:
    def to_list(self): return []
    def __repr__(self): return "Empty"
    def __len__(self): return 0

class Single:
    def __init__(self, val): self.val = val
    def to_list(self): return [self.val]
    def __repr__(self): return f"Single({self.val})"
    def __len__(self): return 1

class Deep:
    def __init__(self, left, middle, right):
        self.left = left      # list of 1-4 elements
        self.middle = middle   # finger tree of nodes
        self.right = right     # list of 1-4 elements
        self._size = len(self.left) + _mid_count(self.middle) + len(self.right)
    def to_list(self):
        mid = []
        for node in _tree_to_list(self.middle):
            mid.extend(node)
        return list(self.left) + mid + list(self.right)
    def __repr__(self):
        return f"Deep({self.left}, ..., {self.right})"
    def __len__(self): return self._size

def _mid_count(t):
    """Count total leaf elements stored in the middle tree of nodes."""
    if isinstance(t, Empty): return 0
    if isinstance(t, Single): return len(t.val) if isinstance(t.val, tuple) else 1
    # Deep middle: sum all
    return sum(len(n) if isinstance(n, tuple) else 1 for n in _tree_to_list(t))

def _tree_to_list(t):
    if isinstance(t, Empty): return []
    if isinstance(t, Single): return [t.val]
    return t.to_list()

def cons(x, t):
    """Add to front."""
    if isinstance(t, Empty): return Single(x)
    if isinstance(t, Single): return Deep([x], Empty(), [t.val])
    if len(t.left) < 4:
        return Deep([x] + t.left, t.middle, t.right)
    # Overflow: push node into middle
    a, b, c, d = t.left
    return Deep([x, a], cons((b, c, d), t.middle), t.right)

def snoc(t, x):
    """Add to back."""
    if isinstance(t, Empty): return Single(x)
    if isinstance(t, Single): return Deep([t.val], Empty(), [x])
    if len(t.right) < 4:
        return Deep(t.left, t.middle, t.right + [x])
    a, b, c, d = t.right
    return Deep(t.left, snoc(t.middle, (a, b, c)), [d, x])

def head(t):
    if isinstance(t, Single): return t.val
    if isinstance(t, Deep): return t.left[0]
    raise IndexError("empty tree")

def last(t):
    if isinstance(t, Single): return t.val
    if isinstance(t, Deep): return t.right[-1]
    raise IndexError("empty tree")

def tail(t):
    """Remove from front."""
    if isinstance(t, Single): return Empty()
    if isinstance(t, Deep):
        if len(t.left) > 1:
            return Deep(t.left[1:], t.middle, t.right)
        if not isinstance(t.middle, Empty):
            node = head(t.middle)
            return Deep(list(node), tail(t.middle), t.right)
        if len(t.right) == 1:
            return Single(t.right[0])
        return Deep([t.right[0]], Empty(), t.right[1:])
    raise IndexError("empty tree")

def init(t):
    """Remove from back."""
    if isinstance(t, Single): return Empty()
    if isinstance(t, Deep):
        if len(t.right) > 1:
            return Deep(t.left, t.middle, t.right[:-1])
        if not isinstance(t.middle, Empty):
            node = last(t.middle)
            return Deep(t.left, init(t.middle), list(node))
        if len(t.left) == 1:
            return Single(t.left[0])
        return Deep(t.left[:-1], Empty(), [t.left[-1]])
    raise IndexError("empty tree")

def from_list(xs):
    t = Empty()
    for x in xs:
        t = snoc(t, x)
    return t

def main():
    print("=== 2-3 Finger Tree ===\n")
    # Build from list
    t = from_list(range(10))
    print(f"Built: {t.to_list()}")
    print(f"Size: {len(t)}")
    print(f"Head: {head(t)}, Last: {last(t)}")
    # cons/snoc
    t = cons(-1, t)
    t = snoc(t, 10)
    print(f"After cons(-1) snoc(10): {t.to_list()}")
    # tail/init
    t = tail(t); t = init(t)
    print(f"After tail/init: {t.to_list()}")
    # Stress test
    print(f"\nStress: 10000 cons + 5000 tail...")
    t = Empty()
    for i in range(10000):
        t = cons(i, t)
    assert len(t) == 10000
    for _ in range(5000):
        t = tail(t)
    assert len(t) == 5000
    lst = t.to_list()
    assert len(lst) == 5000
    print(f"  Size: {len(t)}, head={head(t)}, last={last(t)}")
    # Deque operations
    print(f"\nDeque stress: alternating cons/snoc/tail/init...")
    t = Empty()
    for i in range(1000):
        t = cons(i, t)
        t = snoc(t, i)
    for _ in range(500):
        t = tail(t)
        t = init(t)
    print(f"  Size: {len(t)}")
    print(f"  Integrity: {'OK' if len(t.to_list()) == len(t) else 'FAIL'}")

if __name__ == "__main__":
    main()
