# HOW IT CURRENTLY WORKS

Need internet connection to run!

1. Install activitywatch (https://activitywatch.net/).
   a. You will need to create a work default category and create at least one child of that category with the project id. All work categorizations will be defaulted to that, and all other work codes must be children of that categorization rule.
           Make sure the settings of activitywatch categorize the name in the format [description]\*[clockify project id hex string]
           Take a look at https://app.clockify.me/projects  to see the project hex id's. They're in the edit project url.
           For example: https://app.clockify.me/projects/63f2f144df25026c59e2e244/edit, 63f2f144df25026c59e2e244 is one project id string.
2. Go to clockify to also get the workspace id and put it in data/params.py
3. Either: set up automated google calendar integration with OAuth2, or go to your google calendar settings and export the appropriate ics, then move it to data/gcal.ics in the repository. 
     to Export your google calendar as gcal.ics. (Settings -> Click on Calendar on left -> Export Calendar). May need to unzip. Example: 
        unzip morgan @ allfed.info.ical.zip
        HINT: you probably want to confirm yes to any prompts here.
        mv morgan\@allfed.info.ics ~/Code/ClockifyAutomation/data/gcal.ics
4. [optional, if on linux] Install calcurse. Or if on windows, some other quick calendar inspection tool. Google calendar may be fine for this purpose.
        $ calcurse -P #CAUTION: PURGES ALL DATA PREVIOUSLY STORED IN CALCURSE
        $ calcurse -i data/calendar_output_raw.ics 
        $ calcurse
        Now you can inspect the calendar output, make sure it's not missing anything (can compare to month's data/gcal_shortened.ics by running 
        $ calcurse -i data/gcal_shortened.ics;calcurse
        and you'll see both)

        USEFUL COMMAND:
        calcurse -P; calcurse -i chunked_events.ics ; calcurse

Now you're ready to run. You'll need your clockify api key ready to paste in for this.

Run in a terminal
```
python3 run_conversion.py
```

Results should be online now. (Note:Don't upload to clockify twice! It will duplicate the records.)  

If you wish, you can also now fill in your preferred invoice parameters in data/invoice_params.json. You'll need to manually enter the month, hours that month, etc. It generates a pdf in data/ called "Invoice_[invoice number you entered].pdf".
