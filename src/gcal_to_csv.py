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

    # classify a calendar event and return category's description,
    # project, billable
    def classify(summary):
        slow = summary.lower()
        cats = dict(dict(data.items())["categories"].items())
        for k, i in cats.items():
            if (slow in k.lower()) or (k.lower() in slow):
                description = i["description"]
                project = i["project"]
                billable = i["billable"]
                return (description, project, billable)

        print("unmatched calendar item")
        print(summary)
        print("")

        # none of the summary matched the categories
        default = dict(dict(data.items())["default"].items())
        return (default["description"], default["project"], default["billable"])

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
        if project == "personal" and not billable:
            print("")
            print("IGNORING " + description + " as it is not work related.")
            print("")
            continue

        if billable:
            b_string = "true"
        else:
            b_string = "false"

        df_start_timestamp.append(startdt_utc.timestamp())
        df_end_timestamp.append(enddt_utc.timestamp())
        df_start_time.append(startdt_utc.strftime("%Y-%m-%dT%T.000Z"))
        df_end_time.append(enddt_utc.strftime("%Y-%m-%dT%T.000Z"))

        df_project.append(project)
        df_description.append(description)
        df_billable.append(b_string)

        i = i + 1

        # create copy of calendar for ease of error checking
        event = Event()
        if billable:
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
