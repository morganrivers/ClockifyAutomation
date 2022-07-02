# Thanks to klemensschindler! I didn't write this code.
# see https://github.com/klemensschindler/icalfilter/blob/master/icalfilter.py

import icalendar
import datetime
import json
import pytz
utc = pytz.utc


# cuts off any months before the month of interest, saves result as .ics file.
def main(UNFILTERED_GCAL_LOCATION):
    JSON_PARAMETERS_LOCATION = '../data/params.json'
    params = json.load(open(JSON_PARAMETERS_LOCATION, 'r'))
    year = dict(params.items())["year"]
    month_of_interest = dict(params.items())["month_of_interest"]
    OUTPUT_GCAL_ICS_LOCATION = "../data/gcal_shortened.ics"
    YEAR = year
    MONTH = month_of_interest

    # read google calendar info
    with open(UNFILTERED_GCAL_LOCATION, 'r', encoding='utf-8') as f:
        cal = icalendar.Calendar.from_ical(f.read())
        outcal = icalendar.Calendar()

        for name, value in cal.items():
            outcal.add(name, value)

        def active_event(item):
            start_date = item['dtstart'].dt

            # recurrent
            if 'RRULE' in item:
                rrule = item['RRULE']
                # print (rrule)
                if 'UNTIL' not in rrule:
                    return True
                else:
                    assert len(rrule['UNTIL']) == 1
                    until_date = rrule['UNTIL'][0]

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

            raise Exception('ARGH')

        for item in cal.subcomponents:
            if item.name == 'VEVENT':
                if active_event(item):
                    outcal.add_component(item)
            else:
                outcal.add_component(item)

        # write shortened calendar output
        with open(OUTPUT_GCAL_ICS_LOCATION, 'wb') as outf:
            outf.write(outcal.to_ical(sorted=False))


if __name__ == '__main__':
    UNFILTERED_GCAL_LOCATION = "../data/gcal.ics"
    main(UNFILTERED_GCAL_LOCATION)
