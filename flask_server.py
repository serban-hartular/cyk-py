from flask import Flask, send_from_directory
from flask import request
import json

import cyk.grammar

app = Flask(__name__)

# Path for our main Svelte page
@app.route("/")
def test():
    return send_from_directory('client/public', 'index.html')

# Path for all the static files (compiled JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory('client/public', path)

@app.route("/static/")
def static_dir_index():
    return send_from_directory("static", "index.html")


@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)


import dictionary
from cyk import grammar_loader, grammar, rule_io, guess_tree

# grammar_rules = '\n'.join(rom_cfg_nom.cfg_list + rom_cfg_verb.cfg_list)
# grammar = cyk_grammar_loader.load_grammar(grammar_rules)

# with open('rom_cfg_0.3.cfg', 'r', encoding='utf8') as fptr:
# # with open('./ro_locut.cfg', 'r', encoding='utf8') as fptr:
#     default_grammar = cyk_grammar_loader.load_grammar(fptr)

grammar_lines = []
with open('./ro_locut.cfg', 'r', encoding='utf8') as fptr:
    grammar_lines += fptr.readlines()
with open('rom_cfg_0.3.cfg', 'r', encoding='utf8') as fptr:
    grammar_lines += fptr.readlines()
default_grammar = cyk.grammar.Grammar(cyk.grammar_loader.load_rules(grammar_lines))


client_count = 0
client_data = dict()

from cyk.piecewise_parser import PiecewiseParser

@app.route("/get-client-id", methods=['POST'])
def get_client_id():
    global client_count
    grammar = default_grammar
    client_count += 1
    client_id = client_count
    client_data[client_id] = {'grammar':grammar, 
                              'parser': cyk.prob_parser.ProbabilisticParser(grammar),
                              'guesser':None,
                              'unknown_words':list()}

    grammar_strings = [str(rule) for rule in grammar._rules]
    return json.dumps({'client_id': client_id, 'grammar':grammar_strings})


@app.route("/parse", methods=['POST'])
def parse_text():
    # global parser
    # global unknown_words
    # parser = prob_parser.ProbabilisticParser(grammar)
    return_obj = {'error_msg':'', 'data':'', 'unknown':'', 'has_next_parse':str(False)}
    try: # get json obj
        json_obj = request.get_json()
    except Exception as e:
        return_obj['error_msg'] = str(e)
        return return_obj
    text = json_obj['text']
    client_id = json_obj.get('client_id')
    if not client_id:
        return_obj['error_msg'] = 'No client_id'
        return return_obj
    if not client_id in client_data:
        return_obj['error_msg'] = 'Client_id expired. Please reload page'
        return return_obj
    new_grammar = json_obj.get('grammar')
    if new_grammar is None: # if no rule list transmitted, use existing
        grammar = client_data[client_id]['grammar']
    else:
        if not new_grammar: # is empty
            grammar = default_grammar
        else:
            rule_text = '\n'.join(new_grammar)
            try:
                grammar = cyk.grammar.Grammar(cyk.grammar_loader.load_grammar(rule_text))
            except Exception as e:
                return_obj['error_msg'] = 'Grammar rule error: ' + str(e)
                return return_obj
        client_data[client_id]['grammar'] = grammar
        client_data[client_id]['parser'] = cyk.prob_parser.ProbabilisticParser(grammar)
        
    # get words
    sq_list, unknown = dictionary.text_2_square_list(text)
    client_data[client_id]['unknown_words'] = ', '.join(('"'+word+'"') for word in unknown)
    return_obj['unknown'] = client_data[client_id]['unknown_words'] 
    # parse
    parser = client_data[client_id]['parser']
    try:
        parser.input(sq_list)
        n = parser.next_parse()
        return_obj['has_next_parse'] = str(n != 0)
    except Exception as e:
        return_obj['error_msg'] = str(e)
        return return_obj

    return_obj['data'] = parser.to_jsonable()
    return_obj['unknown'] = client_data[client_id]['unknown_words']
    return json.dumps(return_obj)

