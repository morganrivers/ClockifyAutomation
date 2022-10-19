# Thanks to klemensschindler! I didn't write this code.
# see https://github.com/klemensschindler/icalfilter/blob/master/icalfilter.py

import icalendar
import datetime
import json
import pytz
import requests

utc = pytz.utc


# cuts off any months before the month of interest, saves result as .ics file.
def main(UNFILTERED_GCAL_LOCATION):
    JSON_PARAMETERS_LOCATION = "../data/params.json"
    params = json.load(open(JSON_PARAMETERS_LOCATION, "r"))
    json_data = ""
    year = dict(params.items())["year"]
    month_of_interest = dict(params.items())["month_of_interest"]
    OUTPUT_GCAL_ICS_LOCATION = "../data/gcal_shortened.ics"
    YEAR = year
    MONTH = month_of_interest

    if (
        UNFILTERED_GCAL_LOCATION
        == "use secret address in params (THIS IS NOT A FILE!) $,! :)"
    ):
        # this is a secret http address, not a file. It's defined in data/params.json
        URL = dict(params.items())["secret_google_calendar_address"]

        # defining a params dict for the parameters to be sent to the API
        PARAMS = {}

        # sending get request and saving the response as response object
        r = requests.get(url=URL, params=PARAMS)

        # extracting data in string format
        json_data = r.text
    else:

        # read google calendar info from dowloaded exported file
        with open(UNFILTERED_GCAL_LOCATION, "r", encoding="utf-8") as f:
            json_data = f.read()

    cal = icalendar.Calendar.from_ical(json_data)
    outcal = icalendar.Calendar()

    for name, value in cal.items():
        outcal.add(name, value)

    def active_event(item):
        start_date = item["dtstart"].dt

        # recurrent
        if "RRULE" in item:
            rrule = item["RRULE"]
            # print (rrule)
            if "UNTIL" not in rrule:
                return True
            else:
                assert len(rrule["UNTIL"]) == 1
                until_date = rrule["UNTIL"][0]

                if type(until_date) == datetime.datetime:
                    return until_date >= utc.localize(datetime.datetime(YEAR, MONTH, 1))

                if type(until_date) == datetime.date:
                    return until_date >= datetime.date(YEAR, MONTH, 1)

                raise Exception('Unknown date format for "UNTIL" field')

        # not reccurrent
        if type(start_date) == datetime.datetime:
            return start_date >= utc.localize(datetime.datetime(YEAR, MONTH, 1))

        if type(start_date) == datetime.date:
            return start_date >= datetime.date(YEAR, MONTH, 1)

        raise Exception("ARGH")

    for item in cal.subcomponents:
        if item.name == "VEVENT":
            if active_event(item):
                outcal.add_component(item)
        else:
            outcal.add_component(item)

    # write shortened calendar output
    with open(OUTPUT_GCAL_ICS_LOCATION, "wb") as outf:
        outf.write(outcal.to_ical(sorted=False))


if __name__ == "__main__":
    USE_SECRET_ADDRESS = True
    if USE_SECRET_ADDRESS:
        main("use secret address in params (THIS IS NOT A FILE!) $,! :)")
    else:
        main("../data/gcal.ics")
