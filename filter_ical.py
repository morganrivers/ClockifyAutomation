#Thanks to klemensschindler! I didn't write this code. 
# see https://github.com/klemensschindler/icalfilter/blob/master/icalfilter.py

import icalendar
import datetime
import pytz
utc = pytz.utc

YEAR = 2022
MONTH = 4

def main():
    with open('data/gcal.ics', 'r', encoding='utf-8') as f:
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
                start_date = item['dtstart'].dt
                if active_event(item):
                    print ('INCLUDE', item['summary'], repr(start_date))
                    outcal.add_component(item)
                else:
                    print ('EXCLUDE', item['summary'], repr(start_date))
                    pass
            else:
                outcal.add_component(item)

        with open('out.ics', 'wb') as outf:
            outf.write(outcal.to_ical(sorted=False))

main()