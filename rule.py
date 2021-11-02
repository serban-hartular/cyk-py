
from typing import Dict, List
from collections import defaultdict
TYPE_STR = 'type'

VAR_PREFIX = '@'


# RValues = List[str]
from rvalues import RValues

class NodeData(Dict[str, RValues]):
    def __init__(self, d : dict):
        super().__init__()
        for k,v in d.items():
            self[k] = RValues(v)
    def __setitem__(self, key, value):
        super().__setitem__(key, RValues(value))

# def isVar(val : RValues):
#     if not val or len(val) != 1: return None
#     val = list(val)
#     if val[0].startswith(VAR_PREFIX): return val[0]
#     return None

class Constraint:
    def __init__(self, key: str, values : RValues, isStrict : bool = False, isNegated : bool = False) -> None:
        if not values:
            raise Exception("Constraint must contain values")
        self.key = key
        self.values = RValues(values)
        self.isStrict = isStrict
        self.isNegated = isNegated
        self.isVariable = self.values.isVariable
        if self.isVariable and self.isNegated:
            raise Exception("Negated equality to unknown variable not allowed")
        # if self.isVariable and var == VAR_PREFIX:
        #     self.values = RValues(VAR_PREFIX + key)
    def matches(self, data : NodeData, var_dict : dict = None) -> bool:
        if self.isVariable and var_dict is None:
            raise Exception('Asked to evaluate variable and no var_dict provided in %s' % str(self))
        data_values = data.get(self.key)
        if not data_values:
            data_values = RValues() if self.isStrict else RValues.all()
        self_values = var_dict[self.key] if self.isVariable else self.values
        intersection = self_values.intersection(data_values)
        if not intersection:
            return self.isNegated # true if result is empty, false if it isn't
        if self.isVariable:
            var_dict[self.key] = intersection
        return not self.isNegated 
    def to_text(self):
        if not self.isNegated:
            operator = '==' if self.isStrict else '='
        else:
            operator = '!=' if self.isStrict else '!=='
        values = ','.join([v for v in self.values]) if not self.isVariable else (RValues.VAR_STR + self.values.get())
        return self.key + operator + values
    def __str__(self):
        return self.to_text()
    def __repr__(self):
        return str(self)

class RuleItem(Dict[str, Constraint]):
    def __init__(self, l : List[Constraint], annotation : Dict = None):
        super().__init__({c.key : c for c in l})
        self.annotation = annotation if annotation else dict()
    def matches(self, item : NodeData, variable_dict : dict, keys_to_skip = list()):
        for key, constraint in self.items():
            if key in keys_to_skip: continue
            if not constraint.matches(item, variable_dict):
                return False
        return True
    def to_node(self):
        return NodeData({k:v.values for k, v in self.items()})
    def to_text(self):
        text = self[TYPE_STR].values.get() if TYPE_STR in self.keys() else ''
        keys_less_type = [k for k in self.keys() if k != TYPE_STR]
        if not keys_less_type: return text
        text += '['
        text += ' '.join([self[k].to_text() for k in keys_less_type])
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
        self.score = 1
    def apply(self, candidates : List[NodeData]) -> (NodeData, List[Dict]):
        if len(candidates) != len(self.children):
            return None
        # try constraints on candidates
        variable_dict = defaultdict(lambda : RValues.all())
        for i in range(0, len(candidates)):
            if not self.children[i].matches(candidates[i], variable_dict):
                return None
        parent_node = NodeData(self.parent.to_node())
        # look for variables
        keys_to_pop = []
        for key, value in parent_node.items():
            # var = isVar(value)
            if not value.isVariable: continue
            actual_val = variable_dict.get(key)
            if not actual_val: return None
            if actual_val.isAll():
                keys_to_pop.append(key) # if isAll() -- no new info, pop
            else:
                parent_node[key] = actual_val
        for key in keys_to_pop: parent_node.pop(key)
        return parent_node, [child.annotation for child in self.children]
    def to_text(self):
        return self.parent.to_text() + ' ::= ' + ' '.join([c.to_text() for c in self.children])
    def __str__(self):
        return self.to_text()
    def __repr__(self):
        return str(self)
