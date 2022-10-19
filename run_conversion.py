# from Tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename
import os
from src import filter_ical
from src import aw_to_csv
from src import gcal_to_csv
from src import combine_csvs
from src import chunk_time
from src import put_csv_through_api

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
    gcal = "../data/gcal.ics"
    print("Default location data/gcal.ics chosen")
print("")
print("File picker for activitywatch json? ( y / n )")
aw_response = input()
if aw_response[0].lower() == "y":
    aw = (
        askopenfilename()
    )  # show an "Open" dialog box and return the path to the selected file
    print("Location " + aw + " chosen")
else:
    aw = "../data/aw-category-export.json"
    print("Default location data/aw-category-export.json chosen")
print("")

while True:
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
    (u / e / r)
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
