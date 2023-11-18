# What does this repo do exactly?
If you're entering specific working hours via invoicing as a contractor, you know this can be a distracting, annoying, and often imprecise process. The goal of this repository is to empower contractors to no longer have to worry about manual time entry and invoicing.
The software:
 - Imports this window title data and merges it with data from google calendar.
 - Connects to the api of a software called "clockify" often used for corporate invoice management.
 - Allows the user to view clockify project codes and efficiently sort their time all at once when the invoice is being submitted, using regular expression text-based search on window titles.
 - Makes intelligent decisions about when the user was working and when the user was away based on away from keyboard "afk" time, and the chunking of time bins.
 - Uploads relevant binned data to the clockify time bin.
 - Makes it easy for a contractor to export an invoice as a pdf based on time used.

Additionally, the instructions below provides installation instructions for scripts that ensures window titles are tracked locally using the Activitywatch application by launching activitywatch on startup and notifying the user if it's not running, as well as ensuring regular backups are made of the time data so that data loss is much less likely.

This is an alpha version of an integration that should eventually be integrated into activity watch. 

# HOW IT CURRENTLY WORKS
(command line version)
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
4. [optional, and only if on linux] Install calcurse. Or if on windows, some other quick calendar inspection tool. Google calendar may be fine for this purpose.
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

# Other configuration

I recommend the following if you're using this app for tracking work time:

1. Making regular backups of activity watch data
2. Starting up activity watch on boot
3. Ensuring there's a way the computer can tell you that activity watch isn't running for some reason.

I did these in linux with the i3 windows manager as follows:

## 1. Making regular backups of activity watch data and 2. Starting activitywatch on boot.

This is currently the first two lines in my crontab (`crontab -e` command in linux):

```
# m h  dom mon dow   command
@reboot sleep 5 && export DISPLAY=:0 && while ! i3 --get-socketpath >/dev/null 2>&1; do sleep 5; done && /usr/bin/i3-msg " exec /bin/termit --execute='/home/dmrivers/Apps/activitywatch/aw-qt'" && /usr/bin/i3-msg "exec /bin/termit --execute='/home/dmrivers/Apps/activitywatch/aw-watcher-afk/aw-watcher-afk'" && sleep 15 && exec /home/dmrivers/Code/ClockifyAutomation/backup_aw.sh >/dev/null
```

The command provided is a chain of instructions that seem to be configured to run at system reboot, set within a user's crontab or similar scheduler. Here's a breakdown of what each part of the command does:

- `@reboot`: This is a directive used in cron, a time-based job scheduler in Unix-like operating systems. It specifies that the following commands should be run at startup after the system reboots.

- `sleep 5`: Pauses execution for 5 seconds. This gives the system some time to initialize other services before the subsequent commands are executed.

- `export DISPLAY=:0`: Sets the `DISPLAY` environment variable to `:0`, which is typically the default display number for a computer's first graphical X session. This is necessary for graphical applications to know where to render themselves if they are being started by a script.

- `while ! i3 --get-socketpath >/dev/null 2>&1; do sleep 5; done`: This loop continuously checks whether the i3 window manager is up and running by trying to get its socket path. If `i3 --get-socketpath` returns a non-zero exit status (i.e., i3 is not ready), it sleeps for 5 seconds and tries again. The loop exits once i3 is ready.

- `/usr/bin/i3-msg " exec /bin/termit --execute='/home/dmrivers/Apps/activitywatch/aw-qt'"`: Once i3 is running, it uses `i3-msg`, which is a tool to send messages to the i3 window manager, to execute `termit`, a terminal emulator. The `termit` terminal is told to execute a script at the path `/home/dmrivers/Apps/activitywatch/aw-qt`, which is the ActivityWatch application.

- `/usr/bin/i3-msg "exec /bin/termit --execute='/home/dmrivers/Apps/activitywatch/aw-watcher-afk/aw-watcher-afk'"`: Similarly, another `termit` window is opened to execute the ActivityWatch AFK watcher script found at `/home/dmrivers/Apps/activitywatch/aw-watcher-afk/aw-watcher-afk`. This tracks the user's idle time.

- `sleep 15`: This pauses execution for another 15 seconds, to ensure that the previously started applications have enough time to initialize before the next command is run.

- `exec /home/dmrivers/Code/ClockifyAutomation/scripts/backup_aw.sh >/dev/null`: Finally, this command executes a script named `backup_aw.sh` located at the cloned github repo location. The `exec` command replaces the shell with the specified program, which in this case is the script. The output is redirected to `/dev/null`, which means all output of the script (standard output and error) is discarded and not shown anywhere.

## 3. Ensuring there's a way the computer can tell you that activity watch isn't running for some reason.
This is the third line in my crontab:
```
* * * * * /usr/bin/python3 /home/dmrivers/Code/ClockifyAutomation/scripts/alert_user_if_aw_not_running.py
```
That launches a cron job to run the `alert_user_if_aw_not_running.py` script every minute. The script checks the running processes and uses notify-send to alert the user if any processes are missing each minute.


## Final note

You can find both `alert_user_if_aw_not_running.py` and `backup_aw.sh` in the scripts/ folder in this repository.
These are specific to i3 but can be modified for other use cases. Other methods of startup, checking, and backups can also accomplish similar results.

# Status and note on fair usage of the software.
The software is in alpha right now, and is intended for those using linux and with some knowledge of python. Some adaptation would be needed for other operating systems.
The software is privacy protecting, and empowering the contractor rather than the agency employing the contractor. It is a violation of the LICENSE of this software if the usage of it, or derivative works, are enforced, conditional, or otherwise compulsory.
