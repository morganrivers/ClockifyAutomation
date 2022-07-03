import re
import json
import pandas as pd
from datetime import datetime, timedelta, timezone

from aw_core.models import Event
from aw_client import ActivityWatchClient

import aw_transform
from aw_query.functions import filter_period_intersect
import aw_query

import json

CLOCKIFY_CATEGORIES_LOCATION = '../data/aw-category-export.json'
JSON_PARAMETERS_LOCATION = '../data/params.json'
OUTPUT_CSV_LOCATION = "../data/activitywatch_output_raw.csv"


class DateTimeEncoder(json.JSONEncoder):
    def default(self, z):
        if isinstance(z, datetime):
            return (str(z))
        elif isinstance(z, timedelta):
            return (str(z))
        else:
            return super().default(z)

def get_window_events_this_month(YEAR,MONTH_OF_INTEREST):
    client = ActivityWatchClient("test-client", testing=False)

    all_afk = client.export_all()['buckets']['aw-watcher-afk_snailshale']
    all_win = client.export_all()['buckets']['aw-watcher-window_snailshale']

    # run through json, convert afk to events type
    v = all_afk.items()
    events = []
    for item in list(list(list(v)[6])[1]):
        e = Event(timestamp=item['timestamp'],
                  duration=timedelta(seconds=item['duration']),
                  data={'status': item['data']['status']})
        events.append(e)

    not_afk_events = aw_query.functions.filter_keyvals(events, "status", ["not-afk"])

    # run through json, convert window to events type
    v = all_win.items()
    events = []
    for item in list(list(list(v)[6])[1]):
        duration = timedelta(seconds=item['duration'])
        e = Event(timestamp=item['timestamp'],
                  duration=duration,
                  data=item['data'])
        if(duration.seconds <= 10):  # remove any really short events
            continue

        events.append(e)

    window_events = aw_query.functions.filter_period_intersect(events, not_afk_events)
    print("len(window_events)")
    print(len(window_events))

    # exclude all events not during the month of interest
    start = datetime(YEAR, MONTH_OF_INTEREST, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
    end = datetime(YEAR, MONTH_OF_INTEREST+1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
    seconds = (end - start).total_seconds()

    whole_month = Event(timestamp=start,
                        duration=timedelta(seconds=seconds),
                        data={'status': "not-afk"})
    window_events_this_month = filter_period_intersect(window_events, [whole_month])

    with open("../data/aw_buckets.json", 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(window_events_this_month, indent=4,cls=DateTimeEncoder))

    return window_events_this_month

def get_rules():
    with open(CLOCKIFY_CATEGORIES_LOCATION, "r") as read_file:
        # with open("aw-category-export.json", "r") as read_file:
        categories = json.load(read_file)['categories']

    category_names = []
    for c in categories:
        category_names.append(c['name'])

    rules = []
    for c in categories:
        rule = aw_transform.Rule(c)

        rule.regex = re.compile(c['rule']['regex'])
        rules.append((c['name'], rule))
    return rules

def main(UNPROCESSED_AW_LOCATION):

    params = json.load(open(JSON_PARAMETERS_LOCATION, 'r'))

    hours_off_utc = dict(params.items())["hours_off_utc"]
    year = dict(params.items())["year"]
    month_of_interest = dict(params.items())["month_of_interest"]
    aw_work_tree_root = dict(params.items())["aw_work_tree_root"]

    MONTH_OF_INTEREST = month_of_interest
    YEAR = year
    HOURS_OFF_UTC = hours_off_utc

    window_events_this_month = get_window_events_this_month(YEAR,MONTH_OF_INTEREST)
    
    print("len(window_events_this_month)")
    print(len(window_events_this_month))

    rules = get_rules()

    categorized = aw_transform.categorize(window_events_this_month, rules)

    # now we categorize all the existing timesheet data with the correct project, category, description, billable, attended

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

        if(cz['data']['$category'][0] == "Uncategorized"):
            continue  # uncategorized in this case
        category_tree = cz['data']['$category']
        if(category_tree[0] != aw_work_tree_root):
            continue
        if(len(category_tree) == 1):  # the generic one
            tuple = [aw_work_tree_root.split("*")[0],
                     aw_work_tree_root.split("*")[1]]
        else:
            tuple = category_tree[1].split("*")
        description, project = tuple

        if("pdc" in description.lower()):
            billable = "false"
        else:
            billable = "true"

        start_dt = cz['timestamp'] + timedelta(hours=HOURS_OFF_UTC)  # convert to PST from UTC
        duration_delta = cz['duration']
        df_start_timestamp.append(start_dt.replace(microsecond=0).timestamp())
        df_end_timestamp.append((start_dt+duration_delta)
                                .replace(microsecond=0).timestamp())

        df_start_time.append(start_dt.replace(microsecond=0)
                                     .strftime('%Y-%m-%dT%T.000Z'))

        df_end_time.append(
            (start_dt+duration_delta).replace(microsecond=0).strftime('%Y-%m-%dT%T.000Z'))

        df_project.append(project)
        df_description.append(description)
        df_billable.append(billable)

        i = i+1

    df['Project'] = df_project
    df['Description'] = df_description
    df['Billable'] = df_billable
    df['Start Time'] = df_start_time
    df['End Time'] = df_end_time
    # useful for later comparison, not imported
    df['start_timestamp'] = df_start_timestamp
    df['end_timestamp'] = df_end_timestamp

    df.to_csv(OUTPUT_CSV_LOCATION, index=False)


if __name__ == '__main__':
    UNPROCESSED_AW_LOCATION = "../data/aw-category-export.json"
    main(UNPROCESSED_AW_LOCATION)
