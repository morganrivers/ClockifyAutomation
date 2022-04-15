You will need to get the API key from the settings in clockify and use the script "get_workspace_id.py" to get the workspace id. It's somewhere in the text that script spits out.

1. Make sure the settings of activitywatch categorize the name in the format [description]\*[clockify project id hex string] and export the activitywatch json categories as 'data/aw-category-export-api.json'
2. Run aw_to_csv.py. The resulting csv is in 'data/activitywatch_output_raw.csv', 
3. export your google calendar as gcal.ics.
4. Alter 'gcal_to_csv.py' to include reasonable capture conditions for categorizing the google meets. (note: right now the attendance is not really working, so you have to categorize whether you went based on the window title only.) 
5. Run 'gcal_to_csv.py'. The results are in 'data/calendar_output_raw.csv'
6. Run 'combine_csvs.py'. The results are in 'data/combined_output_raw.csv' 7. Run 'put_csv_through_api.py'. Results should be online now. (Note:Don't put the same CSV online twice! It will duplicate the records.)  