# Presumably we don't want activity watch to track things like tor browser or other
# privacy oriented tools, so you can run this to clean these things up.

import datetime

import aw_client
from datetime import datetime, timedelta, timezone


def delete_events(YEAR, MONTH_OF_INTEREST):

    aw_c = aw_client.ActivityWatchClient()

    start = datetime(YEAR, MONTH_OF_INTEREST, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
    end = datetime(YEAR, MONTH_OF_INTEREST + 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)

    all_events = aw_c.get_events("aw-watcher-window_snailshale", start=start, end=end)

    for event in all_events:
        # BE VERY CAUTIOUS!!! CAN DELETE LITERALLY EVERYTHING IF CONDITION BLANK!!!
        if "Tor Browser" in event["data"]["title"]:
            print("deleting event: " + str(event))
            aw_c.delete_event(
                bucket_id="aw-watcher-window_snailshale", event_id=event["id"]
            )


if __name__ == "__main__":
    print(delete_events(2022, 10))
