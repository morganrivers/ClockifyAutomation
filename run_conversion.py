# from Tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename
import os
from src import filter_ical
from src import aw_to_csv
from src import gcal_to_csv
from src import combine_csvs
from src import chunk_time
from src import put_csv_through_api

import json

JSON_PARAMETERS_LOCATION = "../data/params.json"

os.chdir("src")

# import the gcal and aw files
print(
    """Google calendar access: load from secret gcal address in data/params ( s ), file 
    picker ( p ), or default location dowloaded ical ( d )"""
)
while True:
    gcal_response = input()
    if len(gcal_response) == 0:
        print("Please type an input")
    else:
        break
if gcal_response[0].lower() == "s":
    gcal = "use secret address in params (THIS IS NOT A FILE!) $,! :)"
    print("Using secret address from data/params.json file.")
elif gcal_response[0].lower() == "p":
    gcal = (
        askopenfilename()
    )  # show an "Open" dialog box and return the path to the selected file
    assert type(gcal) == str, "Error: Must select a file!"
    print("Location " + gcal + " chosen")

else:
    gcal = "../data/morgan@allfed.info.ics"
    print("Default location data/gcal.ics chosen")
print("")
print("File picker for activitywatch json? ( y / n )")
aw_response = input()
if aw_response[0].lower() == "y":
    aw = (
        askopenfilename()
    )  # show an "Open" dialog box and return the path to the selected file
    if len(aw) == 0:
        print("ERROR: cancelled dialog")
        quit()
    print("Location " + str(aw) + " chosen")
else:
    aw = "../data/aw-category-export.json"
    print("Default location data/aw-category-export.json chosen")
print("")

while True:
    params = json.load(open(JSON_PARAMETERS_LOCATION, "r"))
    year = dict(params.items())["year"]
    month_of_interest = dict(params.items())["month_of_interest"]
    print("year: " + str(year))
    print("month_of_interest: " + str(month_of_interest))
    print("day range:" + str(dict(params.items())["day_range"]))
    print(
        'Day range is first to last day inclusive, and also you can put "all" as well for the whole month'
    )
    print()
    # run the import script, combining google calendar (ics) and activity watch.
    filter_ical.main(gcal)
    aw_to_csv.main(aw)
    gcal_to_csv.main()
    combine_csvs.main()
    chunk_time.main()
    print(
        """Recommended to check out the resulting calendar 'data/chunked_events.ics'.
    Enter u to UPLOAD to clockify, e to EXIT, r to RERUN the processing to clockify 
    events with same file (probably because you've updated some values in the
    filter parameters) 
    Please type one of these characters then press enter: (u / e / r)
    """
    )
    while True:
        response = input()
        if len(response) == 0:
            print("Please type an input")
        else:
            break
    if response[0].lower() == "r":
        continue
    elif response[0].lower() == "u":
        break
    else:
        os.chdir("..")
        quit()

# ask for the API key and export the time sheet to clockify
put_csv_through_api.main()

os.chdir("..")
