import warnings
import datetime
from datetime import timedelta, timezone
import arrow
from ics import Event, Calendar
import numpy as np
import json
import pandas as pd
import calendar


def calculate_start_end_dates(year, month_of_interest, day_range):
    if day_range == "all":
        start_date_raw = datetime.datetime(
            year,
            month_of_interest,
            1,  # day of month
            tzinfo=timezone.utc,
        )
        end_date_raw = datetime.datetime(
            year + month_of_interest // 12,
            (month_of_interest) % 12 + 1,
            1,
            0,
            0,
            0,
            0,
            tzinfo=timezone.utc,
        )

        return start_date_raw, end_date_raw

    start_day = day_range[0]
    end_day = day_range[1]

    start_date_raw = datetime.datetime(
        year,
        month_of_interest,
        start_day,
        tzinfo=timezone.utc,
    )
    end_date_raw = datetime.datetime(
        year + month_of_interest // 12,
        (month_of_interest),
        end_day,
        23,  # End of the day
        59,
        59,
        999999,  # Maximum microsecond value
        tzinfo=timezone.utc,
    )

    return start_date_raw, end_date_raw


def print_summary_for_user(
    week_index,
    this_week_hours,
    overall_delta,
    time_end,
    time_start,
    start_date,
    end_date,
    year,
    month_of_interest,
    day_range,
):
    # print("last week (index " + str(week_index) + ") total hours:")
    # print(this_week_hours.total_seconds() / (60 * 60))
    # print("")
    print("year: " + str(year))
    print("month_of_interest: " + str(month_of_interest))
    print("day range:" + str(day_range))

    total_hours_worked = overall_delta.total_seconds() / (
        60 * 60
    )  # total duration in seconds to hours (60 seconds in min, 60 min in hour)

    print("")
    print("Total Hours worked in time period in question:")
    print(total_hours_worked)

    total_weeks_window = (time_end - time_start) / (
        60 * 60 * 24 * 7
    )  # total duration in units 7*24 hours

    # https://stackoverflow.com/questions/56005112/how-to-find-a-number-of-workdays-between-two-dates-in-python
    weekdays = np.busday_count(start_date, end_date)
    print("total M-F workdays")
    print(weekdays)
    print("effective number of weeks considered (weekdays/5)")
    print(weekdays / 5)

    print("Average hours per 5 day work week")
    print("this is: (total_hours_worked / weekdays) * 5, holidays ignored")
    print((total_hours_worked / weekdays) * 5)

    print("weekdays * 8: " + str(weekdays * 8))
    print(
        "Hours that would remain until meeting a 40 hour week (weekdays * 8 - total_hours_worked):"
    )
    print(weekdays * 8 - total_hours_worked)
    print("NOTE: BILLABLE HOURS AND NONBILLABLE HOURS ARE COMBINED FOR NUMBERS ABOVE")


