
from rule_io import parse_rule
from cyk_parser import Grammar
from rule import Constraint

def load_grammar(text : str):
    lines = text.split('\n')
    line_count = 0
    rule_list = list()
    group_dict = dict()
    for line in lines:
        line_count += 1
        line = line.strip()
        if not line or line[0] == '#': continue
        line = line.split('#', 1)[0]   # end-of-line comments
        if line.startswith('%%'):
            # do group instruction. Format: %%group Case,Gender,Number CGN
            line = line.split()
            if len(line) != 3 or line[0] != '%%group':
                print('Bad %%group instruction line ' + line_count)
                return None
            keys = line[1].split(',')
            group = line[2]
            group_dict[group] = keys
        else: # parse rule and deal with it
            try:
                rule = parse_rule(line)
            except:
                print('Parse error line ' + line_count)
                return None
            # search for groups to replace
            item_list = [rule.parent] + rule.children
            for rule_item in item_list:
                keys_to_pop = []
                constraints_to_add = []
                for key, constraint in rule_item:
                    if key not in group_dict: continue
                    group = group_dict[key]
                    new_constraints = [Constraint(g, constraint.values, constraint.isStrict, constraint.isNegated) \
                                            for g in group]
                    keys_to_pop.append(key)
                    constraints_to_add += new_constraints
                # now remove what is to be removed and add what is to be added
                for key in keys_to_pop:
                    rule_item.pop(key)
                rule_item.update({c.key:c for c in constraints_to_add})

            rule_list.append(rule)
    return Grammar(rule_list)