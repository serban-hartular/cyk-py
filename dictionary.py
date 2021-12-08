from collections import defaultdict


import pyconll

from rule import NodeData
from rule_io import TYPE_STR, FORM_STR, LEMMA_STR, UNKOWN_STR, POSITION_STR
from typing import List

import re

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

ud_word_dict['de'].remove(ud_word_dict['de'][1]) # remove 'foreign' de

punctuation_dict = {'PUNCT': 'COMMA'}

def word_dict_2_tree(form : str, word_rec : dict, id : str = None) -> cyk_parser.Tree:
    node_data = {k:list(v) for k,v in word_rec['data'].items()}
    if node_data.get(TYPE_STR)[0] in punctuation_dict: # replace punctuation
        node_data[TYPE_STR] = [punctuation_dict[node_data[TYPE_STR][0]]]
    node_data[FORM_STR] = form
    if id is not None:
        node_data[POSITION_STR] = id
    count = word_rec['count']
    tree = cyk_parser.Tree(NodeData(node_data))
    tree.score = count
    return tree

def word_2_parse_square(word : str, id : str = None, word_dict = ud_word_dict) -> cyk_parser.ParseSquare:
    form = word
    word = word.lower()
    if not word in word_dict: return None
    tree_list = [word_dict_2_tree(form, word_rec, id) for word_rec in word_dict[word]]
    score_sum = sum([tree.score for tree in tree_list])
    for tree in tree_list:
        tree.score = tree.score / score_sum
    return cyk_parser.ParseSquare(tree_list)

def text_2_square_list(text : str, remove_punct = True, word_dict = ud_word_dict) \
        -> (List[cyk_parser.ParseSquare], List[str]):
    split = re.split(r'[ \t\.,;:\\?!@#$%^&“„]', text)
    # split = re.split('\W+|(,)', text) # to do
    # split = [s for s in split if s]
    words = []
    unknown_words = []
    for atom in split:
        if not atom: continue
        if '-' in atom:
            words += separate_dashed_word(atom, word_dict)
        else:
            words.append(atom)
    sq_list = []
    for id, word in enumerate(words):
        sq = word_2_parse_square(word)
        if not sq:
            # raise Exception('Unkown word "%s"' % word)
            sq = cyk_parser.ParseSquare([cyk_parser.Tree(NodeData({TYPE_STR: UNKOWN_STR, FORM_STR: word}))]) # unknown
            unknown_words.append(word)
        # add ID
        for tree in sq:
            tree.data[POSITION_STR] = str(id+1)
        sq_list.append(sq)
    return sq_list, unknown_words

def separate_dashed_word(word : str, word_dict = ud_word_dict) -> List[str]:
    atoms = re.split('(-)', word)
    final_list = []
    while len(atoms) > 1:
        candidate = atoms[0] + atoms[1]
        if candidate.lower() in word_dict:
            final_list.append(candidate)
            atoms = atoms[2:]
        else:
            final_list.append(atoms[0])
            atoms = atoms[1:]
    if atoms:
        final_list.append(atoms[0])
    return final_list
