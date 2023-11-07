"""
ActivityWatch Process Checker

This script checks for the presence of specific ActivityWatch processes on a Unix-like system
and sends a desktop notification if any are missing. It is intended to be used as a monitoring tool
to ensure that all components of ActivityWatch are running correctly, especially after a system startup
or when running as a scheduled task (e.g., cron job).

Usage:
    Intended to be run as a standalone script or called by a scheduler like cron.
    Ensure that the script has executable permissions and the necessary environment
    variables for desktop notifications are accessible.

Author: Morgan Rivers
"""

import subprocess
from pwd import getpwnam

import os

from datetime import datetime, timedelta, timezone


def check_processes():
    # This command checks if any processes with 'aw' in their name are running.
    check_cmd = "ps -A | grep -q 'aw' && echo 1 || echo 0"
    # This command lists processes with 'aw' in their name.
    cmd = "ps -A | grep 'aw'"

    try:
        # Execute the check command to see if 'aw' processes are running.
        can_check = subprocess.check_output(check_cmd, shell=True).decode("utf-8").split("\n")
        if int(can_check[0]) == 1:
            # If 'aw' processes are found, get their details.
            processes = subprocess.check_output(cmd, shell=True).decode("utf-8").split("\n")
        else:
            processes = ""
    except subprocess.CalledProcessError:
        # If the check command fails, send a notification to the user.
        notify_cmd = f'notify-send "Warning! Activitywatch unable to check_processes"'
        subprocess.run(notify_cmd, shell=True)
        return

    # Extract just the process names from the process details.
    processes = [p.split(" ")[-1] for p in processes if p]

    # Define a list of processes that we expect to be running.
    required_processes = [
        "aw-qt",
        "aw-server",
        "aw-watcher-wind",
        "aw-watcher-afk",
    ]
    # Check which required processes are missing.
    missing_processes = [p for p in required_processes if p not in processes]

    if missing_processes:
        # Concatenate all missing process names into a single string.
        all_missing = ""
        for missing in missing_processes:
            all_missing += f"{missing} "

        # Get the username of the currently logged-in user.
        logname = os.environ["LOGNAME"]

        # get the user id of the first logged in user
        uid = getpwnam(logname).pw_uid

        # Find the process ID(s) for the i3 window manager running under the current user.
        pgrep_command = "pgrep -u $LOGNAME i3"
        result = subprocess.run(pgrep_command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True)
        pids = result.stdout.decode("utf-8").strip().split("\n")

        # Notify the user for each PID found that Activitywatch processes are missing.
        for pid in pids:
            # Construct the notify command for this PID
            notify_cmd = (
                f'eval "export $(egrep -z DBUS_SESSION_BUS_ADDRESS /proc/{pid}/environ)";'
                f'export XDG_RUNTIME_DIR=/run/user/{uid};/usr/bin/notify-send "Warning! Activitywatch has missing\
                 processes: \n {all_missing}"'
            )

            # Execute the notify command
            subprocess.run(notify_cmd, shell=True)
        # the truly awful command above is to get the notify-send to work from cron
        # https://askubuntu.com/questions/298608/notify-send-doesnt-work-from-crontab
        # based on above but modified to get the first result and look for i3, not gnome-session
        # subprocess.run(notify_cmd, shell=True)
        # os.chdir(os.path.expanduser("~/Apps/activitywatch"))
        # subprocess.run("export DISPLAY=:0;./aw-qt", shell=True)
        # subprocess.run("sh /home/dmrivers/Apps/activitywatch/aw-qt", shell=True)
        return False
    return True


if __name__ == "__main__":
    check_processes()
