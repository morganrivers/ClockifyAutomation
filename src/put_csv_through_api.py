import requests
import json
import pandas as pd
import time

def main():
    JSON_PARAMETERS_LOCATION = '../data/params.json'
    params = json.load(open(JSON_PARAMETERS_LOCATION, 'r'))

    CHUNKS_INPUT_CSV_LOCATION = '../data/chunked_events.csv'

    workspaceid = dict(params.items())["clockify_workspace_id"]

    print("please enter clockify API key")
    api_key = input()
    data = {'x-api-key': api_key}

    df = pd.read_csv(CHUNKS_INPUT_CSV_LOCATION)

    index = 0
    while index < len(df):
        row = df.iloc[index]
        time.sleep(1)

        # CHECK! if(row["Billable"]): # this might be correct?
        if(row["Billable"]):
            b = "true"
        else:
            b = "false"

        print(row["Project"])
        time_entry = {
            "start": row["Start Time"],
            "billable": b,
            "description": row["Description"],
            "projectId": row["Project"],
            "end": row["End Time"]
        }

        r = requests.post("https://api.clockify.me/api/v1/workspaces/" +
                          workspaceid+"/time-entries", json=time_entry, headers=data)

        print(time_entry)

        print(r)


        if(r.status_code != 201):
            if(r.status_code == 404):
                print("")
                print("Trying again, in case network is bad.")
                continue
            elif(r.status_code == 400):
                print("")
                print("Probably a mistake in the values if entered manually")
                print("Otherwise, check workspace/user id.")
                quit()

        index += 1

        print("")
        print("")


if __name__ == '__main__':
    main()
