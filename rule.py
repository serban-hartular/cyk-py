
from typing import Dict, List
from collections import defaultdict
TYPE_STR = 'type'

VAR_PREFIX = '@'
ALL_SET = ['##ALL##']

Values = List[str]
class NodeData(Dict[str, Values]):
    def __init__(self, d):
        super().__init__(d)
        for val in self.values():
            if isinstance(val, str):
                raise Exception("'" + val + "' is a string, must be a list/iterable")
    def __setitem__(self, key, value):
        if isinstance(value, str): raise Exception('Value %s is a string, must be list' % value)
        if not isinstance(key, str): raise Exception('Key %s must be a string' % str(key))
        super().__setitem__(key, value)

def isVar(val : Values):
    if not val: return None
    if val[0].startswith(VAR_PREFIX): return val[0]
    return None

def intersection(l1 : list, l2 : list) -> list:
    if l1 == ALL_SET: return l2
    if l2 == ALL_SET: return l1
    return [v for v in l1 if v in l2]

class Constraint:
    def __init__(self, values : Values, isStrict : bool = False, isNegated : bool = False) -> None:
        if not values:
            raise Exception("Constraint must contain values")
        if isinstance(values, str):
            raise Exception("values is a string, must be a list/iterable")
        self.values = values
        self.isStrict = isStrict
        self.isNegated = isNegated
        if isVar(self.values) and self.isNegated:
            raise Exception("Negated equality to variable not allowed")
    def _matches(self, values : Values) -> Values:
        if not values:
            return [] if self.isStrict else self.values
        return intersection(values, self.values)
    def matches(self, values : Values) -> Values:
        m = self._matches(values)
        if not self.isNegated: return m
        if m: return []
        else: return ALL_SET
    def to_text(self):
        return ('!=' if self.isNegated else ('==' if self.isStrict else '=')) + ','.join([v for v in self.values])
    def __str__(self):
        return self.to_text()
    def __repr__(self):
        return str(self)

class RuleItem(Dict[str, Constraint]):
    def __init__(self, d : Dict[str, Constraint]):
        super().__init__(d)
        for key, constraint in self.items():
            if isVar(constraint.values) and constraint.values[0] == VAR_PREFIX:
                constraint.values[0] += key # num=@ will become num=@num
    def matches(self, item : NodeData, variable_dict : dict, keys_to_skip = list()):
        for key, constraint in self.items():
            if key in keys_to_skip: continue
            item_val = item.get(key)
            if not item_val: item_val = [] if constraint.isStrict else ALL_SET
            if isVar(constraint.values): 
                var_value = intersection(variable_dict[isVar(constraint.values)], item_val)
                variable_dict[isVar(constraint.values)] = var_value
                if not var_value: return False
            elif not constraint.matches(item_val):
                return False
        return True
    def to_node(self):
        return NodeData({k:v.values for k, v in self.items()})
    def to_text(self):
        text = self[TYPE_STR].values[0] if TYPE_STR in self.keys() else ''
        keys_less_type = [k for k in self.keys() if k != TYPE_STR]
        if not keys_less_type: return text
        text += '['
        text += ' '.join([k + self[k].to_text() for k in keys_less_type])
        text += ']'
        return text
    def __str__(self):
        return self.to_text()
    def __repr__(self):
        return str(self)


class Rule:
    def __init__(self, parent : RuleItem, children : List[RuleItem]):
        self.parent = parent
        self.children = children
    def apply(self, candidates : List[NodeData]) -> NodeData:
        if len(candidates) != len(self.children):
            return None
        # try constraints on candidates
        variable_dict = defaultdict(lambda : ALL_SET)
        for i in range(0, len(candidates)):
            if not self.children[i].matches(candidates[i], variable_dict):
                return None
        parent_node = NodeData(self.parent.to_node())
        # look for variables
        for key, value in parent_node.items():
            var = isVar(value)
            if not var: continue
            actual_val = variable_dict.get(var)
            if not actual_val: return None
            parent_node[key] = actual_val
        return parent_node
    def to_text(self):
        return self.parent.to_text() + ' ::= ' + ' '.join([c.to_text() for c in self.children])
    def __str__(self):
        return self.to_text()
    def __repr__(self):
        return str(self)

        
# NP = RuleItem({'type':Constraint(['NP']), 'nr':Constraint(['@1']), 'def':Constraint(['Def'])})
# N = RuleItem({'type':Constraint(['N']), 'nr':Constraint(['@1'])})
# Det = RuleItem({'type':Constraint(['Det']), 'nr':Constraint(['@1']), 'def':Constraint(['Def', 'Undef'], True)})
# NP_Rule = Rule(NP, [Det, N])
# 
# 
# Un = NodeData({'type':['Det'], 'nr':['1', '2']}) #, 'def':['Def']})
# Tip = NodeData({'type':['N'], 'nr':['2']})
# 
# UnTip = NP_Rule.apply([Un, Tip])
