from cyk.rule_counter import RuleCounter
from dictionary import text_2_square_list, word_2_parse_square
from cyk.grammar import Grammar
from cyk import grammar_loader, rule_counter

import time

from cyk.prob_parser import ProbabilisticParser
import cyk.grammar_loader

grammar_lines = []
with open('./ro_locut.cfg', 'r', encoding='utf8') as fptr:
    grammar_lines += fptr.readlines()
with open('rom_cfg_0.3.cfg', 'r', encoding='utf8') as fptr:
    grammar_lines += fptr.readlines()
grammar = Grammar(cyk.grammar_loader.load_rules(grammar_lines))
    
# parser_old = Parser(grammar)
parser = ProbabilisticParser(grammar)
def parse(text : str, _parser : ProbabilisticParser = parser):
    sq_list, unknown = text_2_square_list(text)
    if unknown:
        print('Unkown: ' + ', '.join(unknown))
    _parser.input(sq_list)
    return _parser.next_parse()


from ud_train.convert_to_ud import *
from ud_train.process_conllu import *
import pyconll


not_proj = ['dev-312', 'dev-450', 'dev-31', 'dev-443', 'dev-36', 'dev-444', 'dev-28', 'dev-180', 'dev-318', 'dev-437', 'dev-440', 'dev-516', 'dev-334', 'dev-600', 'dev-290', 'dev-366', 'dev-445', 'dev-75', 'dev-198', 'dev-286', 'dev-451', 'dev-229', 'dev-511', 'dev-630', 'dev-633', 'dev-92', 'dev-59', 'dev-181', 'dev-288', 'dev-251', 'dev-377', 'dev-701', 'dev-60', 'dev-405', 'dev-536', 'dev-273', 'dev-259', 'dev-381', 'dev-14', 'dev-101', 'dev-185', 'dev-325', 'dev-387', 'dev-274', 'dev-383', 'dev-19', 'dev-149', 'dev-190', 'dev-463', 'dev-469', 'dev-559', 'dev-53', 'dev-10', 'dev-724', 'dev-145', 'dev-674', 'dev-565', 'dev-676', 'dev-454', 'dev-466', 'dev-695', 'dev-591', 'dev-310', 'dev-716', 'dev-456', 'dev-562', 'dev-714', 'dev-160', 'dev-698', 'dev-7', 'dev-679', 'dev-683', 'dev-152', 'dev-148']
incomplete = ['dev-692', 'dev-312', 'dev-450', 'dev-31', 'dev-27', 'dev-37', 'dev-36', 'dev-28', \
              'dev-339', 'dev-468', 'dev-307', 'dev-528']
dicendi = ['dev-34', 'dev-47', 'dev-26', 'dev-70', 'dev-448']
modal = ['dev-352']
npe = ['dev-452', 'dev-211', 'dev-500', 'dev-509', 'dev-564']
restant = ['dev-302', 'dev-55'] # mii de ani (dezacord gen)
bad_annot = ['dev-67', 'dev-511']
list_item = ['dev-600']

succesful_10min_parses = ['dev-57', 'dev-687', 'dev-46', 'dev-287', 'dev-298', 'dev-317', 'dev-326', 'dev-18', 'dev-32', 'dev-297', 'dev-5', 'dev-6', 'dev-35', 'dev-44', 'dev-291', 'dev-320', 'dev-439', 'dev-449', 'dev-501', 'dev-733', 'dev-12', 'dev-33', 'dev-69', 'dev-280', 'dev-311', 'dev-447', 'dev-486', 'dev-8', 'dev-173', 'dev-61', 'dev-119', 'dev-163', 'dev-195', 'dev-285', 'dev-489', 'dev-502', 'dev-507', 'dev-73', 'dev-303', 'dev-471', 'dev-610', 'dev-615', 'dev-616', 'dev-39', 'dev-289', 'dev-295', 'dev-358', 'dev-364', 'dev-365', 'dev-539', 'dev-554', 'dev-29', 'dev-49', 'dev-203', 'dev-215', 'dev-226', 'dev-239', 'dev-356', 'dev-4', 'dev-88', 'dev-293', 'dev-343', 'dev-363', 'dev-426', 'dev-427', 'dev-606', 'dev-85', 'dev-208', 'dev-292', 'dev-350', 'dev-390', 'dev-453', 'dev-508', 'dev-731', 'dev-678', 'dev-353', 'dev-369', 'dev-133', 'dev-729']
# ten minute limit


no_do = not_proj + incomplete + dicendi + modal + npe + restant + bad_annot + list_item + succesful_10min_parses


good_parses = []
bad_parses = []
no_parses = []

timeout = 60*60

counter = RuleCounter()

if __name__ == '__main__':
    filename = './corpus_ud/ro_rrt-ud-dev.conllu'
    # filename = './test.conll'

    conll = pyconll.load_from_file(filename)
    # sort by shortest
    sentence_list = [s for s in conll]
    sentence_list.sort(key=lambda s: len(s))
    for sentence in sentence_list:
        if sentence.id in no_do:
            continue
        has_shit = False
        for i, token in enumerate(sentence):
            if token.upos in ['SYM', 'INTJ'] or (token.upos in ['PUNCT'] and i != len(sentence)-1):
                has_shit = True
                break
        if has_shit:
            continue
        ud_tokens = elim_upos_from_conllu(sentence, ['PUNCT', 'INTJ'])
        # feed tokens to dictionary for sq_list
        sq_list = [word_2_parse_square(token.form, str(i+1)) for i, token in enumerate(ud_tokens)]
        # print(sq_list)
        parser.input(sq_list)
        # look for parse that matches
        matching_parse = None
        tic = time.perf_counter()
        toc = tic
        print(sentence.id, sentence.text)
        while parser.next_parse() > 0:
            toc = time.perf_counter()
            if toc - tic > timeout:  # 75 secs
                break
            if not parser.root():
                continue
            tree = parser.root()[-1]
            node_list = UD_Node.token_list(to_ud(tree)[0])
            if not UD_Node.differences(node_list, ud_tokens):
                matching_parse = tree
                break
        # print('dt = ' + str(toc-tic))
        if matching_parse is None: # didn't find parse
            if parser.root():
                print('Bad parse %s after %s s' % (sentence.id, str(toc-tic)))
                bad_parses.append(sentence.id)
            else:
                print('No parse %s after %s s' % (sentence.id, str(toc-tic)))
                no_parses.append(sentence.id)
        else:
            good_parses.append(sentence.id)
            counter.add_tree(matching_parse)

#bad ['dev-294', 'dev-358', 'dev-554', 'dev-49', 'dev-352']
#timeout ['dev-742', 'dev-306', 'dev-322']
