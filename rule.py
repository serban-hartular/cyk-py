
from typing import Dict, List
from collections import defaultdict

TYPE_STR = 'type'
VAR_PREFIX = '@'
DEPREL_STR = 'deprel'
HEAD_STR = 'h'

# RValues = List[str]
from rvalues import RValues

class NodeData(Dict[str, RValues]):
    def __init__(self, d : dict = None):
        super().__init__()
        if d:
            for k,v in d.items():
                self[k] = RValues(v)
    def __setitem__(self, key, value):
        super().__setitem__(key, RValues(value))
    def to_jsonable(self) -> dict:
        return {k: self[k].to_jsonable() for k in self.keys()}

# def isVar(val : RValues):
#     if not val or len(val) != 1: return None
#     val = list(val)
#     if val[0].startswith(VAR_PREFIX): return val[0]
#     return None

class Variable:
    def __init__(self, key:str, value:str):
        self.key = key
        self.value  = value
    def __str__(self):
        return '%s=@%s' % (self.key, self.value)

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
    def matches(self, data : NodeData) -> bool:
        assert not self.isVariable
        data_values = data.get(self.key)
        if not data_values:
            data_values = RValues() if self.isStrict else RValues.all()
        self_values = self.values # var_dict[self.key] if self.isVariable else self.values
        intersection = self_values.intersection(data_values)
        if not intersection:
            return self.isNegated # true if result is empty, false if it isn't
        return not self.isNegated 
    def process_variable(self, data : NodeData, var_dict : dict):
        assert self.isVariable
        data_values = data[self.key] if self.key in data else RValues.all()
        # print(self.key, data_values, end='\t')
        var_name = self.values.get()
        intersection = var_dict[var_name].intersection(data_values)
        # print(var_name, intersection)
        var_dict[var_name] = intersection
        return bool(var_dict[var_name])

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

class RuleItem:
    def __init__(self, constraints : List[Constraint], annotation : Dict = None):
        self.constraints = {c.key : c for c in constraints if not c.isVariable } 
        self.variables = {c.key : c for c in constraints if c.isVariable}
        self.annotation = annotation if annotation else dict()
    def matches(self, item : NodeData, variable_dict : dict):
        for key, constraint in self.constraints.items():
            if not constraint.matches(item):
                return False
        for key, variable in self.variables.items():
            if not variable.process_variable(item, variable_dict):
                return False
        return True
    def to_node(self):
        return NodeData({k:v.values for k, v in self.constraints.items()})
    def to_text(self):
        text = (self.annotation[DEPREL_STR] + ':') if DEPREL_STR in self.annotation else ''
        text += self.constraints[TYPE_STR].values.get() if TYPE_STR in self.constraints else ''
        keys_less_type = [k for k in self.constraints if k != TYPE_STR]
        if not keys_less_type and not self.variables: return text
        text += '['
        text += ' '.join([self.constraints[k].to_text() for k in keys_less_type] + 
                         [self.variables[k].to_text() for k in self.variables])
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
        #create parent node. First add head data if there is any
        parent_node = NodeData()
        for child, candidate in zip(self.children, candidates):
            if(child.annotation.get(DEPREL_STR) == HEAD_STR):
                parent_node.update(candidate)
        #now add the parent_node data
        # parent_node = NodeData(self.parent.to_node())
        parent_node.update(self.parent.to_node())
        # look for variables
        # print(variable_dict)
        for key, var_name in self.parent.variables.items():
            var_name = var_name.values.get()
            value = variable_dict[var_name]
            # print(var_name, value)
            if value.isAll(): continue
            parent_node[key] = value
        # print(parent_node)
        return parent_node, [child.annotation for child in self.children]
    def to_text(self):
        return self.parent.to_text() + ' ::= ' + ' '.join([c.to_text() for c in self.children])
    def __str__(self):
        return self.to_text()
    def __repr__(self):
        return str(self)
