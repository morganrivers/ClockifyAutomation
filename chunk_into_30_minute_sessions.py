
# NEEDS WORK

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import datetime
import arrow
from ics import Event, Calendar
import copy
import numpy as np
df = pd.read_csv('combined_output_raw.csv')

df_sorted = df.sort_values(by='start_timestamp')
df_sorted.reset_index(drop=True, inplace=True)

df_sorted["duration"] = df_sorted["end_timestamp"]-df_sorted["start_timestamp"]
#use the majority amount of time in the block to assign the proper time code.
#if less than 10 minutes total in that block, do not assign time to it.
time_start = df_sorted.loc[0].start_timestamp - df_sorted.loc[0].start_timestamp%(15*60)
time_end = df_sorted.loc[len(df_sorted)-1].start_timestamp - df_sorted.loc[0].start_timestamp%(15*60) + 15*60
for i in range(0,int(np.floor(time_end-time_start)/(15*60))):
    time_block_start = time_start+i*15*60
    time_block_end = time_block_start+15*60
    rows=df_sorted[df_sorted["start_timestamp"]<time_block_end
    if(len(rows)>0):
        continue
    rows_grouped=rows.groupby(['Description']).sum()

    print(rows_grouped)
quit()
# first pass: delete if less than 60 seconds in duration
i = 0
while i < len(df_sorted)-2:
    i = i + 1
    row = df_sorted.iloc[i]
    dur_1 = row["end_timestamp"] - row["start_timestamp"]
    next_row = df_sorted.iloc[i+1]
    if(dur_1 < 60):
        print("deleting short current")
        df_sorted.drop(axis=0,index=i, inplace=True)  # delete this event
        df_sorted.reset_index(drop=True, inplace=True)
        i=i-1
        continue

print("df<60")
print(df)

#second pass: get rid of simultaneous starts
i = 0
while i < len(df_sorted)-2:
    i = i + 1
    row = df_sorted.iloc[i]
    next_row = df_sorted.iloc[i+1]

    dur_1 = row["end_timestamp"] - row["start_timestamp"]
    dur_2 = next_row["end_timestamp"] - next_row["start_timestamp"]
    t_diff=next_row["start_timestamp"]-row["end_timestamp"] # space between events

    #if start simultaneously
    if(int(row["start_timestamp"]) == int(next_row["start_timestamp"])):

        #delete the shorter event
        if(dur_2 > dur_1):
            df_sorted.loc[i,"Description"] = next_row["Description"]
            df_sorted.loc[i,"end_timestamp"] = next_row["end_timestamp"]
            print("deleting simultaneously current")
            df_sorted.drop(axis=0,index=i, inplace=True)  # delete this event
        else:
            print("deleting simultaneously next")
            df_sorted.drop(axis=0,index=i+1, inplace=True)  # delete next event
        df_sorted.reset_index(drop=True, inplace=True)
        i=i-1
        continue
        print("deleted")

i = 0
while i < len(df_sorted)-3:
    i = i + 1
    row = df_sorted.iloc[i]
    next_row = df_sorted.iloc[i+1]
    next_next_row = df_sorted.iloc[i+2]

    dur_1 = row["end_timestamp"] - row["start_timestamp"]
    dur_2 = next_row["end_timestamp"] - next_row["start_timestamp"]
    dur_3 = next_row["end_timestamp"] - next_next_row["start_timestamp"]
    t_diff=next_row["start_timestamp"]-row["end_timestamp"] # space between events
    t_diff2=next_next_row["start_timestamp"]-row["end_timestamp"] # space between events

    print(i)
    if(row['Description']==next_row['Description']):
        print(row['Description'])

        # print(t_diff)
        assert(t_diff >= 0)

        if(t_diff < 600): # if identical event within 10 minutes
            print("t_diff")
            print(t_diff)

            print("duration")
            print("dur1")
            print(dur_1)
            print("dur_2")
            print(dur_2)
            print("")
            df_sorted.loc[i,"end_timestamp"] = next_row["end_timestamp"]
            df_sorted.drop(axis=0,index=i+1, inplace=True)  # delete next event
            print("deleting short time between next")
            print("next_row[Description")
            print(next_row["Description"])
            df_sorted.reset_index(drop=True, inplace=True)
            i = i - 1 # retest this index again with the next event
            continue

    #useful for deleting short interruptions in largely a certain project
    if(row['Description']==next_next_row['Description']):
        if(t_diff2 < 600):
            df_sorted.loc[i,"end_timestamp"] = next_next_row["end_timestamp"]
            df_sorted.drop(axis=0,index=i+1, inplace=True)  # delete sandwiched event
            df_sorted.drop(axis=0,index=i+2, inplace=True)  # delete nextnext event
            df_sorted.reset_index(drop=True, inplace=True)
            i = i - 1 # retest this index again with the next event
            continue

while i < len(df_sorted)-3:
    i = i + 1
    row = df_sorted.iloc[i]
    next_row = df_sorted.iloc[i+1]
    next_next_row = df_sorted.iloc[i+2]

    dur_1 = row["end_timestamp"] - row["start_timestamp"]
    dur_2 = next_row["end_timestamp"] - next_row["start_timestamp"]
    dur_3 = next_row["end_timestamp"] - next_next_row["start_timestamp"]
    t_diff=next_row["start_timestamp"]-row["end_timestamp"] # space between events
    t_diff2=next_next_row["start_timestamp"]-row["end_timestamp"] # space between events

    print(i)
    if(row['Description']==next_row['Description']):
        print(row['Description'])

        # print(t_diff)
        assert(t_diff >= 0)

        if(t_diff < 600): # if identical event within 10 minutes
            print("t_diff")
            print(t_diff)

            print("duration")
            print("dur1")
            print(dur_1)
            print("dur_2")
            print(dur_2)
            print("")
            df_sorted.loc[i,"end_timestamp"] = next_row["end_timestamp"]
            df_sorted.drop(axis=0,index=i+1, inplace=True)  # delete next event
            print("deleting short time between next")
            print("next_row[Description")
            print(next_row["Description"])
            df_sorted.reset_index(drop=True, inplace=True)
            i = i - 1 # retest this index again with the next event
            continue


print(df)
print(df_sorted)

#build up a new calendar ics reflecting 
new_calendar = Calendar()

for index, row in df_sorted.iterrows():
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

with open('combined.ics', 'w') as f:
    f.write(str(new_calendar))
