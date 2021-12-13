from dictionary import text_2_square_list, word_2_parse_square
from cyk_parser import Parser
from cyk_grammar import Grammar
import cyk_grammar_loader

import time

import rom_cfg_nom
import rom_cfg_verb
from prob_parser import ProbabilisticParser

grammar_lines = []
with open('./ro_locut.cfg', 'r', encoding='utf8') as fptr:
    grammar_lines += fptr.readlines()
with open('rom_cfg_0.3.cfg', 'r', encoding='utf8') as fptr:
    grammar_lines += fptr.readlines()
grammar = Grammar(cyk_grammar_loader.load_rules(grammar_lines))
    
# parser_old = Parser(grammar)
parser = ProbabilisticParser(grammar)
def parse(text : str, _parser : ProbabilisticParser = parser):
    sq_list, unknown = text_2_square_list(text)
    if unknown:
        print('Unkown: ' + ', '.join(unknown))
    _parser.input(sq_list)
    return _parser.next_parse()

from guess_tree import *
from cyk_parser import *

from ud_train.convert_to_ud import *
from ud_train.process_conllu import *
import pyconll


incomplete = ['dev-692', 'dev-312', 'dev-450', 'dev-31', 'dev-27', 'dev-37', 'dev-36', 'dev-28']
dicendi = ['dev-34', 'dev-47', 'dev-26', 'dev-70', 'dev-448']
long = ['dev-12', 'dev-8', 'dev-502', 'dev-244']
bad_tag = ['dev-299', 'dev-713']
modal = ['dev-443', 'dev-444', 'dev-180']
npe = ['dev-452', 'dev-211']
list_item = ['dev-543'] # 3. Se spala tra la la 
long_bad = ['dev-471']

good_parses = []
bad_parses = []

stop_at = 'dev-356'

import cyk_rule_counter

counter = cyk_rule_counter.RuleCounter()

if __name__ == '__main__':
    filename = './corpus_ud/ro_rrt-ud-dev.conllu'
    # filename = './test.conll'

    conll = pyconll.load_from_file(filename)
    # sort by shortest
    sentence_list = [s for s in conll]
    sentence_list.sort(key=lambda s: len(s))
    for sentence in sentence_list:
        if sentence.id == stop_at:
            break
        if sentence.id in (incomplete + dicendi + bad_tag + modal + npe + list_item + long_bad):
            continue
        print(sentence.id, sentence.text)
        # get a parsed sentence
        ud_tokens = elim_upos_from_conllu(sentence, ['PUNCT', 'INTJ'])
        # feed tokens to dictionary for sq_list
        sq_list = [word_2_parse_square(token.form, str(i+1)) for i, token in enumerate(ud_tokens)]
        parser.input(sq_list)
        # look for parse that matches
        matching_parse = None
        tic = time.perf_counter()
        toc = tic
        while parser.next_parse() > 0:
            toc = time.perf_counter()
            if not parser.root():
                continue
            tree = parser.root()[-1]
            node_list = UD_Node.token_list(to_ud(tree)[0])
            if not UD_Node.differences(node_list, ud_tokens):
                matching_parse = tree
                break
            if toc - tic > 75:  # 90 secs
                break
        print('dt = ' + str(toc-tic))
        if matching_parse is None: # didn't find parse
            print("Couldn't find parse for {}: '{}'".format(sentence.id, sentence.text))
            bad_parses.append(sentence.id)
        else:
            good_parses.append(sentence.id)
            counter.add_tree(matching_parse)

print('Bad parses:' + '\n'.join(bad_parses))
r = list(counter.get_rules())
# r = parser.root()[0]
# nl = UD_Node.token_list(to_ud(r)[0])
# nl.sort(key=lambda n : int(n.id))
# print('\n'.join([str(n) for n in nl]))