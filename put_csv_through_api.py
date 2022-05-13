import requests
import json
import pandas as pd
import time
workspaceid="5e56ce010121f031bdc3a7f2" # ALLFED

# workspaceid="62574afc85712a3bddd78faf" # test
print("please enter clockify API key")
api_key = input()
data = {'x-api-key': api_key}

df = pd.read_csv('data/manually_entered_march.csv')

for index, row in df.iterrows():
    time.sleep(1)
    if(row["Billable"]):
        b = "true"
    else:
        b = "false"

    # time_entry = {
    #   "start": "2022-03-12T13:48:14.000Z",
    #   "billable": "true",
    #   "description": "ukraine meetings",
    #   "projectId": "5f2da49c3afc991c82a2546b",
    #   "end": "2022-03-12T13:50:14.000Z"
    # }
    print(row["Project"])
    time_entry = {
      "start":row["Start Time"],
      "billable": b,
      "description": row["Description"],
      "projectId": row["Project"],
      "end": row["End Time"]
    }


    r = requests.post("https://api.clockify.me/api/v1/workspaces/"+workspaceid+"/time-entries", json=time_entry, headers=data)


    print(time_entry)

    print(r)

    if(r.status_code != 201):
        quit()

    print("")
    print("")
