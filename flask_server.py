from flask import Flask, send_from_directory
from flask import request
import json

from rule import NodeData
from rule_io import TYPE_STR

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

import cyk_parser
import dictionary
import cyk_grammar_loader
import guess_tree

# grammar_rules = '\n'.join(rom_cfg_nom.cfg_list + rom_cfg_verb.cfg_list)
# grammar = cyk_grammar_loader.load_grammar(grammar_rules)
with open('rom_cfg_0.1.cfg', 'r', encoding='utf8') as fptr:
    grammar = cyk_grammar_loader.load_grammar(fptr)

parser = cyk_parser.Parser(grammar)

@app.route("/parse", methods=['POST'])
def parse_text():
    json_obj = None
    return_obj = {'error_msg':'', 'data':''}
    try: # get json obj
        json_obj = request.get_json()
    except Exception as e:
        return_obj['error_msg'] = str(e)
        return return_obj
    text = json_obj['text']
    guess_root = json_obj['guess']
    try:
        sq_list, unknown_words = dictionary.text_2_square_list(text)
    except Exception as e:
        return_obj['error_msg'] = str(e)
        return return_obj
    parser.parse(sq_list)
    if not parser.root(): # no parse, try guessing
        guess_tree.guess_tree(parser, NodeData({TYPE_STR:guess_root}), add_guesses=True)
    return_obj['data'] = parser.to_jsonable()
    return json.dumps(return_obj)



if __name__ == "__main__":
    app.run(debug=True)
