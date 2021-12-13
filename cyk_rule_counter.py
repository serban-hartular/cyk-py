from collections import defaultdict
from typing import Dict, List

from cyk_parser import Tree
from rule import Rule
from rule_io import LEMMA_STR


class RuleCounter:
    def __init__(self):
        self.counter = defaultdict(int) 
        self._rules = set()
        self._lemmas = set()
    def add(self, rule : Rule, lemmas : List[str]):
        assert len(lemmas) in [1, 2]
        rule_str = str(rule)
        arg = tuple([rule_str] + lemmas)
        self.counter[arg] += 1
        if len(lemmas) == 2:
            self.counter[(rule_str, lemmas[0], None)] += 1
            self.counter[(rule_str, None, lemmas[1])] += 1
        self.counter[(rule_str,)] += 1
        self._rules.add(rule_str)
        self._lemmas.add(tuple(lemmas))
    def add_tree(self, tree : Tree):
        if not tree.children:
            return
        self.add(tree.rule, [str(child.data.get(LEMMA_STR)) if child.data.get(LEMMA_STR) else ''
                             for child in tree.children])
        for child in tree.children:
            self.add_tree(child)
    def get_rules(self) -> list:
        return list(self._rules)
    def get_count(self, rule, lemmas : List[str] = None) -> int:
        rule = str(rule)
        lemmas = list(lemmas)
        if not lemmas:
            return self.counter[(rule,)]
        return self.counter[tuple([rule] + lemmas)]
    def get_lemmas(self, rule) -> list:
        rule = str(rule)
        count_list = []
        for key in self.counter:
            if key[0] == rule and len(key)>1 and not None in key:
                count_list.append((key[1:], self.counter[key]))
        return count_list
    