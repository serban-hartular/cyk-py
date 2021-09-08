

from lark import Lark, Tree, Token
from typing import List

import rule

TYPE_STR = 'type'
FORM_STR = 'form'
DEPREL_STR = 'deprel'
LEMMA_STR = 'lemma'


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

values :   VALUE
       |   values "," VALUE

VALUE : /[@a-zA-Z0-9]+/
EQUALS : "="
STRICT_EQ : "=="
INEQ : "!="

"""

def get_list(tree : Tree):
    l = []
    for child in tree.children:
        if isinstance(child, Token):
            l += [child.value]
        else:
            l += get_list(child)
    return l

def get_constraint(tree : Tree) -> (str, rule.Constraint):
    assert tree.data == 'constraint'
    key = tree.children[0].value
    isStrict = (tree.children[1].value == '==')
    isNegated = (tree.children[1].value == '!=')
    values = get_list(tree.children[2])
    return key, rule.Constraint(values, isStrict, isNegated)

def get_constraint_dict(tree : Tree):
    assert tree.data == 'constraint_list'
    d = {}
    for child in tree.children:
        if child.data == 'constraint':
            (key, constraint) = get_constraint(child)
            d[key] = constraint
        else:
            d.update(get_constraint_dict(child))
    return d

def get_rule_item(tree : Tree) -> rule.RuleItem:
    assert tree.data == 'item'
    d = {TYPE_STR : rule.Constraint([tree.children[0].value], True)}
    if(len(tree.children) > 1):
        d.update(get_constraint_dict(tree.children[1]))
    return rule.RuleItem(d)

def get_dependent_item(tree: Tree) -> rule.RuleItem:
    assert tree.data == "dependent"
    if isinstance(tree.children[0], Token):
        deprel = tree.children[0].value
        i = 1
    else:
        deprel = None
        i = 0
    item = get_rule_item(tree.children[i])
    if deprel: item[DEPREL_STR] = rule.Constraint([deprel])
    return item
        

def get_dependent_list(tree : Tree) -> list:
    l = []
    for child in tree.children:
        if child.data == 'dependent':
            l += [get_dependent_item(child)]
        else:
            l += get_dependent_list(child)
    return l

def get_rule(tree : Tree) -> rule.Rule:
    assert tree.data == 'rule'
    return rule.Rule(get_rule_item(tree.children[0]), get_dependent_list(tree.children[1]))

_parser = Lark(grammar, start='rule')

def parse_rule(text : str) -> rule.Rule:
    tree = _parser.parse(text)
    return get_rule(tree)

def rule_list_from_string(text : str) -> List[rule.Rule]:
    lines = text.split('\n')
    rules = []
    for line in lines:
        line = line.strip()
        if not line: continue
        rules.append(parse_rule(line))
    return rules
