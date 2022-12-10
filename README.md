Edits:
seemingly missing green gang call on 6/6 in gcal_shortened, probably a repeating call problem
timezone off for integrated model call
add in hours from phone


MVP PLAN: we are *not* using clockify as the "main UI", we will still have to integrate loosely with it and include pulling project names as well as pushing clockify events. https://clockify.me/feature-list for what clockify does is useful reference as we re-implement some features.
Pages:
1. @morgan Categorizing each day (sorted descending by total time of window title)
* option to pull in projects from the clockify backend, or create your own projects separate from clockify
2. settings page
* Button for porn scrubbing
(Also, the way I deal with porn is you just have to use "tor" browser or "incognito", and it will recognize those keywords and automatically delete window titles from the Activity Watch events before generating any summary results or data processing for time tracking. There could also be an option to label these as "NSFW" :P Maybe this can be a tickbox option in the UI, "ignore NSFW" or "keep time track of generic NSFW label for personal time accounting" xD)
* input clockify api key
3. visualization based on existing activitywatch (with piechart)
4. @morgan pdf invoice generation

API:
1. option to pull in projects from the clockify backend, or create your own projects separate from clockify

-> function that will generate the pdf with results
    - configuration to remove miscellaneous tags + user selected tags from the pdf output
-> run the program at all times add a tray icon for it
    https://github.com/moses-palmer/pystray
-> prompt users on the first X (7?) days of use every new [tab in program] which [tag] should we label it with
-> create screen where user can
    - input boxes for their gcal/activitywatch API keys
        - primarily the user will input their API keys, later on we add the login/automatic fetch support for the keys
    - ? button to erase senstive data
        - ? should we try to recognize porn with our language model
    - button to generate the result pdf
        - I'm thinking this button should both call the function that retrains the model + generate the pdf
        - ? or maybe not cause eventually the pdf will be the size of the world, maybe we should throw old data away and just train the models with 2mo old data
    - visualize and edit all of their activities and manually label the windows
        - ? possibility to cluster similar windows through search, so if users want to label every single use of "terminal" as "work", or "youtube" as "free time" they can
        - this change has to be r+w on the real csv file
        - ? re-run model automatically once changes are done
    - tickbox that removes miscellaneous tags + user selected tags from the pdf output


PLAN:

the most important thing to do: make a usable js webapp.
-> doesn't have to be a js webapp, we can create a python app using a)pyside b)pyqt c)tkinter. AFAIU pyside offers the easiest way to have a slick app.

menu on left side that doesn't go away.

5 pages. Import/export page, Projects page, categorizing page, calendar page, invoice page, 

Import/export page:
        What it currently does in python with imports: Runs the import from activity watch and google calendar files.  
        What id does with exports: takes the clockify api key and uploads to clockify.

Projects page:

        projects get pulled from clockify into table of options. You can select your own complete list of projects on this page. Just checklist table, with selected checklist bubbling up to the top
        project category is also shown.

Categorizing page:
        can take a look at activitywatch+gcal data on any day/week/month.

        Left hand half of page (time filtered):

                Default is checked for an optional "uncategorized" checkbox top left
                Default is checked for an optional "show gcal" checkbox top left
                Default is checked for an optional "show activity watch" checkbox top left
                Show irrelevant is default unchecked for an optional "show irrelevant" checkbox top left
                "Threshold" is an editable text field option for minimum time threshold to show items.

                If "uncategorized" unchecked, all window titles sorted by total time descending in relevent day/week/month are shown.
                If "uncategorized" checked, only window titles which are uncategorized sorted by total time descending in relevent day/week/month are shown.

                Each row shows:
                Window title, total time, project/uncategorized

        Right hand half of page (project search strings)

                name of the project along with the relevant tags. Probably makes sense to just add tags and little close [x] things on each tag. can scroll through projects and edit their tags. Left hand auto updates once a tag is entered.
                "Irrelevant" search box is used to get rid of things you don't want to see.

Calendar page
        Shows chunked results in gcal format for each week. window Title and project shown.
        https://github.com/ArrobeFr/jquery-calendar-bs4
Invoice page:
        forms for all the invoice parameters.
        click button generate invoice as pdf. Text boxes allow you to fill in and save your details.

needs to be javascript....


TODO: need to fix time zone issues... Carina's calendar event is always the wrong hour...

TODO: critical for anyone else to use this that we move away from using the explicit project ID's. Ideally, it will pull in the project ID list, and you can type the common name as needed. A set of project id's should be pulled in to select from.

TODO: put this in a localhost interface like activity watch with its own page?

You will need to get the API key from the settings in clockify and use the script "get_workspace_id.py" to get the workspace id. It's somewhere in the text that script spits out.

Some of this appears to be replicated here:
https://github.com/ActivityWatch/aw-import-ical/blob/master/main.py

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



2. Alter the month and year of filter_ical.py. Run filter_ical.py. Creates gcal_shortened.ics with just the one month of calendar events.
3. Run aw_to_csv.py. The resulting csv is in 'data/activitywatch_output_raw.csv', 
5. Alter 'gcal_to_csv.py' to include reasonable capture conditions for categorizing the google meets.
6. Run 'gcal_to_csv.py'. The results are in 'data/calendar_output_raw.csv'. You may want to look at the output and alter the conditions to more closely match your meeting attendance.
7. Run 'combine_csvs.py'. The results are in 'data/combined_output_raw.csv'
8. Run 'chunk_time.py'. The results are in 'data/chunks.ics' 
9. Run 'put_csv_through_api.py'. Results should be online now. (Note:Don't put the same CSV online twice! It will duplicate the records.)  
