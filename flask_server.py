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

@app.route("/parse", methods=['POST'])
def parse_text():
    json_obj = None
    return_obj = {'error_msg':'', 'data':''}
    try: # get json obj
        json_obj = request.get_json()
    except Exception as e:
        return_obj['error_msg'] = str(e)
        return return_obj
    return_obj['data'] = json_obj
    print(json.dumps(return_obj))
    return json.dumps(return_obj)



if __name__ == "__main__":
    app.run(debug=True)
