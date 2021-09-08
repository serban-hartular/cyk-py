from collections import defaultdict


import pyconll

from rule import NodeData
from rule_io import TYPE_STR, FORM_STR, LEMMA_STR
from typing import List

def generate_word_dict():
    path = r'C:\Users\ffxvtj\Documents\Projects\Lingv\Corpus\\'
    filenames = [r'ro_rrt-ud-train.conllu', r'ro_rrt-ud-dev.conllu', r'ro_rrt-ud-test.conllu']
    words = defaultdict(list)
    for filename in filenames:
        conll = pyconll.iter_from_file(path + filename)
        for sentence in conll:
            for token in sentence:
                form = token.form.lower()
                type = token.upos
                lemma = token.lemma
                data = dict(token.feats)
                data[TYPE_STR] = {type}
                data[FORM_STR] = {form}
                data[LEMMA_STR] = {lemma}
                same_dict = [d for d in words[form] if d['data'] == data]
                if not same_dict:
                    words[form].append({'data':data, 'count':1})
                else:
                    same_dict[0]['count'] += 1
    return words

import pickle
import cyk_parser

ud_word_dict_filename = 'ud-word-dict.p'
infile = open(ud_word_dict_filename, 'rb')
ud_word_dict = pickle.load(infile)
infile.close()

def word_dict_2_tree(word_rec : dict) -> cyk_parser.Tree:
    node_data = {k:list(v) for k,v in word_rec['data'].items()}
    count = word_rec['count']
    tree = cyk_parser.Tree(NodeData(node_data))
    tree.score = count
    return tree

def word_2_parse_square(word : str, word_dict = ud_word_dict) -> cyk_parser.ParseSquare:
    word = word.lower()
    if not word in word_dict: return None
    tree_list = [word_dict_2_tree(word_rec) for word_rec in word_dict[word]]
    score_sum = sum([tree.score for tree in tree_list])
    for tree in tree_list:
        tree.score = tree.score / score_sum
    return cyk_parser.ParseSquare(tree_list)

def text_2_square_list(text : str, remove_punct = True, word_dict = ud_word_dict) -> List[cyk_parser.ParseSquare]:
    words = text.split()
    return [word_2_parse_square(w) for w in words]

