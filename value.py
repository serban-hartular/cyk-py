from typing import Set, Iterable


class Value(Set[str]):
    ALL_STR = '##ALL##'
    def __init__(self, s=None):
        super().__init__()
        if s is None:
            s = set()
        self._isAll = False
        if isinstance(s, str):
            if s == Value.ALL_STR:
                self._isAll = True
                s = set()
            else:
                s = s.split(',')
        self.update(s)
        if isinstance(s, Value):
            self._isAll = s.isAll()
    @staticmethod
    def all() -> 'Value':
        a = Value()
        a._isAll = True
        return a
    def isAll(self) -> bool:
        return self._isAll
    # @override
    def union(self, s: Iterable[str]) -> 'Value':
        s = Value(s)
        if self.isAll() or s.isAll(): return Value.all()
        return Value(super().union(s))
    def intersection(self, s: Iterable[str]) -> 'Value':
        s = Value(s)
        if self.isAll(): return Value(s)
        if s.isAll(): return Value(self)
        return Value(super().intersection(s))
    def issubset(self, s: Iterable[str]) -> bool:
        s = Value(s)
        if s.isAll() and self.isAll(): return True
        if self.isAll(): return False
        if s.isAll(): return True
        return super().issubset(s)
    def __eq__(self, other):
        other = Value(other)
        if self.isAll() and other._isAll(): return True
        return super().__eq__(other)
    def __bool__(self) -> bool:
        if self.isAll(): return True
        return bool(len(self))
    def __len__(self) -> int:
        if self.isAll(): return -1
        return super().__len__()
    def __repr__(self) -> str:
        if self.isAll():
            return 'Value(%s)' % Value.ALL_STR
        return super(Set, self).__repr__()
    def __str__(self) -> str:
        if self.isAll():
            return Value.ALL_STR
        return ','.join([str(s) for s in self])