@app.route("/next-parse", methods=['POST'])
def next_parse():
    # global parser
    # global unknown_words
    return_obj = {'error_msg':'', 'data':'', 'unknown':'', 'has_next_parse':str(False)}
    try:  # get json obj
        json_obj = request.get_json()
    except Exception as e:
        return_obj['error_msg'] = str(e)
        return return_obj
    client_id = json_obj.get('client_id')
    if not client_id:
        return_obj['error_msg'] = 'No client_id'
        return return_obj
    parser = client_data[client_id]['parser']

    n = parser.next_parse()
    return_obj['has_next_parse'] = str(n != 0)
    # except Exception as e:
    #     return_obj['error_msg'] = str(e)
    #     return return_obj
    return_obj['data'] = parser.to_jsonable()
    return_obj['unknown'] = client_data[client_id]['unknown_words']
    return json.dumps(return_obj)

import lark


@app.route("/guess-parse", methods=['POST'])
def guess_parse():
    # global parser
    # global unknown_words
    return_obj = {'error_msg':'', 'data':'', 'unknown':'',
                  'has_next_parse':str(False), 'has_next_guess':str(True)}
    try:  # get json obj
        json_obj = request.get_json()
    except Exception as e:
        return_obj['error_msg'] = str(e)
        return return_obj
    guess_root = json_obj.get('guess')
    if not guess_root:
        return_obj['error_msg'] = 'No guess root provided'
        return return_obj
    try:
        pp = lark.Lark(rule_io.grammar, start='item')
        tree = pp.parse('VP[a=2]')
        guess_data = rule_io.get_rule_item(tree).to_node()
    except Exception as e:
        return_obj['error_msg'] = 'guess string error: ' + str(e)
        return return_obj
    client_id = json_obj.get('client_id')
    if not client_id:
        return_obj['error_msg'] = 'No client_id'
        return return_obj
    parser = client_data[client_id]['parser']
    guesser = guess_tree.GuessTable(parser, guess_data) #NodeData({TYPE_STR:guess_root}))
    client_data[client_id]['guesser'] = guesser
    if not guesser.guess():
        return_obj['has_next_guess'] = str(False)
    data = guesser.to_jsonable()
    return_obj['unknown'] = client_data[client_id]['unknown_words']
    return_obj['data'] = data
    return json.dumps(return_obj)
    # guess_parser = parser.table_copy()
    # try:
    #     guess_tree.guess_tree(guess_parser, NodeData({TYPE_STR:guess_root}), add_guesses=True)
    #     return_obj['data'] = guess_parser.to_jsonable()
    #     return_obj['unknown'] = client_data[client_id]['unknown_words']
    # except Exception as e:
    #     return_obj['error_msg'] = str(e)
    #     return return_obj
    # return json.dumps(return_obj)

@app.route("/next-guess", methods=['POST'])
def next_guess():
    return_obj = {'error_msg':'', 'data':'', 'unknown':'',
                  'has_next_parse':str(False), 'has_next_guess':str(True)}
    try:  # get json obj
        json_obj = request.get_json()
    except Exception as e:
        return_obj['error_msg'] = str(e)
        return return_obj
    client_id = json_obj.get('client_id')
    if not client_id:
        return_obj['error_msg'] = 'No client_id'
        return return_obj
    guesser = client_data[client_id]['guesser']
    if not guesser.guess():
        return_obj['has_next_guess'] = str(False)
    data = guesser.to_jsonable()
    return_obj['unknown'] = client_data[client_id]['unknown_words']
    return_obj['data'] = data
    
    return json.dumps(return_obj)

import sys

if __name__ == "__main__":
    arg_dict = {'host':'127.0.0.1', 'port':'5000'}
    cmd_line = {arg.split('=',1)[0]:arg.split('=',1)[1] for arg in sys.argv if '=' in arg}
    arg_dict.update(cmd_line)
    app.run(debug=True, host=arg_dict['host'], port=int(arg_dict['port']))
