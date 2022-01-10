from typing import List

import pyconll
from pyconll.unit.token import Token
from cyk.rule import NodeData, TYPE_STR
from cyk.rule_io import LEMMA_STR

filelist = ['../corpus_ud/ro_rrt-ud-dev.conllu'] #, '../corpus_ud/ro_rrt-ud-train.conllu', '../corpus_ud/ro_rrt-ud-test.conllu']

def tok_info(tok : Token) -> dict:
    attr_dict = {'upos':TYPE_STR, 'lemma':LEMMA_STR}
    info = {attr_v: tok.__getattribute__(attr_k).replace('.', '').replace('-', '')
             for attr_k, attr_v in attr_dict.items()}
    
    if tok.upos in ['NOUN', 'PRON', 'ADJ']:
        feats = tok.feats
        feat_keys = [k for k in ['Definite', 'Gender', 'Number', 'Case'] if k in feats]
        for k in feat_keys:
            info[k] = ','.join(feats[k])
    return info

to_latin = {'ș':'s','ț':'t', 'ă':'a', 'â':'a', 'î':'i', '-':'_', '.':'_'}
def to_rule_name(items : List[str]) -> str:
    l = []
    for item in items:
        item = item.lower()
        for k,v in to_latin.items():
            item = item.replace(k,v)
        l.append(item.upper())
    return '_'.join(l)

def expression_to_rules(expression : List[dict], name_dict : dict) -> str:
    """returns sequence of _rules with two children"""
    assert len(expression) > 1
    expression = list(expression)
    pair = expression[-2:]
    expression = expression[:-2]
    name = to_rule_name([str(n[LEMMA_STR]) for n in pair])
    if name in name_dict:
        # check if it's the same
        if name_dict[name] == pair:
            pass
        else:
            name += '_'
    name_dict[name] = pair
    while expression:
        last = expression.pop()
        new_name = to_rule_name([str(last[LEMMA_STR]), name])
        pair = [last, name]
        # new_rules.append([new_name, last, name])
        new_name += ('_' if new_name in name_dict and name_dict[new_name] != pair else '')
        name_dict[new_name] = pair
        name = new_name
    return name

expression_list = []

for filename in filelist:
    for sentence in pyconll.iter_from_file(filename):
        for token in sentence:
            if token.deprel == 'fixed':
                head_id = sentence[token.id].head
                fixed_head = tok_info(sentence[head_id])
                expr = [tok_info(t) for t in sentence if t.head == head_id and t.deprel == 'fixed']
                expression_list.append([fixed_head] + expr)

rule_dict = {}
heads = set()
for e in expression_list:
    h = expression_to_rules(e, rule_dict)
    heads.add(h)

for k,v in rule_dict.items():
    v = [i if isinstance(i, str) else str(NodeData(i)).replace('(', '[').replace(')', ']') for i in v]
    print(k + '\t::= ' + 'h:' + str(v[0]) + ' fixed:' + str(v[1]))
