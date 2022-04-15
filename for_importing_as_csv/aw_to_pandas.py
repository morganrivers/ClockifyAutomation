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

MONTH_OF_INTEREST = 3
YEAR = 2022
HOURS_OFF_UTC = -7

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



with open("aw-category-export.json", "r") as read_file:
     categories = json.load(read_file)['categories']

category_names = []
for c in categories:
    category_names.append(c['name'])


rules = []
for c in categories:
    rule=aw_transform.Rule(c)

    rule.regex=re.compile(c['rule']['regex'])
    # print(c['name_pretty'])
    rules.append((c['name_pretty'], rule))
categorized = aw_transform.categorize(window_events_this_month, rules)

# now we categorize all the existing timesheet data with the correct project, category, description, billable, attended

i=0
df=pd.DataFrame([])
df_start_date = []
df_start_time = []
df_start_timestamp = []
df_end_timestamp = []
df_duration = []
df_project = []
df_category = []
df_description = []
df_billable = []
df_task = []
df_email = []
df_user = []
df_tags = []
df_client = []

for cz in categorized:

    #not really sure why, but the parent's name doesn't seem to change, it should be Research - Miscellaneous*Research*Uncategorized research for ALLFED*Yes, but it's just "ALLFED"

    if(cz['data']['$category'][0]=="Uncategorized"):
        continue # uncategorized in this case
    # print(cz['data']['$category'])
    category_tree=cz['data']['$category'].split(">")
    if(category_tree[0] != "ALLFED"):
        continue
    if(len(category_tree)==1): # the "ALLFED" generic one
        tuple = ["Research - Miscellaneous","Research","Uncategorized research for ALLFED","Yes"]
    else:
        tuple = category_tree[1].split("*")
    # print(tuple)
    project, category, description, billable = tuple

    start_dt = cz['timestamp'] + timedelta(hours=HOURS_OFF_UTC) #convert to PST from UTC
    duration_delta=cz['duration']

    df_start_timestamp.append(start_dt.timestamp())
    df_end_timestamp.append((start_dt+duration_delta).timestamp())


    df_start_time.append(start_dt.time().replace(microsecond=0) )
    df_start_date.append(start_dt.strftime('%m/%d/%Y'))
    minutes = int((duration_delta.seconds%3600)/60)
    seconds = int((duration_delta.seconds%60))
    df_duration.append(str(int(duration_delta.seconds/60/60))+":"+str("%02d" % (minutes,))+":"+str("%02d" % (int(seconds),)))
    # print(df_duration)
    # print("summary")
    # print(summary)

    df_project.append(project)
    if(":" in category):
        c_and_t=category.split(":")[0]
        df_category.append(c_and_t[0])
        df_task.append(c_and_t[1])
    else:
        df_category.append(category)
        df_task.append("")

    df_description.append(description)
    df_billable.append(billable)
    df_email.append("morgan@allfed.info")
    # print("category")
    # print(category)
    # print("attend")
    # print(attend)
    # print("")
    # # if(not attend):
    # #     continuer

    df_user.append("morgan@allfed.info")
    df_tags.append("")
    df_client.append("morgan@allfed.info")

    i=i+1

print(i)
df['Client'] = df_client
df['Project'] = df_project
df['Description'] = df_description
df['Task'] = df_task
df['User'] = df_user
df['category'] = df_category
df['Email'] = df_email
df['Billable'] = df_billable
df['Start Date'] = df_start_date
df['Start Time'] = df_start_time
df['Duration (h)'] = df_duration
#useful for later comparison, not imported
df['start_timestamp'] = df_start_timestamp
df['end_timestamp'] = df_end_timestamp

print(df)
df.to_csv("activitywatch_output_raw.csv",index = False)
