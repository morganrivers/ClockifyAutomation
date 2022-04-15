import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import datetime
# Read CSV file into DataFrame df
df_aw = pd.read_csv('activitywatch_output_raw.csv') # activitywatch
df_gcal = pd.read_csv('calendar_output_raw.csv') # google calendar

#loop through each item in activitywatch. if it falls within a calendar output timeslot, then remove it.

combined_df=pd.DataFrame()

for index, row_aw in df_aw.iterrows():

    collides = False

    for index, row_gcal in df_gcal.iterrows():

        # collision detection
        if(row_gcal["start_timestamp"] <= row_aw["start_timestamp"] <= row_gcal["end_timestamp"]
           or row_gcal["start_timestamp"] <= row_aw["end_timestamp"] <= row_gcal["end_timestamp"]):
            collides = True

    if(not collides):
        # combined_df.append(row_aw)
        new_df = pd.DataFrame([row_aw])
        combined_df = pd.concat([combined_df, new_df], axis=0, ignore_index=True)

#collision detect calendar events, but only if they don't collide with any other calendar event
removed_indices = []
kept_indices = []
for index1, row_gcal1 in df_gcal.iterrows():

    if(index1 in removed_indices):
        continue

    for index2, row_gcal2 in df_gcal.iterrows():
        if(index1==index2):  # if collision is not with self
            continue
        # if(index1 == 31 and index2 == 35):
        #     print(row_gcal1["Description"])
        #     print(row_gcal1["Start Date"])
        #     print(row_gcal1["Start Time"])
        #     print(row_gcal1["start_timestamp"])
        #     print(row_gcal2["Description"])
        #     print(row_gcal2["Start Date"])
        #     print(row_gcal2["Start Time"])
        #     print(row_gcal2["start_timestamp"])
        #     print(row_gcal1["end_timestamp"]-row_gcal2["end_timestamp"])
        #     print(row_gcal1["start_timestamp"]-row_gcal2["start_timestamp"])
        #     quit()
        if(row_gcal1["start_timestamp"] < row_gcal2["start_timestamp"] < row_gcal1["end_timestamp"]
           or row_gcal1["start_timestamp"] < row_gcal2["end_timestamp"] < row_gcal1["end_timestamp"]
           or (row_gcal1["start_timestamp"] == row_gcal2["start_timestamp"]
               and row_gcal1["end_timestamp"] == row_gcal2["end_timestamp"])):

            removed_indices.append(index2) # we need to not add the offending event


for index, row_gcal in df_gcal.iterrows():
    if(index not in removed_indices):
        new_df = pd.DataFrame([row_gcal])
        combined_df = pd.concat([combined_df, new_df], axis=0, ignore_index=True)

combined_df.to_csv("combined_output_raw.csv",index = False)

print(combined_df)
