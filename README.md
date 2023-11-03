MVP PLAN: we are *not* using clockify as the "main UI", we will still have to integrate loosely with it and include pulling project names as well as pushing clockify events. https://clockify.me/feature-list for what clockify does is useful reference as we re-implement some features.

Backend:
1 make a fork of activity watch without any of its UI features, so that it monitors and saves events, but is missing a lot of the the current UI stuff, we only really want the settings page and visualization page, which we will also modify.
2 set it up as a standalone elektron app to be run on linux, windows, or mac on startup (make sure it's a thing running in the tray, using https://github.com/moses-palmer/pystray). NOTE: System tray is already implemented in AW though.
3 make the spacy text categorization be able to load in the activitywatch events, and then categorize the uncategorized events based on past examples


Pages:
1. @morgan Categorizing each day (sorted descending by total time of window title)
* just uses projects from the "Projects" page (which are either user-made or imported from clockify)
* allows editing of  "categorization", similar to the existing clockify categorization, where we have a page which has, for each tag, a tag name, billable rate (or "billable/not billable"), and a listing of window titles falling under this category. I think the MVP probably also needs the option for this to have a regex search feature so if someone wants to add a strictly defined classification they can. So you can either categorize with regex or window titles individually
* machine learning model gives "suggestions" which you can confirm or alter if needed
* can take a look at activitywatch+gcal data on any given day
a. Left hand half of page (time filtered):
* Default is checked for an optional "uncategorized" checkbox top left
* Default is checked for an optional "show gcal" checkbox top left
* Default is checked for an optional "show activity watch" checkbox top left
* If "uncategorized" unchecked, all window titles (sorted by total time descending in relevent day) are shown.
* If "uncategorized" checked, only window titles which are uncategorized (sorted by total time descending in relevent day) are shown.
* Each row shows: Window title, total time, project/uncategorized
b. Right hand half of page (project search strings)
* name of the project along with the relevant regex (displayed as tags). Probably makes sense to just add tags and little close [x] things on each tag. can scroll through projects and edit their tags. Left hand auto updates once a tag is entered.
* "Irrelevant" category at top is used to get rid of things you don't want to see (if you don't care to track time for irrelevant window titles).


2. settings page
* Button for porn scrubbing (already partially implemented with delete_aw_events.py)
(Also, the way I deal with porn is you just have to use "tor" browser or "incognito", and it will recognize those keywords and automatically delete window titles from the Activity Watch events before generating any summary results or data processing for time tracking. There could also be an option to label these as "NSFW" :P Maybe this can be a tickbox option in the UI, "ignore NSFW" or "keep time track of generic NSFW label for personal time accounting" xD)
* input clockify api key
* gcal secret url text box
* option to turn on machine learning categorization guessing
* export (uploads) to clockify api button (curretnly implemented with put_csv_through_api.py)
* import from gcal button (currently implemented by running gcal_to_csv.py)
* "Threshold" is an editable text field option for minimum time threshold to show items.

3. visualization based on existing activitywatch (with piechart)
* Involves an "Activity" screen visualization of the projects (specifically, I think the MVP can have "Top Categories" and "Category Tree" [here](https://activitywatch.net/img/screenshots/screenshot-v0.9.3-activity.png)) for each day in addition to a date picker for the day or series of days/weeks/months which will be visualized. This is actually very similar to the clockify feature (see https://clockify.me/feature-list).

5. @morgan pdf invoice generation
* Invoice page:
* forms for all the invoice parameters.
* click button generate invoice as pdf. Text boxes allow you to fill in and save your details.
* already implemented with generate_invoice.py

6. Projects page
* button to pull in from clockify
* option to alter names and details and billable rates of projects
* very similar to projects page from https://clockify.me/feature-list


API:
1. option to pull in projects from the clockify backend, or create your own projects separate from clockify



TODO: need to fix time zone issues... Carina's calendar event is always the wrong hour...

TODO: critical for anyone else to use this that we move away from using the explicit project ID's. Ideally, it will pull in the project ID list, and you can type the common name as needed. A set of project id's should be pulled in to select from.

TODO: put this in a localhost interface like activity watch with its own page?

You will need to get the API key from the settings in clockify and use the script "get_workspace_id.py" to get the workspace id. It's somewhere in the text that script spits out.

Some of this appears to be replicated here:
https://github.com/ActivityWatch/aw-import-ical/blob/master/main.py

# HOW IT CURRENTLY WORKS

1. Make sure the settings of activitywatch categorize the name in the format [description]\*[clockify project id hex string] and export the activitywatch json categories as 'data/aw-category-export.json'
2. Export your google calendar as gcal.ics. (Settings -> Click on Calendar on left -> Export Calendar). May need to unzip. Example: 
        unzip morgan @ allfed.info.ical.zip
        HINT: you probably want to confirm yes to any prompts here.
        mv morgan\@allfed.info.ics ~/Code/ClockifyAutomation/data/gcal.ics
3. [if on linux] Install calcurse. Or if on windows, some other quick calendar inspection tool. Google calendar may be fine for this purpose.
        $ calcurse -P #CAUTION: PURGES ALL DATA PREVIOUSLY STORED IN CALCURSE
        $ calcurse -i data/calendar_output_raw.ics 
        $ calcurse
        Now you can inspect the calendar output, make sure it's not missing anything (can compare to month's data/gcal_shortened.ics by running 
        $ calcurse -i data/gcal_shortened.ics;calcurse
        and you'll see both)

        USEFUL COMMAND:
        calcurse -P; calcurse -i chunked_events.ics ; calcurse

2. Alter the month and year of filter_ical.py. Run filter_ical.py. Creates gcal_shortened.ics with just the one month of calendar events.
3. Run aw_to_csv.py. The resulting csv is in 'data/activitywatch_output_raw.csv', 
5. Alter 'gcal_to_csv.py' to include reasonable capture conditions for categorizing the google meets.
6. Run 'gcal_to_csv.py'. The results are in 'data/calendar_output_raw.csv'. You may want to look at the output and alter the conditions to more closely match your meeting attendance.
7. Run 'combine_csvs.py'. The results are in 'data/combined_output_raw.csv'
8. Run 'chunk_time.py'. The results are in 'data/chunks.ics' 
9. Run 'put_csv_through_api.py'. Results should be online now. (Note:Don't put the same CSV online twice! It will duplicate the records.)  
