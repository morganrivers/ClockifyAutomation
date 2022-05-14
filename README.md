You will need to get the API key from the settings in clockify and use the script "get_workspace_id.py" to get the workspace id. It's somewhere in the text that script spits out.

1. Make sure the settings of activitywatch categorize the name in the format [description]\*[clockify project id hex string] and export the activitywatch json categories as 'data/aw-category-export.json'
2. Alter the month and year of filter_ical.py. Run filter_ical.py. Creates out.ics with just the one month of calendar events.
3. Run aw_to_csv.py. The resulting csv is in 'data/activitywatch_output_raw.csv', 
4. Export your google calendar as gcal.ics. (Settings -> Click on Calendar on left -> Export Calendar). May need to unzip. Example: 
        unzip morgan @ allfed.info.ical.zip
        mv morgan\@allfed.info.ics ~/Code/ClockifyAutomation/data/gcal.ics
5. Alter 'gcal_to_csv.py' to include reasonable capture conditions for categorizing the google meets.
6. Run 'gcal_to_csv.py'. The results are in 'data/calendar_output_raw.csv'. You may want to look at the output and alter the conditions to more closely match your meeting attendance.
7. Run 'combine_csvs.py'. The results are in 'data/combined_output_raw.csv'
8. Run 'chunk_time.py'. The results are in 'data/chunks.ics' 
9. Run 'put_csv_through_api.py'. Results should be online now. (Note:Don't put the same CSV online twice! It will duplicate the records.)  