import re
import json
import pandas as pd
from time import sleep
from datetime import datetime, timedelta, timezone

from aw_core.models import Event
from aw_client import ActivityWatchClient

import aw_transform
from aw_query.functions import filter_period_intersect
import aw_query

MONTH_OF_INTEREST = 4
YEAR = 2022
HOURS_OFF_UTC = 4

client = ActivityWatchClient("test-client", testing=False)

all_afk=client.export_all()['buckets']['aw-watcher-afk_snailshale']
all_win=client.export_all()['buckets']['aw-watcher-window_snailshale']

#run through json, convert afk to events type
v=all_afk.items()
events=[]
for item in list(list(list(v)[6])[1]):
    e = Event(timestamp=item['timestamp'],
               duration=timedelta(seconds=item['duration']),
               data={'status':item['data']['status']})
    events.append(e)



not_afk_events=aw_query.functions.filter_keyvals(events,"status", ["not-afk"])

# print(not_afk_events[0])
# quit()
#run through json, convert window to events type
v=all_win.items()
events=[]
for item in list(list(list(v)[6])[1]):
    duration=timedelta(seconds=item['duration'])
    e = Event(timestamp=item['timestamp'],
               duration=duration,
               data=item['data'])
    if(duration.seconds<=10): #remove any really short events
        continue

    events.append(e)

window_events = aw_query.functions.filter_period_intersect(events, not_afk_events);
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

print("len(window_events_this_month)")
print(len(window_events_this_month))



with open("data/aw-category-export.json", "r") as read_file:
# with open("aw-category-export.json", "r") as read_file:
     categories = json.load(read_file)['categories']

category_names = []
for c in categories:
    category_names.append(c['name'])

rules = []
for c in categories:
    rule=aw_transform.Rule(c)

    rule.regex=re.compile(c['rule']['regex'])
    # print(c['name_pretty'])
    rules.append((c['name'], rule))
categorized = aw_transform.categorize(window_events_this_month, rules)

# now we categorize all the existing timesheet data with the correct project, category, description, billable, attended

i=0
df=pd.DataFrame([])
df_start_time = []
df_end_time = []
df_start_timestamp = []
df_end_timestamp = []
df_project = []
df_description = []
df_billable = []
for cz in categorized:

    #not really sure why, but the parent's name doesn't seem to change, it should be Research - Miscellaneous*Research*Uncategorized research for ALLFED*Yes, but it's just "ALLFED"

    print(cz['data']['$category'])

    if(cz['data']['$category'][0]=="Uncategorized"):
        continue # uncategorized in this case
    # print(cz['data']['$category'])
    category_tree=cz['data']['$category']
    if(category_tree[0] != "Uncategorized research for ALLFED*5e56de580121f031bdc3afac"):
        continue
    if(len(category_tree)==1): # the "ALLFED" generic one
        tuple = ["Uncategorized research for ALLFED","5e56de580121f031bdc3afac"]
    else:
        tuple = category_tree[1].split("*")
    print(tuple)
    description, project = tuple

    if("pdc" in description.lower()):  
        billable="false"
    else:
        billable="true"

    start_dt = cz['timestamp'] + timedelta(hours=HOURS_OFF_UTC) #convert to PST from UTC
    print(start_dt)
    duration_delta=cz['duration']
    df_start_timestamp.append(start_dt.replace(microsecond=0).timestamp())
    df_end_timestamp.append((start_dt+duration_delta).replace(microsecond=0).timestamp())


    df_start_time.append(start_dt.replace(microsecond=0).strftime('%Y-%m-%dT%T.000Z'))

    df_end_time.append((start_dt+duration_delta).replace(microsecond=0).strftime('%Y-%m-%dT%T.000Z'))

    df_project.append(project)
    df_description.append(description)
    df_billable.append(billable)

    i=i+1

print(i)
df['Project'] = df_project
df['Description'] = df_description
df['Billable'] = df_billable
df['Start Time'] = df_start_time
df['End Time'] = df_end_time
#useful for later comparison, not imported
df['start_timestamp'] = df_start_timestamp
df['end_timestamp'] = df_end_timestamp

print(df)
df.to_csv("data/activitywatch_output_raw.csv",index = False)
