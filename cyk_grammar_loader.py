
from rule_io import parse_rule
from cyk_grammar import Grammar
from rule import Constraint, VAR_PREFIX, Rule
from rvalues import RValues

COMMENT_STR = '#'

def load_rules(lines):
    if isinstance(lines, str):
        lines = lines.split('\n')
    line_count = 0
    rule_list = list()
    group_dict = dict()
    for line in lines:
        orig_line = str(line)
        line_count += 1
        line = line.strip()
        if not line or line[0] == COMMENT_STR: continue
        line = line.split(COMMENT_STR, 1)[0]   # end-of-line comments
        if line.startswith('%%alias'):
            # do group instruction. Format: %%alias Case,Gender,Number CGN
            line = line.split()
            if len(line) != 3:
                print('Bad %%alias instruction line ' + str(line_count) + '\n' + orig_line)
                return None
            keys = line[1].split(',')
            group = line[2]
            group_dict[group] = keys
        elif line.startswith('%score'):
            line = line.split()
            if(len(line) < 2):
                print('Bad %score line ' + str(line_count)  + '\n' + orig_line)
                return None
            try:
                score = float(line[1])
            except:
                print('Bad score value %s at line %d' % (line[1], line_count))
                return None
            if not rule_list:
                print('Score directive before any _rules at line %d, ignoring' % line_count)
                continue
            last = rule_list[-1]
            last.score = score
        elif line.startswith('%reverse'):
            if not rule_list:
                print('Reverse directive before any _rules at line %d, ignoring' % line_count)
                continue
            last = rule_list[-1]
            if len(last.children) < 2:
                print('Trying to reverse a rule with less than 2 children at line %d, ignoring' % line_count)
                continue
            r = Rule(last.parent, [last.children[1], last.children[0]])
            rule_list.append(r)
        else: # parse rule and deal with it
            try:
                rule = parse_rule(line)
            except:
                print('Parse error line ' + str(line_count)  + '\n' + orig_line)
                return None
            # search for groups to replace
            item_list = [rule.parent] + rule.children
            for rule_item in item_list:
                for dicts in [rule_item.constraints, rule_item.variables]:
                    keys_to_pop = []
                    constraints_to_add = []
                    for key, constraint in dicts.items():
                        if key not in group_dict: continue
                        group = group_dict[key]
                        isSimpleVar = (constraint.isVariable and constraint.values.get() == key)
                        new_constraints = [Constraint(item, RValues(item, True) if isSimpleVar else constraint.values, \
                                                      constraint.isStrict, constraint.isNegated) \
                                                      for item in group]
                        keys_to_pop.append(key)
                        constraints_to_add += new_constraints
                    # now remove what is to be removed and add what is to be added
                    for key in keys_to_pop:
                        dicts.pop(key)
                    dicts.update({c.key:c for c in constraints_to_add})

            rule_list.append(rule)
    return rule_list #Grammar(rule_list)

if __name__ == "__main__":
    grammar_text = """
        %%alias caz,gen CG
        %score 0.666
        NP[caz=@ gen=@] ::= N[CG=@]
        AdjP ::= Adj
        %reverse
        NP[caz=@1 gen=@2] ::= NP[caz=@2 gen=@1] AdjP
        %score 1.2
        """
    grammar = Grammar(load_rules(grammar_text))
