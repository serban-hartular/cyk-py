from collections import defaultdict
from typing import List, Dict, Iterable

from cyk.rule import Rule
from cyk.rule_io import TYPE_STR


class Grammar:
    def __init__(self, rules : List[Rule]):
        self._rules = rules
        self._singletons = [r for r in rules if len(r.children) == 1]
        self._doubletons = [r for r in rules if len(r.children) == 2]
        others = [r for r in rules if len(r.children) != 1 and len(r.children) != 2]
        if others:
            raise Exception("Rules can only have 1 or 2 children: '%s'" % others[0].to_text())
        self.nonterminals = set([rule.parent.constraints[TYPE_STR].values.get() for rule in self._rules])
        self.terminals = set([ruleitem.constraints[TYPE_STR].values.get() for rule in rules \
                              for ruleitem in ([rule.parent] + rule.children) \
                              if ruleitem.constraints[TYPE_STR].values.get() not in self.nonterminals])
        self.assign_scores()
        self._rule_map : Dict[tuple, List[Rule]] = defaultdict(list)
        self._add_rules_to_map()
    def assign_scores(self):
        for nonterm in self.nonterminals:
            rules = [rule for rule in self._rules if rule.parent.constraints[TYPE_STR].values.get() == nonterm]
            n = 0
            for rule in rules:
                if len(rule.children) == 1: # this is kind of doubtful
                    rule.score = 1.00001
                    continue
                rule.score = 1 / (n+1)
                n += 1
    def is_known(self, type_str : str) -> bool:
        return type_str in self.terminals.union(self.nonterminals)
    def _add_rules_to_map(self):
        for rule in self._rules:
            types = [str(item.constraints[TYPE_STR].values) for item in ([rule.parent] + rule.children)]
            self._rule_map[tuple(types)].append(rule)
            for i in range(0, len(types)):
                arg = [s for s in types]
                arg[i] = None
                self._rule_map[tuple(arg)].append(rule)
            for i in range(0, len(types)):
                arg = [s if j == i else None for j,s in enumerate(types)]
                self._rule_map[tuple(arg)].append(rule)
    def get_rules(self, args : Iterable[str] = None):
        if not args: return self._rules
        args = tuple(args)
        if args == (None,): return self._singletons
        if args == (None, None): return self._doubletons
        return self._rule_map[args]
    