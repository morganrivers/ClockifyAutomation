from ics import Event, Calendar
import arrow
import datetime
import warnings
import pandas as pd


def main():
    warnings.simplefilter(action="ignore", category=FutureWarning)

    AW_INPUT_LOCATION = "../data/activitywatch_output_raw.csv"
    GCAL_INPUT_LOCATION = "../data/calendar_output_raw.csv"
    OUTPUT_COMBINED_LOCATION = "../data/combined_events.csv"
    OUTPUT_COMBINED_CALENDAR = "../data/combined_events.ics"

    # Read CSV file into DataFrame df
    df_aw = pd.read_csv(AW_INPUT_LOCATION)  # activitywatch
    df_gcal = pd.read_csv(GCAL_INPUT_LOCATION)  # google calendar

    # loop through each item in activitywatch. if it falls within a calendar output timeslot, then remove it.

    combined_df = pd.concat([df_gcal, df_aw], axis=0, ignore_index=True)
    df_sorted = combined_df.sort_values(by="start_timestamp")
    df_sorted.reset_index(drop=True, inplace=True)

    # delete zero length events
    i = 0
    while i < len(df_sorted) - 1:
        i = i + 1
        row = df_sorted.iloc[i]
        if row["start_timestamp"] >= row["end_timestamp"]:
            df_sorted.drop(axis=0, index=i, inplace=True)  # delete this event
            df_sorted.reset_index(drop=True, inplace=True)

    # Example:
    #   [     ] <--- row1
    #   [   ]   <--- row2
    # result:
    #   [     ] <--- row1
    # Example:
    #   [     ] <--- row1
    #     [ ]   <--- row2
    # result:
    #   [     ] <--- row1
    # Example:
    #   [     ] <--- row1
    #   [     ] <--- row2
    # result:
    #   [     ] <--- row1
    # collision detect sandwiched or equivalent calendar events, but only if they don't collide with any other calendar event
    index1 = 0
    while index1 < len(df_sorted) - 2:
        index1 = index1 + 1
        row1 = df_sorted.iloc[index1]
        index2 = index1 + 1
        row2 = df_sorted.iloc[index2]

        # sandwich condition, equivalence condition
        if (
            (
                row1["start_timestamp"]
                <= row2["start_timestamp"]
                <= row1["end_timestamp"]
            )
            and (
                row1["start_timestamp"]
                <= row2["end_timestamp"]
                <= row1["end_timestamp"]
            )
        ) or (
            row1["start_timestamp"] == row2["start_timestamp"]
            and row1["end_timestamp"] == row2["end_timestamp"]
        ):
            df_sorted.drop(axis=0, index=index2, inplace=True)  # delete this event
            df_sorted.reset_index(drop=True, inplace=True)
            index1 = index1 - 1

    index1 = 0
    # collision detect imperfectly overlapping events, and alter their endpoint to match the collider (first one to happen gets priority)
    while index1 < len(df_sorted) - 2:
        index1 = index1 + 1
        row1 = df_sorted.iloc[index1]
        index2 = index1 + 1
        row2 = df_sorted.iloc[index2]

        # Example:
        # [     ]    <--- row1
        #      [  ]  <--- row2
        # result:
        # [     ]    <--- row1
        #       [ ]  <--- row2
        # overlaps at start of second item
        if row1["start_timestamp"] < row2["start_timestamp"] < row1["end_timestamp"]:
            # assign start of 2 to end of 1
            df_sorted.loc[index2, "start_timestamp"] = row1["end_timestamp"]
            df_sorted.loc[index2, "Start Time"] = row1["End Time"]

            assert not (
                row1["start_timestamp"] < row2["end_timestamp"] < row1["end_timestamp"]
            )  # no sandwiches!

            continue

        # Example:
        #    [     ]  <--- row1
        #  [   ]      <--- row2
        # result:
        #    [     ]  <--- row1
        #  [ ]        <--- row2
        # overlaps at end of second item
        if row1["start_timestamp"] < row2["end_timestamp"] < row1["end_timestamp"]:
            assert not (
                row1["start_timestamp"]
                < row2["start_timestamp"]
                < row1["end_timestamp"]
            )  # no sandwiches!

            df_sorted.loc[index2, "end_timestamp"] = row1["start_timestamp"]
            df_sorted.loc[index2, "End Time"] = row1["Start Time"]
            continue

    df_sorted.drop(axis=0, index=index2, inplace=True)  # delete this event
    df_sorted.reset_index(drop=True, inplace=True)
    df_sorted.to_csv(OUTPUT_COMBINED_LOCATION, index=False)

    # build up a new calendar ics
    new_calendar = Calendar()

    for index, row in df_sorted.iterrows():
        project = row["Project"]
        description = row["Description"]
        billable = row["Billable"]
        start_timestamp = row["start_timestamp"]
        end_timestamp = row["end_timestamp"]
        # create copy of calendar for ease of error checking
        event = Event()
        if billable:
            event.name = description + " " + project + " bill"
        else:
            event.name = description + " " + project + " no bill"

        event.begin = arrow.get(datetime.datetime.fromtimestamp(int(start_timestamp)))
        event.end = arrow.get(datetime.datetime.fromtimestamp(int(end_timestamp)))
        new_calendar.events.add(event)

    with open(OUTPUT_COMBINED_CALENDAR, "w") as f:  # giving up on merge...
        f.write(str(new_calendar))

    print("AW and gcal events combined")
    print()


if __name__ == "__main__":
    main()
