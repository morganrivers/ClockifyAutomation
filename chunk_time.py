import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
import pandas as pd
import datetime
import arrow
from ics import Event, Calendar
import copy
import numpy as np
df = pd.read_csv('data/combined_output_raw.csv')

df_sorted = df.sort_values(by='start_timestamp')
df_sorted.reset_index(drop=True, inplace=True)

df_sorted["duration"] = df_sorted["end_timestamp"]-df_sorted["start_timestamp"]
blk = 30*60  # 30 minute block

#use the majority amount of time in the block to assign the proper time code.
#if less than blk seconds total in that block, do not assign time to it.
time_start = df_sorted.loc[0].start_timestamp - df_sorted.loc[0].start_timestamp%blk
time_end = df_sorted.loc[len(df_sorted)-1].start_timestamp - df_sorted.loc[0].start_timestamp%blk + blk
df_new = pd.DataFrame()
for i in range(0,int(np.floor(time_end-time_start)/blk)):
    time_block_start = time_start+i*blk
    time_block_end = time_block_start+blk

    # select events which end after the block-start 
    # and start before the block-end
    events=df_sorted[df_sorted["end_timestamp"]>time_block_start][
    df_sorted["start_timestamp"]<time_block_end]
    # print(events)
    if(len(events)==0):
        continue

    durations = {}
    for index,event in events.iterrows():
        dpb = event["Description"]+"*"+event["Project"]+"*"+str(event["Billable"])

        # evaluate the total amount of time of each event in the block

        if(dpb not in durations.keys()):
            durations[dpb] = 0

        #add the duration to this block
        durations[dpb] = durations[dpb] + event["duration"]

        # if the event starts before the block, reduce its duration
        if(event["start_timestamp"] < time_block_start):
            durations[dpb] = \
                durations[dpb] - (time_block_start - event["start_timestamp"])

        # if the event ends after the block, reduce its duration
        if(event["end_timestamp"] > time_block_end):
            durations[dpb] = \
                durations[dpb] - (event["end_timestamp"] - time_block_end)


    #select the dominant event description
    max_keys = [key for key, value in durations.items() \
                if value == max(durations.values())]
    dominant_event = max_keys[0]
    dominant_event_duration = durations[max_keys[0]]

    tuple = dominant_event.split("*")
    description, project, billable = tuple

    #ignore if less than a minute during that half hour
    if(dominant_event_duration < 60):
        continue
    
    start_dt = datetime.datetime.fromtimestamp(int(time_block_start))
    end_dt = datetime.datetime.fromtimestamp(int(time_block_end))

    start_string = (start_dt).replace(microsecond=0).strftime('%Y-%m-%dT%T.000Z')
    end_string = (end_dt).replace(microsecond=0).strftime('%Y-%m-%dT%T.000Z')

    #merge with previous event if was the same (and ended at same as this start)
    if(len(df_new)>0 
        and df_new.loc[len(df_new)-1,"Description"]==description
        and int(df_new.loc[len(df_new)-1,"end_timestamp"]) == int(time_block_start)):
        df_new.loc[len(df_new)-1,"End Time"] = end_string
        df_new.loc[len(df_new)-1,"end_timestamp"] = time_block_end
    else: # create new event
        tmp = pd.DataFrame([{"Project":project,"Description":description,"Billable":billable,"Start Time":start_string,"End Time":end_string,"start_timestamp":time_block_start,"end_timestamp":time_block_end}])
        df_new = pd.concat([df_new, tmp], axis=0, ignore_index=True)

print(df_new)

df_chunks = df_new.sort_values(by='start_timestamp')
df_chunks.reset_index(drop=True, inplace=True)
df_chunks.to_csv("data/chunks.csv",index = False)

#build up a new calendar ics reflecting 
new_calendar = Calendar()

for index, row in df_chunks.iterrows():
    project = row['Project']
    description = row['Description']
    billable = row['Billable']
    start_timestamp = row['start_timestamp']
    end_timestamp = row['end_timestamp']
    #create copy of calendar for ease of error checking
    event = Event()
    if(billable):
        event.name = description+" "+project+" bill"
    else:
        event.name = description+" "+project+" no bill"

    event.begin = arrow.get(datetime.datetime.fromtimestamp(int(start_timestamp)))
    event.end = arrow.get(datetime.datetime.fromtimestamp(int(end_timestamp)))
    new_calendar.events.add(event)

with open('data/chunks.ics', 'w') as f:
    f.write(str(new_calendar))
