from flask import Flask, render_template, json

import os
import sys

module_path = os.path.abspath(os.path.join("../.."))
if module_path not in sys.path:
    sys.path.append(module_path)

from scripts.csv_to_json import make_json

app = Flask(__name__, static_folder="static")

CLOCKIFY_CATEGORIES_LOCATION = "../../data/aw-category-export.json"
AW_BUCKETS_LOCATION = "../../data/aw_buckets.json"
GCAL_BUCKETS_LOCATION = "../../data/calendar_output_raw.json"
JSON_PARAMETERS_LOCATION = "../../data/params.json"


@app.route("/")
def home():
    return render_template("index.html")
    # return "Hello world!"


# @app.route('/get_json')
# def hello():
#     data = {'username': 'Pang', 'site': 'stackoverflow.com'}
#     return render_template('settings.html', data=data)


@app.route("/api/<name>/")
def api_get_name(name):
    # Opening JSON file
    if name == "get_buckets":
        # params = json.load(open(AW_BUCKETS_LOCATION,'r'))
        # returns JSON object as
        # a dictionary

        # make_json('csvFilePath', jsonFilePath)
        pass

    if name == "load_json_categories":
        work_cats = {}
        params = json.load(open(JSON_PARAMETERS_LOCATION, "r"))
        aw_work_tree_root = dict(params.items())["aw_work_tree_root"]
        categories = json.load(open(CLOCKIFY_CATEGORIES_LOCATION, "r"))
        all_cats = categories["categories"]
        for item in all_cats:
            if item["name"][0] != aw_work_tree_root:
                continue
            if len(item["name"]) < 2:
                continue
            project_name = item["name"][1].split("*")[0]
            project_id = item["name"][1].split("*")[1]
            work_cats[project_name] = {}
            work_cats[project_name]["project_id"] = project_id
            work_cats[project_name]["rules"] = item["rule"]["regex"].split("|")

        return json.jsonify(work_cats)

    # not really used
    if name == "get_work_tree_root":
        # return aw_work_tree_root

        return json.jsonify({"aw_work_tree_root": aw_work_tree_root})

    return json.jsonify({"FAIL": "FAIL"})


if __name__ == "__main__":
    app.run()
