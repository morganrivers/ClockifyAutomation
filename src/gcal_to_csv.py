import pandas as pd
from ics import Calendar, Event
import datetime
from datetime import timedelta, timezone
from dateutil import tz
import pytz
import arrow
import json


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

    def classify(summary):
        slow = summary.lower()
        default = data["default"]
        cats = data["categories"]
        for k, i in cats.items():
            if slow in k.lower() or k.lower() in slow:
                return (i["description"], i["project"], i["billable"])

        print("Unmatched calendar item")
        print(summary)
        print("")

        entered_description = input(
            "Enter the description for this event, or just hit enter to always categorize this as a default generic research project: "
        )
        if entered_description == "":
            new_description = default["description"]
            new_project = default["project"]
            new_billable = default["billable"]
        else:
            new_description = entered_description
            while True:
                new_project = input("Enter the project ID for this event, or type 'list' to see existing categories: ")
                if new_project == "list":
                    print("Here are the existing categories for each project ID:")
                    for project_id in set(details["project"] for details in cats.values()):
                        associated_categories = get_project_selection(data, project_id)
                        print(f"{project_id}: {associated_categories}")
                else:
                    break
            new_billable = input("Is this event billable? (True/False): ")

        # Update the categories with the new user-provided information
        new_category = {summary: {"description": new_description, "project": new_project, "billable": new_billable}}
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

    g = open(INPUT_CALENDAR_LOCATION, "rb")
    text = g.read()
    string = text.decode("utf-8")
    cal = Calendar(string)

    i = 0
    df = pd.DataFrame([])
    df_start_time = []
    df_end_time = []
    df_start_timestamp = []
    df_end_timestamp = []
    df_project = []
    df_description = []
    df_billable = []

    # build up a new calendar ics reflecting just meetings
    new_calendar = Calendar()

    for event in cal.events:
        start = event.begin.datetime
        end = event.end.datetime
        if start is None:
            continue
        if end is None:
            continue
        startdt = start + timedelta(hours=HOURS_OFF_UTC)
        enddt = end + timedelta(hours=HOURS_OFF_UTC)

        if startdt is None:
            continue
        if enddt is None:
            continue

        if startdt.month != MONTH_OF_INTEREST or startdt.year != YEAR:
            continue

        if DAY_RANGE != "all":
            # Check if the week of the event's start date is in the list of weeks of interest
            start_day = DAY_RANGE[0]
            end_day = DAY_RANGE[1]
            event_day = startdt.day
            if event_day < start_day or event_day > end_day:
                continue

        duration = enddt - startdt

        if duration.seconds / 60 / 60 >= 7:  # remove any really long events
            continue

        if duration.seconds <= 10:  # remove any really short events
            continue

        utc = timezone.utc
        startdt_utc = startdt.replace(tzinfo=utc)
        enddt_utc = enddt.replace(tzinfo=utc)

        accept = False
        for attendee in event.attendees:
            if attendee.email == YOUR_EMAIL:
                if attendee.partstat == "ACCEPTED" or attendee.partstat == "TENTATIVE":
                    accept = True
        if not accept:
            continue

        summary = event.name
        description, project, billable = classify(summary)

        # if this is a personal, then the description, project, and billable are all as follows
        if project == "personal" and not (billable.lower() == "true"):
            print("")
            print("IGNORING " + description + " as it is not work related.")
            print("")
            continue

        df_start_timestamp.append(startdt_utc.timestamp())
        df_end_timestamp.append(enddt_utc.timestamp())
        df_start_time.append(startdt_utc.strftime("%Y-%m-%dT%T.000Z"))
        df_end_time.append(enddt_utc.strftime("%Y-%m-%dT%T.000Z"))

        df_project.append(project)
        df_description.append(description)
        df_billable.append(billable.lower())

        i = i + 1

        # create copy of calendar for ease of error checking
        event = Event()
        if billable.lower() == "true":
            event.name = description + " " + project + " bill"
        else:
            event.name = description + " " + project + " no bill"

        event.begin = arrow.get(startdt_utc)
        event.end = arrow.get(enddt_utc)
        new_calendar.events.add(event)

    with open(CALENDAR_EVENTS_OUTPUT_ICS_LOCATION, "w") as f:
        f.write(str(new_calendar))

    g.close()
    df["Project"] = df_project
    df["Description"] = df_description
    df["Billable"] = df_billable
    df["Start Time"] = df_start_time
    df["End Time"] = df_end_time
    df["start_timestamp"] = df_start_timestamp
    df["end_timestamp"] = df_end_timestamp

    df.to_csv(CALENDAR_EVENTS_OUTPUT_CSV_LOCATION, index=False)
    print("Calendar csvs categorized.")
    print("")


if __name__ == "__main__":
    main()
