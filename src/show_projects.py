import requests
import json


def make_clockify_request(method, workspaceid, api_key):
    """Makes a POST or PUT request to the Clockify API based on the method specified."""
    headers = {"x-api-key": api_key}  # Ensure api_key is accessible here
    url = f"https://api.clockify.me/api/v1/workspaces/{workspaceid}/projects"

    r = requests.request(method, url, headers=headers)
    return r


def main():
    JSON_PARAMETERS_LOCATION = "../data/params.json"
    params = json.load(open(JSON_PARAMETERS_LOCATION, "r"))

    workspaceid = dict(params.items())["clockify_workspace_id"]

    print("Please enter clockify API key:")
    api_key = input()

    response = make_clockify_request(
        "GET",
        workspaceid,
        api_key,
    )

    print("")  # newline for readability
    if response.status_code == 200:
        projects = response.json()
        for project in projects:
            # Print each project's details
            print(f"Project Name: {project.get('name', 'N/A')}")
            print(f"Project ID: {project.get('id', 'N/A')}")
            print(f"Public: {project.get('public', 'N/A')}")
            if project.get("note", "N/A") != "":
                print(f"Note: {project.get('note', 'N/A')}")
            print("-" * 30)
    else:
        print("Failed to fetch projects. Status Code:", response.status_code)


if __name__ == "__main__":
    main()
