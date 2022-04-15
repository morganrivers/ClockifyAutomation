from csv_ical import Convert
import pandas as pd
from icalendar import Calendar, Event
from datetime import datetime, timedelta, timezone
from dateutil import tz
import pytz

SAVE_LOCATION = 'gcal.ics'
CSV_FILE_LOCATION = 'calendar_output_raw.csv'
HOURS_OFF_UTC = -7
MONTH_OF_INTEREST = 3
YEAR = 2022


# return  project, category, description, billable, attended
def classify(summary):
    slow = summary.lower()
    if "integrated" in slow:
        return ("Integrated Model Call","602f4800895dec08c3d638ba", True)
    elif "team research call" in slow:
        return ("Regularly Scheduled Research Call", "5e56de580121f031bdc3afac", True)
    elif "ines" in slow:
        return ("call with ines","5edfcdb1c236b03119337f95", True)
    elif "green gang" in slow:
        return ("Regularly Scheduled Green Gang Call", "5edfcdb1c236b03119337f95", True)
    elif "pdc" in slow:
        return ("PDC work, not billable (paid by my grant)","5e56de580121f031bdc3afac", False)
    elif "interview" in slow:
        return ("interview calls","5e56e0c35b92677285acd736", True)
    elif "team meeting" in slow:
        return ("Regularly Scheduled Team Meetings Call","5e56dfce0121f031bdc3b040", True)
    elif "maciej" in slow:
        return ("Meeting with Maciej","5e56e1317ba4ff284c53a2a9", True)
    elif "check in" in slow:
        return ("Scheduled check in","5e56e1317ba4ff284c53a2a9", True)
    elif "check-in" in slow:
        return ("Scheduled check in","5e56e1317ba4ff284c53a2a9", True)
    elif "checkin" in slow:
        return ("Scheduled check in","5e56e1317ba4ff284c53a2a9", True)
    elif "contract" in slow:
        return ("Contract renewal meeting","5e56e1317ba4ff284c53a2a9", True)
    elif "discussion" in slow:
        return ("Small Discussion Group","5e56de580121f031bdc3afac", True)
    elif "aaron adamson" in slow:
        return ("Research","Meeting with Aaron adamson","5e56de580121f031bdc3afac", True)
    elif "kpi" in slow:
        return ("Call about KPIs", "5e56d8767ba4ff284c539e9d", True)
    elif "ukraine" in slow:
        return ("ukraine meetings", "5f2da49c3afc991c82a2546b", True)
    elif "digital resilience" in slow:
        return ("Call about digital resilience", "5f50058c3a37e35cbede35ea", True)
    elif "carina" in slow:
        return ( "Call with carina about trello", "5e56d8767ba4ff284c539e9d", True)
    return ("UNDEFINED","", False)


g = open(SAVE_LOCATION,'rb')
gcal = Calendar.from_ical(g.read())
i=0
df=pd.DataFrame([])
df_start_time = []
df_end_time = []
df_start_timestamp = []
df_end_timestamp = []
df_project = []
df_description = []
df_billable = []

for component in gcal.walk():
    if component.name == "VEVENT":
        start = component.get('dtstart')
        end = component.get('dtend')
        if(start is None):
            # print("startna")
            # print(component.get('summary'))
            continue
        if(end is None):
            # print(component.get('summary'))
            # print("endna")
            continue
        startdt = start.dt + timedelta(hours=HOURS_OFF_UTC)
        enddt = end.dt + timedelta(hours=HOURS_OFF_UTC)

        if(startdt is None):
            # print("startna")
            # print(component.get('summary'))
            continue
        if(enddt is None):
            # print(component.get('summary'))
            # print("endna")
            continue

        if(startdt.month != MONTH_OF_INTEREST or startdt.year != YEAR):
            continue

        duration=enddt - startdt

        if(duration.seconds/60/60>=7): #remove any really long events
            continue

        if(duration.seconds<=10): #remove any really short events
            print("?")
            print(component.get('summary'))
            quit()
            continue

        utc=timezone.utc
        startdt_utc = startdt.replace(tzinfo=utc)
        enddt_utc = enddt.replace(tzinfo=utc)


        summary = component.get('summary')
        description, project, billable = classify(summary)

        if(project==""):
            continue
        task=" "
        if(billable):
            b_string = "true"
        else:
            b_string = "false"

        df_start_timestamp.append(startdt_utc.timestamp())
        # print(df_start_time)
        df_end_timestamp.append(enddt_utc.timestamp())
        # print(df_start_timestamp)
        df_start_time.append(startdt_utc.strftime('%Y-%m-%dT%T.000Z'))
        df_end_time.append(enddt_utc.strftime('%Y-%m-%dT%T.000Z'))

        df_project.append(project)
        df_description.append(description)
        df_billable.append(b_string)

        i=i+1
print(i)
g.close()
df['Project'] = df_project
df['Description'] = df_description
df['Billable'] = df_billable
df['Start Time'] = df_start_time
df['End Time'] = df_end_time
df['start_timestamp'] = df_start_timestamp
df['end_timestamp'] = df_end_timestamp

df.to_csv("data/calendar_output_raw.csv", index=False)

print(df)
