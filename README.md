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