import requests
import json
import pandas as pd


def save_successful_post(time_entry, response_data):
    """Saves the successfully posted time entry with its ID to a JSON file."""
    file_path = "../data/already_posted_time.json"
    try:
        with open(file_path, "r") as file:
            already_posted = json.load(file)
    except FileNotFoundError:
        already_posted = []

    time_entry_with_id = {**time_entry, "id": response_data["id"]}
    already_posted.append(time_entry_with_id)
    with open(file_path, "w") as file:
        json.dump(already_posted, file, indent=4)


def is_already_posted(time_entry):
    """Checks if the time entry is already posted, ignoring the ID field."""
    file_path = "../data/already_posted_time.json"
    try:
        with open(file_path, "r") as file:
            already_posted = json.load(file)
            for posted_entry in already_posted:
                if all(
                    time_entry[k] == posted_entry[k] for k in time_entry if k != "id"
                ):
                    return True
        return False
    except FileNotFoundError:
        return False


def get_user_decision(description, start_time, end_time):
    """Asks the user for their decision on whether to re-upload a time entry."""
    while True:
        decision = input(
            f"\nReplace '{description}' ({start_time} - {end_time})? [y]es, [n]o, [A]ll, [N]one, [c]ancel: "
        ).strip()  # Strips whitespace and converts to lowercase

        if decision in ["y", "yes", "YES", "Yes"]:
            return "yes"
        elif decision in ["n", "no", "No", "NO"]:
            return "no"
        elif decision in ["a", "all", "A", "All", "ALL"]:
            return "all"
        elif decision in ["none", "None", "N", "NONE"]:
            return "none"
        elif decision in ["c", "cancel", "CANCEL", "Cancel"]:
            return "cancel"
        else:
            print("Invalid selection. Please try again.")


def make_clockify_request(method, workspaceid, time_entry, api_key, time_entry_id=None):
    """Makes a POST or PUT request to the Clockify API based on the method specified."""
    headers = {"x-api-key": api_key}  # Ensure api_key is accessible here
    url = f"https://api.clockify.me/api/v1/workspaces/{workspaceid}/time-entries"
    if method == "PUT":
        url += f"/{time_entry_id}"
        time_entry["id"] = time_entry_id

    r = requests.request(method, url, json=time_entry, headers=headers)
    return r


def get_time_entry_id(time_entry, json_file_path="../data/already_posted_time.json"):
    """Returns the ID of the time entry if it exists in the JSON file."""
    try:
        with open(json_file_path, "r") as file:
            time_entries = json.load(file)
            for entry in time_entries:
                if all(time_entry[k] == entry[k] for k in time_entry if k != "id"):
                    return entry["id"]
    except FileNotFoundError:
        print("JSON file not found.")
        return None
    return None


def main():
    JSON_PARAMETERS_LOCATION = "../data/params.json"
    params = json.load(open(JSON_PARAMETERS_LOCATION, "r"))

    CHUNKS_INPUT_CSV_LOCATION = "../data/chunked_events.csv"

    workspaceid = dict(params.items())["clockify_workspace_id"]

    api_key = dict(params.items())["clockify_api_key"]

    df = pd.read_csv(CHUNKS_INPUT_CSV_LOCATION)

    global_reupload_decision = None

    for index, row in df.iterrows():
        if row["Billable"]:
            b = "true"
        else:
            b = "false"

        time_entry = {
            "start": row["Start Time"],
            "billable": b,
            "description": row["Description"],
            "projectId": row["Project"],
            "end": row["End Time"],
        }

        decision = None
        if is_already_posted(time_entry):
            if global_reupload_decision == "none":
                continue
            elif global_reupload_decision != "all":
                decision = get_user_decision(
                    row["Description"], row["Start Time"], row["End Time"]
                )
                if decision == "n":
                    continue
                elif decision == "none":
                    global_reupload_decision = "none"
                    continue
                elif decision == "all":
                    global_reupload_decision = "all"
                elif decision == "c":
                    print("Uploading canceled by the user.")
                    return

            if global_reupload_decision == "all" or decision == "yes":
                time_entry_id = get_time_entry_id(time_entry)
                r = make_clockify_request(
                    "PUT", workspaceid, time_entry, api_key, time_entry_id
                )
                print("Updating time entry")
            else:
                continue
        else:
            print("\nCreating new time entry")
            r = make_clockify_request(
                "POST",
                workspaceid,
                time_entry,
                api_key,
            )

        print("Details:")
        print(time_entry)
        print("")

        if r.status_code == 201 or r.status_code == 200:
            response_data = r.json()
            print(f"Request made: {r.request.method} - {time_entry}")
            print(
                f"Event '{time_entry['description']}' ({time_entry['start']} - {time_entry['end']}) added/replaced."
            )
            save_successful_post(time_entry, response_data)
        elif r.status_code == 404:
            print("Trying again, in case network is bad.")
        else:
            print(f"Request made: {r.request.method} - {time_entry}")
            print(f"Response: {r.status_code} - {r.text}")

            print("Probably a mistake in the values if entered manually")
            print("Otherwise, check workspace/user id.")
            quit()

    print("\nSuccess! All events put to api. Exiting program.\n")


if __name__ == "__main__":
    main()
