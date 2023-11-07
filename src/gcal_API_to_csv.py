from __future__ import print_function

import calendar
import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz  # Make sure to have the pytz library if you want to handle timezones

import pandas as pd
import datetime
from datetime import timedelta, timezone
import arrow
import json

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def get_service():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("../data/token.json"):
        creds = Credentials.from_authorized_user_file("../data/token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "../data/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("../data/token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        return service

    except HttpError as error:
        print("An error occurred: %s" % error)


def update_categories(new_category, data, JSON_CATEGORIES_LOCATION):
    """Updates the categories JSON file with a new category."""
    with open(JSON_CATEGORIES_LOCATION, "w") as f:
        json.dump(data, f, indent=4)


def get_project_selection(data, new_project):
    """Returns a list of categories associated with the given project ID."""
    associated_categories = []
    for name, details in data.get("categories", {}).items():
        if details["project"] == new_project:
            associated_categories.append(f'"{name}"')
    return ", ".join(associated_categories)


def classify(summary, data, JSON_CATEGORIES_LOCATION):
    slow = summary.lower()
    default = data.get("default", {})
    cats = data.get("categories", {})

    # Existing category check
    for k, i in cats.items():
        if slow in k.lower() or k.lower() in slow:
            return (i.get("description"), i.get("project"), i.get("billable"))

    print("Here are the existing categories for each project ID:")
    for project_id in set(details["project"] for details in cats.values()):
        associated_categories = get_project_selection(data, project_id)
        print(f"{project_id}: {associated_categories}")

    # No match found
    print("Unmatched calendar item:", summary)

    print(
        'Enter the description to show on the timesheet for this event, enter "p" for personal event (not work'
    )
    entered_description = input(
        'related) or just hit enter to categorize this as "default generic research project": '
    )

    if entered_description == "p":
        new_description = summary
        new_project = "personal"
        new_billable = "False"
    elif entered_description == "":
        new_description = default["description"]
        new_project = default["project"]
        new_billable = default["billable"]
    else:
        new_description = entered_description
        while True:
            new_project = input(
                "Enter the project ID for this event, or type 'list' to see existing categories: "
            )
            if new_project == "list":
                print("Here are the existing categories for each project ID:")
                for project_id in set(details["project"] for details in cats.values()):
                    associated_categories = get_project_selection(data, project_id)
                    print(f"{project_id}: {associated_categories}")
            else:
                break
        new_billable = input("Is this event billable? (True/False): ")

    # Update the categories
    new_category = {
        summary: {
            "description": new_description,
            "project": new_project,
            "billable": new_billable,
        }
    }
    data["categories"].update(new_category)

    update_categories(new_category, data, JSON_CATEGORIES_LOCATION)

    print("")
    print("New category added to the gcal filter json successfully!")
    print(new_category)
    print("")

    return (
        new_category[summary]["description"],
        new_category[summary]["project"],
        new_category[summary]["billable"],
    )


# use an exported AW categories list and the AW API to get the data, then
# run through the categorization, as well as create an output CSV and ICS
# representing the data
def main():
    INPUT_CALENDAR_LOCATION = "../data/gcal_shortened.ics"
    CALENDAR_EVENTS_OUTPUT_CSV_LOCATION = "../data/calendar_output_raw.csv"
    CALENDAR_EVENTS_OUTPUT_ICS_LOCATION = "../data/calendar_output_raw.ics"
    JSON_CATEGORIES_LOCATION = "../data/gcal_categories.json"
    JSON_PARAMETERS_LOCATION = "../data/params.json"

    params = json.load(open(JSON_PARAMETERS_LOCATION, "r"))
    data = json.load(open(JSON_CATEGORIES_LOCATION, "r"))

    hours_off_utc = dict(params.items())["hours_off_utc"]
    your_email = dict(params.items())["your_email"]
    month_of_interest = dict(params.items())["month_of_interest"]
    day_range = dict(params.items())["day_range"]
    year = dict(params.items())["year"]

    HOURS_OFF_UTC = hours_off_utc
    YOUR_EMAIL = your_email
    YEAR = year
    MONTH_OF_INTEREST = month_of_interest
    DAY_RANGE = day_range

    # Get the current time in RFC3339 format
    now = datetime.datetime.utcnow().isoformat() + "Z"

    service = get_service()

    if day_range == "all":
        # First and last day of the month
        start_day = 1
        end_day = calendar.monthrange(int(year), int(month_of_interest))[
            1
        ]  # This gets the last day of the month
    else:
        # Specific range of days
        start_day, end_day = day_range

    # Create timezone-aware datetime objects for the start and end of the period
    timezone = pytz.timezone(
        "UTC"
    )  # Replace with your timezone, e.g., "UTC", "Europe/Berlin", etc.
    start_of_period = timezone.localize(
        datetime.datetime(int(year), int(month_of_interest), start_day)
    )
    end_of_period = timezone.localize(
        datetime.datetime(int(year), int(month_of_interest), end_day, 23, 59, 59)
    )  # end of day_range[1]

    # Convert to RFC3339 format
    time_min = start_of_period.isoformat()
    time_max = end_of_period.isoformat()

    # Use these in your API request
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = events_result.get("items", [])

    if not events:
        print("No upcoming events found.")
    else:
        df = pd.DataFrame([])
        df_start_time = []
        df_end_time = []
        df_start_timestamp = []
        df_end_timestamp = []
        df_project = []
        df_description = []
        df_billable = []

        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))

            if not start or not end:
                continue

            startdt = arrow.get(start).datetime
            enddt = arrow.get(end).datetime
            duration = enddt - startdt

            if duration.total_seconds() >= 7 * 3600:  # remove any really long events
                continue

            if duration.total_seconds() <= 10:  # remove any really short events
                continue

            # Check for user acceptance
            accept = any(
                attendee.get("email") == YOUR_EMAIL
                and attendee.get("responseStatus") in ["accepted", "tentative"]
                for attendee in event.get("attendees", [])
            )

            if not accept:
                continue

            summary = event["summary"]
            description, project, billable = classify(
                summary, data, JSON_CATEGORIES_LOCATION
            )

            if project == "personal" and not (billable.lower() == "true"):
                print(f"IGNORING {description} as it is not work related.")
                continue

            utc = timezone
            startdt_utc = startdt.replace(tzinfo=utc)
            enddt_utc = enddt.replace(tzinfo=utc)

            df_start_timestamp.append(startdt_utc.timestamp())
            df_end_timestamp.append(enddt_utc.timestamp())
            df_start_time.append(startdt_utc.strftime("%Y-%m-%dT%T.000Z"))
            df_end_time.append(enddt_utc.strftime("%Y-%m-%dT%T.000Z"))

            df_project.append(project)
            df_description.append(description)
            df_billable.append(billable.lower())

        # Build the DataFrame
        df["Project"] = df_project
        df["Description"] = df_description
        df["Billable"] = df_billable
        df["Start Time"] = df_start_time
        df["End Time"] = df_end_time
        df["start_timestamp"] = df_start_timestamp
        df["end_timestamp"] = df_end_timestamp

        # Save DataFrame to CSV
        df.to_csv(CALENDAR_EVENTS_OUTPUT_CSV_LOCATION, index=False)
        print("Calendar csv categorized.")


if __name__ == "__main__":
    main()
