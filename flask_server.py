from flask import Flask, send_from_directory
from flask import request
import json

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
import rom_cfg_nom
import rom_cfg_verb
import cyk_grammar_loader

grammar_rules = '\n'.join(rom_cfg_nom.cfg_list + rom_cfg_verb.cfg_list)
grammar = cyk_grammar_loader.load_grammar(grammar_rules)
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
    try:
        sq_list = dictionary.text_2_square_list(text)
    except Exception as e:
        return_obj['error_msg'] = str(e)
        return return_obj
    parser.parse(sq_list)
    return_obj['data'] = parser.to_jsonable()
    # print(json.dumps(return_obj))
    return json.dumps(return_obj)



if __name__ == "__main__":
    app.run(debug=True)
