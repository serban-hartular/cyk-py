

from lark import Lark, Tree, Token
from typing import List

from cyk.rule import Rule, RuleItem, Constraint
from cyk.rvalues import RValues

TYPE_STR = 'type'
FORM_STR = 'form'
DEPREL_STR = 'deprel'
LEMMA_STR = 'lemma'
HEAD_STR = 'h'
UNKOWN_STR = '##'
GUESS_STR = '?'
POSITION_STR = 'position'

grammar = """
%import common.WS
%ignore WS
%import common.ESCAPED_STRING   -> STRING

rule : item "::=" dependent_list

dependent_list  : dependent 
                | dependent_list dependent

dependent :     item
          |     VALUE ":" item

item    :   VALUE "[" constraint_list "]"
        |   VALUE

constraint_list :   constraint
                |   constraint_list constraint

constraint  : VALUE EQUALS values
            | VALUE STRICT_EQ values
            | VALUE INEQ values
            | VALUE STRICT_INEQ values

values :   VALUE
       |   values "," VALUE

VALUE : /[_@a-zA-Z0-9ăîâșțȘȚĂÎÂ\-]+/
EQUALS : "="
STRICT_EQ : "=="
INEQ : "!="
STRICT_INEQ : "!=="

"""

def get_list(tree : Tree):
    l = []
    for child in tree.children:
        if isinstance(child, Token):
            l += [child.value]
        else:
            l += get_list(child)
    return l

def get_constraint(tree : Tree) -> Constraint:
    assert tree.data == 'constraint'
    key = tree.children[0].value
    # isStrict = (tree.children[1].value == '==')
    # isNegated = (tree.children[1].value == '!=')
    isStrict = ('==' in tree.children[1].value)
    isNegated = ('!' in tree.children[1].value)
    if isNegated: isStrict = not isStrict
    values = get_list(tree.children[2])
    isVariable = (values[0].startswith('@'))
    if isVariable:
        if len(values) > 1: raise Exception('Variable can only have one item, not ' + str(values))
        values[0] = values[0].strip('@')
        if len(values[0]) == 0:
            values[0] = key
    return Constraint(key, RValues(values, isVariable), isStrict, isNegated)

# def get_constraint_dict(tree : Tree):
def get_constraint_list(tree : Tree):
    assert tree.data == 'constraint_list'
    # d = {}
    l = []
    for child in tree.children:
        if child.data == 'constraint':
            constraint = get_constraint(child)
            # d[constraint.key] = constraint
            l.append(constraint)
        else:
            # d.update(get_constraint_dict(child))
            l += get_constraint_list(child)
    return l #d

def get_rule_item(tree : Tree) -> RuleItem:
    assert tree.data == 'item'
    # d = {TYPE_STR : rule.Constraint(TYPE_STR, RValues([tree.children[0].value]), True)}
    constraints = [Constraint(TYPE_STR, RValues([tree.children[0].value]), True)]
    if(len(tree.children) > 1):
        # d.update(get_constraint_dict(tree.children[1]))
        constraints += get_constraint_list(tree.children[1])
    return RuleItem(constraints) #([c for c in d.values()])

def get_dependent_item(tree: Tree) -> RuleItem:
    assert tree.data == "dependent"
    if isinstance(tree.children[0], Token):
        deprel = tree.children[0].value
        i = 1
    else:
        deprel = None
        i = 0
    item = get_rule_item(tree.children[i])
    if deprel:
        item.annotation[DEPREL_STR] = deprel
    return item
        

def get_dependent_list(tree : Tree) -> list:
    l = []
    for child in tree.children:
        if child.data == 'dependent':
            l += [get_dependent_item(child)]
        else:
            l += get_dependent_list(child)
    return l

def get_rule(tree : Tree) -> Rule:
    assert tree.data == 'rule'
    return Rule(get_rule_item(tree.children[0]), get_dependent_list(tree.children[1]))

_parser = Lark(grammar, start='rule')

def parse_rule(text : str) -> Rule:
    tree = _parser.parse(text)
    return get_rule(tree)

def rule_list_from_string(text : str) -> List[Rule]:
    lines = text.split('\n')
    rules = []
    for line in lines:
        line = line.strip()
        if not line: continue
        rules.append(parse_rule(line))
    return rules
