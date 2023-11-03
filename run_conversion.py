# from Tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename
import os
from src import filter_ical
from src import get_aw_buckets
from src import categorize_aw_events
from src import gcal_to_csv
from src import combine_csvs
from src import chunk_time
from src import put_csv_through_api

import json

JSON_PARAMETERS_LOCATION = "../data/params.json"

os.chdir("src")


# Function to write to JSON
def write_to_json(month, day_range):
    with open(JSON_PARAMETERS_LOCATION, "r+") as f:
        data = json.load(f)
        data["month_of_interest"] = month
        data["day_range"] = day_range
        f.seek(0)  # Reset file position to the beginning.
        json.dump(data, f, indent=4)
        f.truncate()  # Remove remaining part of old data


# Function to get the custom day range from user
def get_custom_day_range():
    while True:
        day_range_input = input("Enter the day range in format [n1,n2]: ")
        if day_range_input.strip().lower() == "all":  # Check if input is 'all'
            return "all"
        else:
            try:
                day_range_list = json.loads(day_range_input)  # Convert string input to list
                if (
                    isinstance(day_range_list, list)
                    and len(day_range_list) == 2
                    and 1 <= day_range_list[0] < day_range_list[1] <= 31
                ):
                    return day_range_list
                else:
                    print("Invalid format or range. Please enter a valid day range, or 'all'.")
            except (json.JSONDecodeError, ValueError):
                print("Invalid input. Please enter the day range in format [n1,n2] or 'all'.")


# Function to handle user input for month and day range
def handle_user_input():
    print(
        "Please enter 'j' for using the existing data/params.json month and day range, or 'm' for entering custom month and/or day range to use and update the params file"
    )
    day_range = ""
    month_of_interest = -1
    while True:
        response = input().strip().lower()
        if len(response) == 0:
            print("Please type an input")
        elif response in ["j", "m"]:
            break
        else:
            print("Please enter either 'j' or 'm'")
    if response == "m":
        # Ask for custom month and day range
        while True:
            try:
                month_of_interest = int(input("Enter the month of interest (1-12): "))
                if 1 <= month_of_interest <= 12:
                    break
                else:
                    print("Month must be between 1 and 12.")
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 12.")
        day_range = get_custom_day_range()
        write_to_json(month_of_interest, day_range)
    else:
        print("Using data from params.json.")

        params = json.load(open(JSON_PARAMETERS_LOCATION, "r"))

        month_of_interest = dict(params.items())["month_of_interest"]
        day_range = dict(params.items())["day_range"]

    return month_of_interest, day_range


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
    gcal = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    assert type(gcal) == str, "Error: Must select a file!"
    print("Location " + gcal + " chosen")

else:
    gcal = "../data/morgan@allfed.info.ics"
    print("Default location data/gcal.ics chosen")
print("")
print("File picker for activitywatch json? ( y / n )")
aw_response = input()
if aw_response[0].lower() == "y":
    aw = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
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

    month_of_interest, day_range = handle_user_input()

    print("year: " + str(year))
    print("month_of_interest: " + str(month_of_interest))
    print("day range:" + str(day_range))
    print('Day range is first to last day inclusive, and also you can put "all" as well for the whole month')
    print()
    # run the import script, combining google calendar (ics) and activity watch.
    filter_ical.main(gcal)
    get_aw_buckets.main()
    categorize_aw_events.main()
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