def main():
    warnings.simplefilter(action="ignore", category=FutureWarning)
    warnings.simplefilter(action="ignore", category=UserWarning)

    INPUT_COMBINED_LOCATION = "../data/combined_events.csv"
    OUTPUT_CHUNKED_EVENTS_CSV_LOCATION = "../data/chunked_events.csv"
    OUTPUT_CHUNKED_EVENTS_ICS_LOCATION = "../data/chunked_events.ics"
    JSON_PARAMETERS_LOCATION = "../data/params.json"

    params = json.load(open(JSON_PARAMETERS_LOCATION, "r"))

    BLOCK_MINUTES = dict(params.items())["minutes_timeblock_clockify"]
    SECONDS_PER_BLOCK_THRESHOLD = dict(params.items())[
        "seconds_per_timeblock_threshold"
    ]

    year = dict(params.items())["year"]
    month_of_interest = dict(params.items())["month_of_interest"]
    day_range = dict(params.items())["day_range"]

    df = pd.read_csv(INPUT_COMBINED_LOCATION)

    df_sorted = df.sort_values(by="start_timestamp")
    df_sorted.reset_index(drop=True, inplace=True)

    df_sorted["duration"] = df_sorted["end_timestamp"] - df_sorted["start_timestamp"]
    blk = BLOCK_MINUTES * 60  # minutes converted to seconds

    # use the majority amount of time in the block to assign the proper time code.
    # if less than blk seconds total in that block, do not assign time to it.
    # time_start = (
    #     df_sorted.loc[0].start_timestamp - df_sorted.loc[0].start_timestamp % blk
    # )
    start_date_raw, end_date_raw = calculate_start_end_dates(
        year, month_of_interest, day_range
    )

    start_date = start_date_raw.date()

    time_start = start_date_raw.replace(microsecond=0).timestamp()

    # time_end = (
    #     df_sorted.loc[len(df_sorted) - 1].start_timestamp
    #     - df_sorted.loc[0].start_timestamp % blk
    #     + blk
    # )

    end_date = end_date_raw.date()
    time_end = end_date_raw.replace(microsecond=0).timestamp()

    df_new = pd.DataFrame()
    for i in range(0, int(np.floor(time_end - time_start) / blk)):
        time_block_start = time_start + i * blk
        time_block_end = time_block_start + blk

        # select events which end after the block-start
        # and start before the block-end
        events = df_sorted[df_sorted["end_timestamp"] > time_block_start][
            df_sorted["start_timestamp"] < time_block_end
        ]
        if len(events) == 0:
            continue

        durations = {}
        for index, event in events.iterrows():
            dpb = (
                event["Description"]
                + "*"
                + event["Project"]
                + "*"
                + str(event["Billable"])
            )

            # evaluate the total amount of time of each event in the block

            if dpb not in durations.keys():
                durations[dpb] = 0

            # add the duration to this block
            durations[dpb] = durations[dpb] + event["duration"]

            # if the event starts before the block, reduce its duration
            if event["start_timestamp"] < time_block_start:
                durations[dpb] = durations[dpb] - (
                    time_block_start - event["start_timestamp"]
                )

            # if the event ends after the block, reduce its duration
            if event["end_timestamp"] > time_block_end:
                durations[dpb] = durations[dpb] - (
                    event["end_timestamp"] - time_block_end
                )

        # select the dominant event description
        max_keys = [
            key for key, value in durations.items() if value == max(durations.values())
        ]
        dominant_event = max_keys[0]
        dominant_event_duration = durations[max_keys[0]]

        tuple = dominant_event.split("*")
        description, project, billable = tuple

        # ignore if less than a minute during that half hour
        if dominant_event_duration < SECONDS_PER_BLOCK_THRESHOLD:
            continue

        start_dt = datetime.datetime.fromtimestamp(int(time_block_start))
        end_dt = datetime.datetime.fromtimestamp(int(time_block_end))

        start_string = (start_dt).replace(microsecond=0).strftime("%Y-%m-%dT%T.000Z")
        end_string = (end_dt).replace(microsecond=0).strftime("%Y-%m-%dT%T.000Z")
        # merge with previous event if was the same
        # (and ended at same as this start)
        if (
            len(df_new) > 0
            and df_new.loc[len(df_new) - 1, "Description"] == description
            and int(df_new.loc[len(df_new) - 1, "end_timestamp"])
            == int(time_block_start)
        ):
            df_new.loc[len(df_new) - 1, "End Time"] = end_string
            df_new.loc[len(df_new) - 1, "end_timestamp"] = time_block_end
        else:  # create new event
            tmp = pd.DataFrame(
                [
                    {
                        "Project": project,
                        "Description": description,
                        "Billable": billable,
                        "Start Time": start_string,
                        "End Time": end_string,
                        "start_timestamp": time_block_start,
                        "end_timestamp": time_block_end,
                    }
                ]
            )
            df_new = pd.concat([df_new, tmp], axis=0, ignore_index=True)
    print("len(df_new)")
    print(len(df_new))
    df_chunks = df_new.sort_values(by="start_timestamp")
    df_chunks.reset_index(drop=True, inplace=True)
    df_chunks.to_csv(OUTPUT_CHUNKED_EVENTS_CSV_LOCATION, index=False)

    # build up a new calendar ics reflecting chunked timeblocks
    new_calendar = Calendar()

    # also add up the total billable time for the entire duration (a month, typically)
    overall_delta = timedelta(0)
    #  add up the total billable time for the week
    previous_week_index = 0
    this_week_hours = timedelta(0)
    for index, row in df_chunks.iterrows():
        project = row["Project"]
        description = row["Description"]
        billable = row["Billable"]
        start_timestamp = row["start_timestamp"]
        end_timestamp = row["end_timestamp"]
        event = Event()
        if billable:
            event.name = description + " " + project + " bill"
        else:
            event.name = description + " " + project + " no bill"

        event.begin = arrow.get(datetime.datetime.fromtimestamp(int(start_timestamp)))
        event.end = arrow.get(datetime.datetime.fromtimestamp(int(end_timestamp)))

        overall_delta += event.end - event.begin

        week_index = event.begin.isocalendar()[1]  # gets the week index in question

        start_day = day_range[0]
        end_day = day_range[1]
        if day_range == "all" or (
            event.begin.day >= start_day and event.begin.day <= end_day
        ):  # process only for weeks of interest
            if week_index != previous_week_index and previous_week_index != 0:
                print(
                    "week "
                    + str(week_index - 1)
                    + " hours: \n"
                    + str(this_week_hours.total_seconds() / (60 * 60))
                    + "\n"
                )

                # we are starting a new week!
                this_week_hours = timedelta(0)

            this_week_hours += event.end - event.begin
            # print("Total Hours worked in each week")
            # print(
            #     overall_delta.total_seconds() // (60 * 60)
            # )  # to hours (60 seconds in min, 60 min in h)

            new_calendar.events.add(event)

        previous_week_index = week_index

    print_summary_for_user(
        week_index,
        this_week_hours,
        overall_delta,
        time_end,
        time_start,
        start_date,
        end_date,
        year,
        month_of_interest,
        day_range,
    )

    with open(OUTPUT_CHUNKED_EVENTS_ICS_LOCATION, "w") as f:
        f.write(str(new_calendar))

    print("")
    print("Calendar events chunked")
    print("")


if __name__ == "__main__":
    main()
