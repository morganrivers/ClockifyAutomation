"""
File loads the raw buckets which were exported from activitywatch, then categorizes them.
When there are events accounting for a significant amount of time uncategorized, 
the user is prompted to categorize them.
"""
import pandas as pd
from aw_core.models import Event
from datetime import datetime, timedelta
import aw_transform
import json
import re

AW_BUCKETS_UNCLASSIFIED = "../data/aw_buckets.json"
CLOCKIFY_CATEGORIES_LOCATION = "../data/aw-category-export.json"
JSON_PARAMETERS_LOCATION = "../data/params.json"
OUTPUT_CSV_LOCATION = "../data/activitywatch_output_raw.csv"


# def read_uncategorized_aw_data():
#     # Load the JSON file into a Python dictionary
#     with open(AW_BUCKETS_UNCLASSIFIED, "r", encoding="utf-8") as jsonf:
#         data = json.load(jsonf)
#         return data


def get_rules():
    with open(CLOCKIFY_CATEGORIES_LOCATION, "r") as read_file:
        # with open("aw-category-export.json", "r") as read_file:
        categories = json.load(read_file)["categories"]

    category_names = []
    for c in categories:
        category_names.append(c["name"])

    rules = []
    for c in categories:
        rule = aw_transform.Rule(c)

        rule.regex = re.compile(c["rule"]["regex"])
        rules.append((c["name"], rule))
    return rules


def convert_categorized_data_to_csv(categorized):
    # now we convert categorized data  with the correct project, category, description, billable, attended, in a csv format

    params = json.load(open(JSON_PARAMETERS_LOCATION, "r"))

    hours_off_utc = dict(params.items())["hours_off_utc"]
    HOURS_OFF_UTC = hours_off_utc

    aw_work_tree_root = dict(params.items())["aw_work_tree_root"]

    i = 0
    df = pd.DataFrame([])
    df_start_time = []
    df_end_time = []
    df_start_timestamp = []
    df_end_timestamp = []
    df_project = []
    df_description = []
    df_billable = []
    for cz in categorized:
        # not really sure why, but the parent's name doesn't seem to change, it should be Research - Miscellaneous*Research*Uncategorized research for ALLFED*Yes, but it's just "ALLFED"

        if cz["data"]["$category"][0] == "Uncategorized":
            print("")
            print("Uncategorized!")
            print('cz["data"]["$category"]')
            print(cz["data"]["$category"])
            continue  # uncategorized in this case

        category_tree = cz["data"]["$category"]
        if category_tree[0] != aw_work_tree_root:
            print("")
            print("Categorized not work!")
            print('cz["data"]["$category"]')
            print(category_tree)

            continue
        if len(category_tree) == 1:  # the generic one
            split_by_asterisk_tuple = [aw_work_tree_root.split("*")[0], aw_work_tree_root.split("*")[1]]
        else:
            split_by_asterisk_tuple = category_tree[1].split("*")
        description, project = split_by_asterisk_tuple

        if "pdc" in description.lower():
            billable = "false"
        else:
            billable = "true"

        start_dt = cz["timestamp"] + timedelta(hours=HOURS_OFF_UTC)  # convert to PST from UTC
        duration_delta = cz["duration"]
        df_start_timestamp.append(start_dt.replace(microsecond=0).timestamp())
        df_end_timestamp.append((start_dt + duration_delta).replace(microsecond=0).timestamp())

        df_start_time.append(start_dt.replace(microsecond=0).strftime("%Y-%m-%dT%T.000Z"))

        df_end_time.append((start_dt + duration_delta).replace(microsecond=0).strftime("%Y-%m-%dT%T.000Z"))
        print("project + description")
        print(project + ", " + description)
        print("")
        df_project.append(project)
        df_description.append(description)
        df_billable.append(billable)

        i = i + 1

    df["Project"] = df_project
    df["Description"] = df_description
    df["Billable"] = df_billable
    df["Start Time"] = df_start_time
    df["End Time"] = df_end_time
    # useful for later comparison, not imported
    df["start_timestamp"] = df_start_timestamp
    df["end_timestamp"] = df_end_timestamp

    df.to_csv(OUTPUT_CSV_LOCATION, index=False)


def create_event_from_json(json_data):
    timestamp = datetime.fromisoformat(json_data["timestamp"])
    # Assuming 'duration' is represented as "HH:MM:SS.microseconds"
    hours, minutes, seconds = map(float, json_data["duration"].split(":"))
    duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
    data = json_data["data"]
    return Event(timestamp=timestamp, duration=duration, data=data)


def load_events_from_json(file_path):
    with open(file_path, "r", encoding="utf-8") as jsonf:
        json_events = json.load(jsonf)
        return [create_event_from_json(event_data) for event_data in json_events]


def main():
    print("")
    print("getting AW buckets from json..")

    rules = get_rules()

    # Use the loaded events to categorize them
    events = load_events_from_json(AW_BUCKETS_UNCLASSIFIED)

    categorized_events = aw_transform.categorize(events, rules)

    convert_categorized_data_to_csv(categorized_events)


if __name__ == "__main__":
    main()
