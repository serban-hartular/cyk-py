
from typing import Dict, List
from collections import defaultdict
TYPE_STR = 'type'

VAR_PREFIX = '@'


# Values = List[str]
from values import Values

class NodeData(Dict[str, Values]):
    def __init__(self, d : dict):
        super().__init__()
        for k,v in d.items():
            self[k] = Values(v)
    def __setitem__(self, key, value):
        super().__setitem__(key, Values(value))

def isVar(val : Values):
    if not val or len(val) != 1: return None
    val = list(val)
    if val[0].startswith(VAR_PREFIX): return val[0]
    return None

class Constraint:
    def __init__(self, key: str, values : Values, isStrict : bool = False, isNegated : bool = False) -> None:
        if not values:
            raise Exception("Constraint must contain values")
        self.key = key
        self.values = Values(values)
        self.isStrict = isStrict
        self.isNegated = isNegated
        var = isVar(self.values)
        if var and self.isNegated:
            raise Exception("Negated equality to unkown variable not allowed")
        if var and var == VAR_PREFIX:
            self.values = Values(VAR_PREFIX + key)
    def matches(self, data : NodeData, var_dict : dict = None) -> bool:
        if isVar(self.values) and var_dict is None:
            raise Exception('Asked to evaluate variable and no var_dict provided in %s' % str(self))
        data_values = data.get(self.key)
        if not data_values:
            data_values = Values() if self.isStrict else Values.all()
        self_values = var_dict[self.key] if isVar(self.values) else self.values
        intersection = self_values.intersection(data_values)
        if not intersection:
            return self.isNegated # true if result is empty, false if it isn't
        if isVar(self.values):
            var_dict[self.key] = intersection
        return not self.isNegated 
    # def _matches(self, values : Values) -> Values:
    #     if not values:
    #         values = Values() if self.isStrict else Values.all()
    #     return self.values.intersection(values)
    # def __matches(self, values : Values) -> Values:
    #     m = self._matches(values)
    #     if not self.isNegated: return m
    #     if m: return Values()
    #     else: return Values.all()
    def to_text(self):
        return self.key+('!=' if self.isNegated else ('==' if self.isStrict else '=')) + ','.join([v for v in self.values])
    def __str__(self):
        return self.to_text()
    def __repr__(self):
        return str(self)

class RuleItem(Dict[str, Constraint]):
    def __init__(self, l : List[Constraint]):
        super().__init__({c.key : c for c in l})
        # for key, constraint in self.items():
        #     var = isVar(constraint.values)
        #     if var and var[0] == VAR_PREFIX:
        #         constraint.values = Values(var + key) # num=@ will become num=@num
    def matches(self, item : NodeData, variable_dict : dict, keys_to_skip = list()):
        for key, constraint in self.items():
            if key in keys_to_skip: continue
            if not constraint.matches(item, variable_dict):
                # print(str(item) + ' failed ' + str(constraint))
                return False
            # item_val = item.get(key)
            # if not item_val: item_val = Values() if constraint.isStrict else Values.all()
            # if isVar(constraint.values): 
            #     var_value = variable_dict[isVar(constraint.values)].intersection(item_val)
            #     variable_dict[isVar(constraint.values)] = var_value
            #     if not var_value: return False
            # elif not constraint.matches(item_val):
            #     return False
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
    def apply(self, candidates : List[NodeData]) -> NodeData:
        if len(candidates) != len(self.children):
            return None
        # try constraints on candidates
        variable_dict = defaultdict(lambda : Values.all())
        for i in range(0, len(candidates)):
            if not self.children[i].matches(candidates[i], variable_dict):
                return None
        parent_node = NodeData(self.parent.to_node())
        # look for variables
        keys_to_pop = []
        for key, value in parent_node.items():
            var = isVar(value)
            if not var: continue
            actual_val = variable_dict.get(key)
            if not actual_val: return None
            if actual_val.isAll():
                keys_to_pop.append(key) # if isAll() -- no new info, pop
            else:
                parent_node[key] = actual_val
        for key in keys_to_pop: parent_node.pop(key)
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
