# Presumably we don't want activity watch to track things like tor browser or other
# privacy oriented tools, so you can run this to clean these things up.
import datetime
from datetime import datetime, timezone
import aw_client
import json

JSON_PARAMETERS_LOCATION = "../data/params.json"


def main(year, month):
    params = json.load(open(JSON_PARAMETERS_LOCATION, "r"))
    hostname = dict(params.items())["event_bucket_id"]

    aw_c = aw_client.ActivityWatchClient()

    start = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
    end = (
        datetime(year, month + 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        if month != 12
        else datetime(year + 1, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    )

    all_events = aw_c.get_events(hostname, start=start, end=end)
    n_private_events = 0
    for event in all_events:
        if (
            "Tor Browser" in event["data"]["title"]
            or "Incognito" in event["data"]["title"]
            or "Private Browsing" in event["data"]["title"]
        ):
            # print("deleting event: " + str(event)) # uncomment to see the private events being deleted
            aw_c.delete_event(bucket_id=hostname, event_id=event["id"])
            n_private_events += 1
    print(f"Deleted {n_private_events} private events.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 2:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        main(year=year, month=month)
    else:
        print("Usage: delete_aw_events.py year month")
