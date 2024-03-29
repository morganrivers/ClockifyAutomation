"""
integrates with AW (activitywatch) python bindings to import the raw buckets 
these are saved in AW_BUCKETS_UNCLASSIFIED
"""
import json
from datetime import datetime, timedelta, timezone

from aw_core.models import Event
from aw_client import ActivityWatchClient

from aw_query.functions import filter_period_intersect
import aw_query

import json
import sys
import requests

JSON_PARAMETERS_LOCATION = "../data/params.json"
AW_BUCKETS_UNCLASSIFIED = "../data/aw_buckets.json"


class DateTimeEncoder(json.JSONEncoder):
    def default(self, z):
        if isinstance(z, datetime):
            return str(z)
        elif isinstance(z, timedelta):
            return str(z)
        else:
            return super().default(z)


def calculate_start_end_dates(year, month_of_interest, day_range):
    start_day = day_range[0]
    end_day = day_range[1]
    start_date_raw = datetime(
        year,
        month_of_interest,
        start_day,
        tzinfo=timezone.utc,
    )
    end_date_raw = datetime(
        year + month_of_interest // 12,
        month_of_interest,
        end_day,
        23,  # End of the day
        59,
        59,
        999999,  # Maximum microsecond value
        tzinfo=timezone.utc,
    )

    return start_date_raw, end_date_raw


def parse_iso8601_time(timestamp):
    # This function will parse an ISO 8601 formatted string into a datetime object
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def get_window_events_over_period(
    year, month_of_interest, day_range, event_bucket_id, afk_bucket_id
):
    # Construct the start and end datetime objects
    if day_range == "all":
        start = datetime(year, month_of_interest, 1, tzinfo=timezone.utc)
        end = datetime(
            year if month_of_interest < 12 else year + 1,
            month_of_interest + 1 if month_of_interest < 12 else 1,
            1,
            tzinfo=timezone.utc,
        )
    else:
        # day_range are consecutive integers of the month that we are interested in
        start, end = calculate_start_end_dates(year, month_of_interest, day_range)

    # Format the start and end times for the API call
    start_iso = start.isoformat()
    end_iso = end.isoformat()

    # Construct the API call
    event_api_url = f"http://localhost:5600/api/0/buckets/{event_bucket_id}/events"
    afk_api_url = f"http://localhost:5600/api/0/buckets/{afk_bucket_id}/events"
    params = {"start": start_iso, "end": end_iso}

    # Fetch the data from the API
    response_events = requests.get(event_api_url, params=params)
    # Fetch the data from the API
    response_afk = requests.get(afk_api_url, params=params)

    # Check if the request was successful
    if response_events.status_code == 200 and response_afk.status_code == 200:
        data_events = response_events.json()
        data_afk = response_afk.json()

        # Convert the events from JSON into Event objects
        window_events_in_period = []
        for item in data_events:
            # Parse the timestamp and duration from the item
            timestamp = parse_iso8601_time(item["timestamp"])
            duration = timedelta(seconds=item["duration"])

            # Create an Event object
            event = Event(timestamp=timestamp, duration=duration, data=item["data"])
            window_events_in_period.append(event)
        if len(window_events_in_period) == 0:
            print("There is no activity watch data for this period.")
            print("We haven't really dealt with this edge case. Exiting.")
            sys.exit()
        # Convert AFK events from JSON into Event objects
        afk_events = [
            Event(
                timestamp=parse_iso8601_time(item["timestamp"]),
                duration=timedelta(seconds=item["duration"]),
                data={"status": item["data"]["status"]},
            )
            for item in data_afk
        ]
        not_afk_events = aw_query.functions.filter_keyvals(
            afk_events, "status", ["not-afk"]
        )

        # filter
        window_events_in_period_not_afk = aw_query.functions.filter_period_intersect(
            window_events_in_period, not_afk_events
        )

        # Return the final list of event objects
        return window_events_in_period_not_afk
    else:
        print(
            "Uh oh. You probably don't have the right watcher window id or you didn't start activitywatch before \
            running the script."
        )
        raise Exception(
            f"Failed to fetch data: {response.status_code}, {response.text}"
        )


def main():
    params = json.load(open(JSON_PARAMETERS_LOCATION, "r"))

    year = dict(params.items())["year"]
    month_of_interest = dict(params.items())["month_of_interest"]
    day_range = dict(params.items())["day_range"]
    event_bucket_id = dict(params.items())["event_bucket_id"]
    afk_bucket_id = dict(params.items())["afk_bucket_id"]

    print("")
    print("getting windowed AW events REST API request..")
    window_events_over_period = get_window_events_over_period(
        year, month_of_interest, day_range, event_bucket_id, afk_bucket_id
    )
    print("writing windowed AW events to json..")
    with open(AW_BUCKETS_UNCLASSIFIED, "w", encoding="utf-8") as jsonf:
        jsonf.write(
            json.dumps(window_events_over_period, indent=4, cls=DateTimeEncoder)
        )


if __name__ == "__main__":
    main()
