from csv_ical import Convert
import pandas as pd
from icalendar import Calendar, Event
from datetime import datetime, timedelta, timezone
from dateutil import tz
import pytz

SAVE_LOCATION = 'gcal.ics'
CSV_FILE_LOCATION = 'calendar_output_raw.csv'
HOURS_OFF_UTC = -7


# return  project, category, description, billable, attended
def classify(summary):
    slow = summary.lower()
    if "integrated" in slow:
        return ("Integrated Model", "Research","Integrated Model Call",True, True)
    elif "team research call" in slow:
        return ("Research - Miscellaneous: Research Calls", "Research", "Regularly Scheduled Research Call", True, True)
    elif "ines" in slow:
        return ("Outdoor Growing", "Research", "call with ines",True, True)
    elif "green gang" in slow:
        return ("Outdoor Growing", "Research", "Regularly Scheduled Green Gang Call", True, True)
    elif "pdc" in slow:
        return ("Research - Miscellaneous", "Research","PDC work, not billable (paid by my grant)",False, True)
    elif "interview" in slow:
        return ("Recruitment", "HR","interview calls",True, True)
    elif "team meeting" in slow:
        return ("ALLFED Team Meetings", "Operations","Regularly Scheduled Team Meetings Call",True, True)
    elif "maciej" in slow:
        return ("Appraisal", "HR","Meeting with Maciej",True, True)
    elif "check in" in slow:
        return ("Appraisal", "HR","Scheduled check in",True, True)
    elif "check-in" in slow:
        return ("Appraisal", "HR","Scheduled check in",True, True)
    elif "checkin" in slow:
        return ("Appraisal", "HR","Scheduled check in",True, True)
    elif "contract" in slow:
        return ("Appraisal: Contract Renewals (incl. Admin Prep & renegotiations)", "HR","Contract renewal meeting",True, True)
    elif "discussion" in slow:
        return ("Research - Miscellaneous", "Research","Small Discussion Group",True, True)
    elif "aaron adamson" in slow:
        return ("Research - Miscellaneous", "Research","Meeting with Aaron adamson",True, True)
    elif "kpi" in slow:
        return ("Key Performance Indicators (KPIs)", "Strategy (Meta)", "Call about KPIs", True, True)
    elif "ukraine" in slow:
        return ("Response Team Activations: Russia Ukraine War 2022", "Planning & Preparedness", "ukraine meetings", True, True)
    elif "digital resilience" in slow:
        return ("Digital Resilience", "Research", "Call about digital resilience", True, True)
    elif "carina" in slow:
        return ("Time Logs", "HR", "Call with carina about trello", True, True)
    return ("UNDEFINED", "UNDEFINED","UNDEFINED",False, False)


g = open(SAVE_LOCATION,'rb')
gcal = Calendar.from_ical(g.read())
i=0
df=pd.DataFrame([])
df_start_date = []
df_start_time = []
df_start_timestamp = []
df_end_timestamp = []
df_duration = []
df_project = []
df_category = []
df_description = []
df_billable = []
df_task = []
df_email = []
df_user = []
df_tags = []
df_client = []

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
        duration=enddt - startdt
        # if(not component.get('status') == "CONFIRMED"):
        #     continue

        if(startdt.month != 3 or startdt.year != 2022):
            continue

        if(duration.seconds/60/60>=7): #remove any really long events
            continue

        utc=timezone.utc
        startdt_utc = startdt.replace(tzinfo=utc)
        enddt_utc = enddt.replace(tzinfo=utc)

        if(duration.seconds<=10): #remove any really short events
            print("?")
            print(component.get('summary'))
            quit()
            continue

        in_attendance = False
        for x in component.get("attendee"):
            if("morgan" in x):
                in_attendance = True

        summary = component.get('summary')
        # print(startdt.strftime('%m/%d/%Y'))
        # print("attend: "+str(in_attendance))
        # print("status: "+str(component.get('status')))
        # print(summary)
        project, category, description, billable, attend = classify(summary)
        # print(category)
        # print("")

        # if("Green Gang" in description or "KPI" in description):
        #     if(int(startdt.strftime('%d'))==28):
        #         print(description)
        #         print(start.dt)
                
        #         # offset = utc.utcoffset(start.dt)
        #         # print(dt)
        #         # print("offset")
        #         # print(offset)
        #         print("")

        if("UNDEFINED" in category):
            continue
        task=" "
        if(billable):
            b_string = "Yes"
        else:
            b_string = "No"

        df_start_timestamp.append(startdt_utc.timestamp())
        # print(df_start_time)
        df_end_timestamp.append(enddt_utc.timestamp())
        # print(df_start_timestamp)
        df_start_time.append(startdt_utc.time())
        df_start_date.append(startdt_utc.strftime('%m/%d/%Y'))

        minutes = int((duration.seconds%3600)/60)
        seconds = int((duration.seconds%60))
        df_duration.append(str(int(duration.seconds/60/60))+":"+str("%02d" % (minutes,))+":"+str("%02d" % (seconds,)))

        df_project.append(project)
        df_category.append(category)
        df_description.append(description)
        df_billable.append(b_string)
        df_task.append(task)
        df_email.append("morgan@allfed.info")
        # if(not attend):
        #     continuer

        df_user.append("morgan@allfed.info")
        df_tags.append("")
        df_client.append("morgan@allfed.info")

        i=i+1
print(i)
g.close()
df['Client'] = df_client
df['Project'] = df_project
df['Description'] = df_description
df['Task'] = df_task
df['User'] = df_user
df['category'] = df_category
df['Email'] = df_email
df['Billable'] = df_billable
df['Start Date'] = df_start_date
df['Start Time'] = df_start_time
df['Duration (h)'] = df_duration
df['start_timestamp'] = df_start_timestamp
df['end_timestamp'] = df_end_timestamp

df.to_csv("calendar_output_raw.csv", index=False)

print(df)
