import requests
import json
import pandas as pd
import time

def main():
    JSON_PARAMETERS_LOCATION = '../params.json'
    params = json.load(open(JSON_PARAMETERS_LOCATION, 'r'))

    CHUNKS_INPUT_CSV_LOCATION = '../data/chunked_events.csv'

    workspaceid = dict(params.items())["clockify_workspace_id"]

    # workspaceid="62574afc85712a3bddd78faf" # test
    print("please enter clockify API key")
    api_key = input()
    data = {'x-api-key': api_key}

    df = pd.read_csv(CHUNKS_INPUT_CSV_LOCATION)

    for index, row in df.iterrows():
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
            quit()

        print("")
        print("")


if __name__ == '__main__':
    main()
