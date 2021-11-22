from typing import Set, Iterable


class RValues(Set[str]):
    ALL_STR = '##ALL##'
    VAR_STR = '@'
    def __init__(self, s=None, isVariable : bool = False):
        super().__init__()
        if isinstance(s, RValues):
            self.isVariable = s.isVariable
            self._isAll = s.isAll()
            self.update(s)
            return 
        self.isVariable = isVariable
        if s is None:
            s = set()
        self._isAll = False
        if isinstance(s, str):
            if s == RValues.ALL_STR:
                self._isAll = True
                s = set()
            else:
                s = s.split(',')
        self.update(s)
        if self.isVariable and len(self) != 1:
            raise Exception('RValues variable must have 1 value, not ' + str(set(self)))
    @staticmethod
    def all() -> 'RValues':
        a = RValues()
        a._isAll = True
        return a
    def isAll(self) -> bool:
        return self._isAll
    def get(self):
        # if len(self) != 1: return None
        return list(self)[0]
    def union(self, s: Iterable[str]) -> 'RValues':
        s = RValues(s)
        if self.isAll() or s.isAll(): return RValues.all()
        return RValues(super().union(s))
    def intersection(self, s: Iterable[str]) -> 'RValues':
        s = RValues(s)
        if self.isAll(): return RValues(s)
        if s.isAll(): return RValues(self)
        return RValues(super().intersection(s))
    def issubset(self, s: Iterable[str]) -> bool:
        s = RValues(s)
        if s.isAll() and self.isAll(): return True
        if self.isAll(): return False
        if s.isAll(): return True
        return super().issubset(s)
    def __eq__(self, other):
        other = RValues(other)
        if self.isAll() and other._isAll(): return True
        return super().__eq__(other) and self.isVariable == other.isVariable
    def __bool__(self) -> bool:
        if self.isAll(): return True
        return bool(len(self))
    def __len__(self) -> int:
        if self.isAll(): return -1
        return super().__len__()
    def __repr__(self) -> str:
        if self.isAll():
            return 'RValues(%s)' % RValues.ALL_STR
        return (RValues.VAR_STR if self.isVariable else '') + super().__repr__()
    def __str__(self) -> str:
        if self.isAll():
            return RValues.ALL_STR
        return (RValues.VAR_STR if self.isVariable else '') + ','.join([str(s) for s in self])
    def to_jsonable(self):
        obj = list(self)
        if self.isVariable: obj[0] = '@' + obj[0]
        return obj
