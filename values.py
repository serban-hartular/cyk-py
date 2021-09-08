from typing import Set, Iterable


class Values(Set[str]):
    ALL_STR = '##ALL##'
    def __init__(self, s=None):
        super().__init__()
        if s is None:
            s = set()
        self._isAll = False
        if isinstance(s, str):
            if s == Values.ALL_STR:
                self._isAll = True
                s = set()
            else:
                s = s.split(',')
        self.update(s)
        if isinstance(s, Values):
            self._isAll = s.isAll()
    @staticmethod
    def all() -> 'Values':
        a = Values()
        a._isAll = True
        return a
    def isAll(self) -> bool:
        return self._isAll
    def get(self):
        # if len(self) != 1: return None
        return list(self)[0]
    def union(self, s: Iterable[str]) -> 'Values':
        s = Values(s)
        if self.isAll() or s.isAll(): return Values.all()
        return Values(super().union(s))
    def intersection(self, s: Iterable[str]) -> 'Values':
        s = Values(s)
        if self.isAll(): return Values(s)
        if s.isAll(): return Values(self)
        return Values(super().intersection(s))
    def issubset(self, s: Iterable[str]) -> bool:
        s = Values(s)
        if s.isAll() and self.isAll(): return True
        if self.isAll(): return False
        if s.isAll(): return True
        return super().issubset(s)
    def __eq__(self, other):
        other = Values(other)
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
            return 'Values(%s)' % Values.ALL_STR
        return super(Set, self).__repr__()
    def __str__(self) -> str:
        if self.isAll():
            return Values.ALL_STR
        return ','.join([str(s) for s in self])