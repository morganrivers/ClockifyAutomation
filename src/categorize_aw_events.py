"""
File loads the raw buckets which were exported from activitywatch, then categorizes them.
When there are events accounting for a significant amount of time uncategorized, 
the user is prompted to categorize them.
"""
import pandas as pd
from aw_core.models import Event
from datetime import datetime, timedelta
import aw_transform
from aw_transform.classify import Rule
import json
import re
import copy

AW_BUCKETS_UNCLASSIFIED = "../data/aw_buckets.json"
CLOCKIFY_CATEGORIES_LOCATION = "../data/aw-category-export.json"
JSON_PARAMETERS_LOCATION = "../data/params.json"
OUTPUT_CSV_LOCATION = "../data/activitywatch_output_raw.csv"


def get_rules():
    with open(CLOCKIFY_CATEGORIES_LOCATION, "r") as read_file:
        categories = json.load(read_file)["categories"]

    category_names = []
    for c in categories:
        category_names.append(c["name"])

    rules = []
    for c in categories:
        rule = aw_transform.Rule(c)

        # Check the ignore_case setting and compile the regex accordingly
        if rule.ignore_case:
            quit()
            rule.regex = re.compile(c["rule"]["regex"], re.IGNORECASE)
        else:
            rule.regex = re.compile(c["rule"]["regex"])

        rules.append((c["name"], rule))
    return rules


def add_pattern_to_rules_json(category_name, new_pattern):
    with open(CLOCKIFY_CATEGORIES_LOCATION, "r+") as read_file:
        data = json.load(read_file)
        found_category = False
        for category in data["categories"]:
            if category_name == category["name"]:
                found_category = True
                # The regex patterns are combined using '|'
                category["rule"]["regex"] += "|" + re.escape(new_pattern)
                break
        assert found_category, "Error: tried to add regex string to category but could not be found. Quitting."

        # Go to the beginning of the file to overwrite it
        read_file.seek(0)
        json.dump(data, read_file, indent=4)
        read_file.truncate()  # Truncate the file to the new size


def combine_and_sort_rules(rules):
    # Load parameters from JSON
    params = json.load(open(JSON_PARAMETERS_LOCATION, "r"))
    aw_work_tree_root = dict(params.items())["aw_work_tree_root"]

    combined_rules = {}
    work_generic_description, work_generic_project = aw_work_tree_root.split("*")
    personal_keys = []

    for _, (category_name, rule) in enumerate(rules):
        # print("rule.regex")
        # print(rule.regex)
        regex_pattern = rule.regex.pattern if rule.regex else "N/A"
        if len(category_name) == 1:  # Categories with one-element names are treated as personal
            if (
                category_name[0].split("*")[0] == work_generic_description
                and category_name[0].split("*")[1] == work_generic_project
            ):
                description, project = category_name[0].split("*")
            else:
                description = category_name[0]
                project = "personal"
                personal_keys.append((project, description))
        else:
            description, project = category_name[1].split("*")

        key = (project, description)
        combined_rules.setdefault(key, set()).add(regex_pattern)

    # Separate sort key function to order work_generic at the top, then by project, then personal categories
    def sort_key(item):
        key = item[0]
        if key == (work_generic_project, work_generic_description):
            return ("", "0")
        elif key in personal_keys:
            return (
                "zzzzzzz",
                key[1],
            )  # 'z' will sort these last, ordered by description
        return key

    sorted_combined_rules = sorted(combined_rules.items(), key=sort_key)

    return sorted_combined_rules


def show_rules_and_get_category_numbers(rules):
    # Load parameters from JSON
    params = json.load(open(JSON_PARAMETERS_LOCATION, "r"))
    aw_work_tree_root = dict(params.items())["aw_work_tree_root"]

    sorted_combined_rules = combine_and_sort_rules(rules)
    category_name_by_rule_number = []
    print("FORMAT")
    print("Rule number: (if work, project id) category name : regex search strings ")
    for i, ((project, description), regex_patterns) in enumerate(sorted_combined_rules, start=1):
        assert i < 100  # Ensure the index 'i' is 2 characters wide
        combined_regex = "|".join(regex_patterns)
        SHORTEN_DISPLAYED_REGEXES = True
        if SHORTEN_DISPLAYED_REGEXES:
            to_show_regex = combined_regex[:100]
            if len(combined_regex) > 100:
                to_show_regex += " etc..."
        else:
            to_show_regex = combined_regex
        if project == "personal":
            print(f"{i:2}: {description}: {to_show_regex}")
            category_name_by_rule_number.append([description])  # Assuming personal categories are single-element lists
        else:
            print(f"{i:2}: {project} {description}: {to_show_regex}")
            if description == aw_work_tree_root.split("*")[0]:
                # this is the generic root parent project
                category_name_by_rule_number.append([description + "*" + project])
            else:
                category_name_by_rule_number.append([aw_work_tree_root, description + "*" + project])

    return category_name_by_rule_number


def convert_categorized_data_to_csv(categorized):
    # now we convert categorized data  with the correct project, category, description, billable, attended, in a
    # csv format

    params = json.load(open(JSON_PARAMETERS_LOCATION, "r"))
    aw_work_tree_root = dict(params.items())["aw_work_tree_root"]

    hours_off_utc = dict(params.items())["hours_off_utc"]
    HOURS_OFF_UTC = hours_off_utc

    i = 0
    df = pd.DataFrame([])
    df_start_time = []
    df_end_time = []
    df_start_timestamp = []
    df_end_timestamp = []
    df_project = []
    df_description = []
    df_billable = []
    for cz in categorized:
        # not really sure why, but the parent's name doesn't seem to change, it should be Research
        # - Miscellaneous*Research*Uncategorized research for ALLFED*Yes, but it's just "ALLFED"

        if cz["data"]["$category"][0] == "Uncategorized":
            # print("")
            # print("Uncategorized!")
            # print('cz["data"]["$category"]')
            # print(cz["data"]["$category"])
            continue  # uncategorized in this case

        category_tree = cz["data"]["$category"]
        if category_tree[0] != aw_work_tree_root:
            # print("")
            # print("Categorized not work!")
            # print('cz["data"]["$category"]')
            # print(category_tree)

            continue
        if len(category_tree) == 1:  # the generic one
            split_by_asterisk_tuple = [
                aw_work_tree_root.split("*")[0],
                aw_work_tree_root.split("*")[1],
            ]
        else:
            split_by_asterisk_tuple = category_tree[1].split("*")
        description, project = split_by_asterisk_tuple

        if "pdc" in description.lower():
            billable = "false"
        else:
            billable = "true"

        start_dt = cz["timestamp"] + timedelta(hours=HOURS_OFF_UTC)  # convert to PST from UTC
        duration_delta = cz["duration"]
        df_start_timestamp.append(start_dt.replace(microsecond=0).timestamp())
        df_end_timestamp.append((start_dt + duration_delta).replace(microsecond=0).timestamp())

        df_start_time.append(start_dt.replace(microsecond=0).strftime("%Y-%m-%dT%T.000Z"))

        df_end_time.append((start_dt + duration_delta).replace(microsecond=0).strftime("%Y-%m-%dT%T.000Z"))
        # print("project + description")
        # print(project + ", " + description)
        # print("")
        df_project.append(project)
        df_description.append(description)
        df_billable.append(billable)

        i = i + 1

    df["Project"] = df_project
    df["Description"] = df_description
    df["Billable"] = df_billable
    df["Start Time"] = df_start_time
    df["End Time"] = df_end_time
    # useful for later comparison, not imported
    df["start_timestamp"] = df_start_timestamp
    df["end_timestamp"] = df_end_timestamp

    df.to_csv(OUTPUT_CSV_LOCATION, index=False)


def create_event_from_json(json_data):
    timestamp = datetime.fromisoformat(json_data["timestamp"])
    # Assuming 'duration' is represented as "HH:MM:SS.microseconds"
    hours, minutes, seconds = map(float, json_data["duration"].split(":"))
    duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
    data = json_data["data"]
    return Event(timestamp=timestamp, duration=duration, data=data)


def load_events_from_json(file_path):
    with open(file_path, "r", encoding="utf-8") as jsonf:
        json_events = json.load(jsonf)
        return [create_event_from_json(event_data) for event_data in json_events]


def get_uncategorized_events(categorized_events):
    # Filter out events that have a category set to "Uncategorized"
    return [event for event in categorized_events if event["data"]["$category"][0] == "Uncategorized"]


def get_sorted_event_groups(categorized_events):
    # Group events by description and sum durations
    event_groups = {}
    for event in categorized_events:
        description = event["data"].get("title", "No Description")
        duration = event["duration"].total_seconds()
        if description not in event_groups:
            event_groups[description] = {"duration": duration, "events": [event]}
        else:
            event_groups[description]["duration"] += duration
            event_groups[description]["events"].append(event)

    # Sort by total duration
    sorted_event_groups = sorted(event_groups.items(), key=lambda item: item[1]["duration"], reverse=True)
    return sorted_event_groups


def print_summary_and_maybe_process_actions(action_stack, rules):
    # Print a summary of the rules that will be added or created
    if len(action_stack) == 0:
        print("No additional events categorized.")
        return

    print("Summary of actions to be processed:")
    for action, category_names, regex_to_add in action_stack:
        category_name_for_summary = category_names[-1] if category_names else "Unknown"
        if action == "add":
            print(f"Action: Add Pattern | Category: {category_name_for_summary} | Regex: {regex_to_add}")
        elif action == "new":
            print(f"Action: New Rule | Category: {category_name_for_summary} | Regex: {regex_to_add}")

    # Prompt the user for their choice
    user_choice = (
        input("Please choose an option: 'e' to save and exit cate loop, 'q' to quit without saving: ").strip().lower()
    )
    while True:
        if user_choice == "e":
            # Save changes and exit
            process_action_stack_to_json_and_ensure_rules_match(action_stack, rules)
            print("Changes saved. Exiting categorization loop.")
            return
        elif user_choice == "q":
            # Quit without saving
            print("Exiting categorization loop without saving changes.")
            return
        else:
            print("Invalid option selected.")


# Function to process the action stack
def process_action_stack_to_json_and_ensure_rules_match(action_stack, rules):
    for action, category_name, regex_to_add in action_stack:
        if action == "add":
            add_pattern_to_rules_json(category_name, regex_to_add)
        if action == "new":
            add_rule_to_rules_json(category_name, regex_to_add)

    loaded_rules_from_json = get_rules()  # Reload the rules

    if not rules_are_same(loaded_rules_from_json, rules):
        print(
            "WARNING: rules added do not correspond to rules in program's memory after saving. You might need to "
            "fix the json directly. Sorry about that."
        )


def add_pattern_to_rules(rules, category_name, new_pattern):
    # Update the rule in memory without writing to the JSON file
    found_category = False
    for cname, rule in rules:
        if cname == category_name:
            found_category = True
            # The regex patterns are combined using '|'
            # Make sure to add only if the pattern doesn't already exist
            pattern_parts = rule.regex.pattern.split("|")
            if new_pattern not in pattern_parts:
                rule.regex = re.compile(rule.regex.pattern + "|" + re.escape(new_pattern))

    assert found_category, "Error: category tried to add but could not be found. Quitting."
    return rules


def remove_pattern_from_rules(rules, category_name, pattern_to_remove):
    # Update the rule in memory without writing to the JSON file
    for cname, rule in rules:
        if cname == category_name:
            # Split the regex pattern to remove the specific pattern
            pattern_parts = rule.regex.pattern.split("|")
            # Escape the pattern to remove to avoid issues with regex characters
            escaped_pattern_to_remove = re.escape(pattern_to_remove)
            if escaped_pattern_to_remove in pattern_parts:
                # Remove the pattern
                pattern_parts.remove(escaped_pattern_to_remove)
                # Filter out any empty strings that could lead to an empty regex part
                pattern_parts = list(filter(None, pattern_parts))
                # Recompile the regex if there are any patterns left, otherwise set a default pattern
                rule.regex = re.compile("|".join(pattern_parts)) if pattern_parts else re.compile("a^")
            break
    return rules


def add_rule_to_rules_json(category_name, new_pattern, case_sensitive=False):
    # Load parameters from JSON
    params = json.load(open(JSON_PARAMETERS_LOCATION, "r"))
    aw_work_tree_root = dict(params.items())["aw_work_tree_root"]

    with open(CLOCKIFY_CATEGORIES_LOCATION, "r+") as read_file:
        data = json.load(read_file)
        if category_name.split("*")[1] == "personal":
            # Construct the new rule
            new_rule = {
                "name": [category_name],
                "name_pretty": category_name,
                "rule": {
                    "type": "regex",
                    "regex": re.escape(new_pattern),
                    "ignore_case": not case_sensitive,
                },
                "data": {
                    # no color for now
                    # "color": "#000000"  # Default color
                },
                "subname": category_name,
                # Add more fields as required
                "parent": None,
                "depth": 0,
            }

        else:
            # Construct the new rule
            new_rule = {
                "name": [aw_work_tree_root, category_name],
                "name_pretty": [aw_work_tree_root + ">" + category_name],
                "rule": {
                    "type": "regex",
                    "regex": re.escape(new_pattern),
                    "ignore_case": not case_sensitive,
                },
                "data": {
                    # no color for now
                    # "color": "#000000"  # Default color
                },
                "subname": category_name,
                # Add more fields as required
                "parent": [aw_work_tree_root],
                "depth": 1,
            }

        # Get the next id value
        next_id = max(category["id"] for category in data["categories"]) + 1 if data["categories"] else 1
        new_rule["id"] = next_id

        # Append the new rule to the categories
        data["categories"].append(new_rule)

        # Go to the beginning of the file to overwrite it
        read_file.seek(0)
        json.dump(data, read_file, indent=4)
        read_file.truncate()  # Truncate the file to the new size


def add_new_rule(rules, new_category_name, new_regex_pattern, ignore_case=False):
    """
    Add a new rule to the rules object in memory.

    Parameters:
        rules (list): The current list of rules, where each element is a tuple containing the category name and
            a Rule object.
        new_category_name (Category): The name of the new category to be added.
        new_regex_pattern (str): The regex pattern for the new rule.
        ignore_case (bool): Whether the regex should ignore case.

    Returns:
        List[Tuple[Category, Rule]]: The updated list of rules with the new rule included.
    """
    # Load parameters from JSON
    params = json.load(open(JSON_PARAMETERS_LOCATION, "r"))
    aw_work_tree_root = dict(params.items())["aw_work_tree_root"]

    next_id = len(rules) + 1 if rules else 1

    # regex_flags = re.IGNORECASE if ignore_case else 0
    # regex = re.compile(re.escape(new_regex_pattern), regex_flags)

    # breakpoint()
    if new_category_name.split("*")[1] == "personal":
        nice_cat_name = new_category_name.split("*")[0]
        # Construct the new rule
        new_rule = {
            "name": [nice_cat_name],
            "name_pretty": nice_cat_name,
            "rule": {"type": "regex"},
            "data": {
                # no color for now
                # "color": "#000000"  # Default color
            },
            "subname": nice_cat_name,
            # Add more fields as required
            "parent": None,
            "depth": 0,
            "id": next_id,
        }
    else:
        # Construct the new work rule
        new_rule = {
            "name": [aw_work_tree_root, new_category_name],
            "name_pretty": [aw_work_tree_root + ">" + new_category_name],
            "rule": {"type": "regex"},
            "data": {
                # no color for now
                # "color": "#000000"  # Default color
            },
            "subname": new_category_name,
            # Add more fields as required
            "parent": [aw_work_tree_root],
            "depth": 1,
            "id": next_id,
        }

    rule = aw_transform.Rule(new_rule)
    rule.regex = re.compile(re.escape(new_regex_pattern))
    rules.append((new_rule["name"], rule))

    return rules


def remove_rule(rules, category_name):
    # Filter out the rule with the matching category name
    rules = [rule for rule in rules if rule[0] != category_name]
    return rules


def get_input_from_user(description, details, rules):
    # Show rules and prompt for input
    category_name_by_rule_number = show_rules_and_get_category_numbers(rules)
    while True:
        print(f"\nDescription: {description}")

        # Create a timedelta object
        duration_td = timedelta(seconds=details["duration"])

        # Extract hours and minutes
        hours, remainder = divmod(duration_td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if duration_td.total_seconds() < 30:
            while True:
                print("Remaining event durations all less than 30 seconds. No reason to continue to categorize.")
                print("Would you like to save and exit categorization ('e'), or quit without saving ('q')?")
                response = input()
                if response == "e":
                    return "save_and_exit", None
                elif response == "q":
                    return "quit_no_save", None
                else:
                    print("Invalid input. Try again.")

        # Check if the duration is less than 5 minutes
        if duration_td.total_seconds() < 300:
            # If less than 5 minutes, include seconds in the output
            formatted_duration = f"{seconds}s" if minutes == 0 else f"{minutes}m, {seconds}s"
        else:
            # Otherwise, format as hours and minutes
            formatted_duration = f"{hours}h, {minutes}m" if hours > 0 else f"{minutes}m"

        print(f"Total Duration: {formatted_duration}")
        days = set(event["timestamp"].day for event in details["events"])
        print(f"Days of Month Occurred: {sorted(days)}")

        response = (
            input(
                "\nEnter the rule number to categorize this event, 'u' to undo, 'n' to create new rule,'s' to skip, "
                "'e' to save and exit categorization loop, or q to quit without saving: "
            )
            .strip()
            .lower()
        )
        if response.isdigit():
            rule_number = int(response)
            if 1 <= rule_number <= len(rules):
                prompt_message = (
                    "\nEnter the new (case-sensitive) string to add as a string search pattern for window titles,"
                    "\nOR simply press enter to match only the exact string: "
                )
                category_name = category_name_by_rule_number[rule_number - 1]  # zero-indexing, adjust by -1

                regex_to_add = input(prompt_message).strip()

                if not regex_to_add:
                    regex_to_add = description.strip()

                # Check if regex_to_add is valid
                if any(char in regex_to_add for char in "|*"):
                    print("Invalid rule name, no '|' or '*' or empty rule allowed. Please try again.")
                    continue

                return "add", (category_name, regex_to_add)

        elif response == "u":
            return "undo", None
        elif response == "s":
            return "skip", None
        elif response == "n":
            name = input("\nEnter the name of the new category: ").strip()
            project_id = input(
                "\nEnter the project id of the new category (or simply hit enter if not work related): "
            ).strip()
            if not project_id:
                project_id = "personal"
            regex_to_add = input(
                "\nEnter a string to match window titles\nOR simply press enter to match the category exactly: "
            ).strip()
            if not regex_to_add:
                regex_to_add = description.strip()
            return "new", {
                "category_name": name + "*" + project_id,
                "regex_to_add": regex_to_add,
            }
        elif response == "e":
            return "save_and_exit", None
        elif response == "q":
            return "quit_no_save", None
        else:
            print("\nInvalid input. Please try again.")


def rules_are_same(rules1, rules2):
    # Check if the number of rules matches
    if len(rules1) != len(rules2):
        return False

    # Sort the rules by category name to ensure they are in the same order
    rules1.sort(key=lambda x: x[0])
    rules2.sort(key=lambda x: x[0])

    # Compare each rule
    for rule1, rule2 in zip(rules1, rules2):
        # Compare category names
        if rule1[0] != rule2[0]:
            print_difference_between_rules_lists(rules1, rules2)
            return False

        # Compare regex patterns (as strings)
        if str(rule1[1].regex) != str(rule2[1].regex):
            print_difference_between_rules_lists(rules1, rules2)
            return False

    # If all checks passed, the rules are the same
    return True


def print_difference_between_rules_lists(rule_list1, rule_list2):
    print("")
    print("Printing out unsaved rule additions so far:")

    # Sort the rules by category name to ensure they are in the same order
    rule_list2.sort(key=lambda x: x[0])
    rule_list1.sort(key=lambda x: x[0])

    # Find new rules in rule_list2 that are not in rule_list1
    rule_list1_names = [rule[0] for rule in rule_list1]

    new_rules = [rule for rule in rule_list2 if rule[0] not in rule_list1_names]
    if new_rules:
        print("New rules found:")
        for rule in new_rules:
            print(f"New category: {rule[0]}, Regex: {rule[1].regex}")
        print("")  # For an extra line break at the end

    # First, check for new rules or removed rules
    existing_rule_list1_names = {tuple(rule[0]): rule for rule in rule_list1}
    existing_rule_list2_names = {tuple(rule[0]): rule for rule in rule_list2}

    new_rules = set(existing_rule_list2_names) - set(existing_rule_list1_names)
    removed_rules = set(existing_rule_list1_names) - set(existing_rule_list2_names)

    for rule_name in new_rules:
        print(f"New rule added: {rule_name}")

    for rule_name in removed_rules:
        print(f"Rule removed: {rule_name}")

    # Now compare the rules present in both
    common_rules = set(existing_rule_list1_names) & set(existing_rule_list2_names)
    differences_found = False
    for rule_name in common_rules:
        if (
            existing_rule_list1_names[rule_name][1].regex.pattern
            != existing_rule_list2_names[rule_name][1].regex.pattern
        ):
            differences_found = True

            print(
                f"Regex pattern update for '{rule_name[0]}': '{existing_rule_list1_names[rule_name][1].regex.pattern}'"
                f" (Original) != '{existing_rule_list2_names[rule_name][1].regex.pattern}' (Updated)"
            )

    if not differences_found and not new_rules:
        # If differences were found, the rules are not the same
        print("No differences! Rules are the same.")
        print("")
    else:
        print("")


def prompt_user_for_categorization(events, rules):
    action_stack = []
    continue_categorization = True

    original_rules = copy.deepcopy(rules)

    first_loop = True
    while True:
        if not first_loop:
            print_difference_between_rules_lists(original_rules, rules)
        first_loop = False
        categorized_events = aw_transform.categorize(events, rules)

        uncategorized_events = get_uncategorized_events(categorized_events)
        sorted_event_groups = get_sorted_event_groups(uncategorized_events)

        if not sorted_event_groups:
            break  # Exit if there are no more event groups to process

        for description, details in sorted_event_groups:
            action, action_details = get_input_from_user(description, details, rules)

            if action == "add":
                category_name, regex_to_add = action_details

                action_stack.append(("add", category_name, regex_to_add))
                print("category_name to add")
                print(category_name)
                rules = add_pattern_to_rules(rules, category_name, regex_to_add)

                break  # Exit the for-loop to refresh the sorted_event_groups

            if action == "new":
                category_name = action_details["category_name"]
                regex_to_add = action_details["regex_to_add"]
                print("category_name to add")
                print(category_name)

                action_stack.append(("new", category_name, regex_to_add))
                rules = add_new_rule(rules, category_name, regex_to_add, ignore_case=False)
                break  # Exit the for-loop to refresh the sorted_event_groups

            elif action == "undo":
                print("action_stack")
                print(action_stack)
                if action_stack:
                    last_action = action_stack.pop()
                    print("last_action")
                    print(last_action)
                    print("last_action[0]")
                    print(last_action[0])
                    if last_action[0] == "add":
                        category_name, regex_to_remove = last_action[1:]

                        rules = remove_pattern_from_rules(rules, category_name, regex_to_remove)
                    elif last_action[0] == "new":
                        rules = remove_rule(rules, category_name)
                    else:
                        print(
                            "Last action must have been adding regex or"
                            "making new rule to undo. Nothing was undone.\n"
                        )
                        input("Press enter to continue.")

                    break  # Exit the for-loop to refresh the sorted_event_groups
                else:
                    print("No actions to undo.")

            elif action == "skip":
                continue  # Skip this event and continue with the next one

            elif action == "save_and_exit":
                # we ran through all the rules and classified everything
                print_summary_and_maybe_process_actions(action_stack, rules)
                return rules  # Return the updated rules after exiting the while loop

            elif action == "quit_no_save":
                return original_rules

    # we ran through all the rules and classified everything
    print_summary_and_maybe_process_actions(action_stack, rules)
    return rules


def main():
    print("")
    print("getting AW buckets from json..")

    rules = get_rules()

    # Use the loaded events to categorize them
    events = load_events_from_json(AW_BUCKETS_UNCLASSIFIED)

    # show_rules_and_get_category_numbers(rules)
    # First we will show, sorted in order from longest to shortest total duration of matching events, the
    # rule number, the rule description, and the rule's matching regex codes.
    # You show the rules in order longest to shortest from 1 to N, N being the total number of rules
    # Each rule is shown first with the number of the rule, then their associated description,
    # and then the list of matching texts used by the rule.
    # Events with no matching times are listed last in arbitrary order, but still numbered.
    #
    # Second, the user is shown the list of current project id's with associated regex matching strings.
    # The user is prompted in a loop to create regex categorization rules.
    #     - for each unique event description, summed over all instances then sorted longest to shortest by total
    #       duration, the user is shown the event details
    #           - event details:
    #                 - event duration
    #                 - event description
    #                 - which numeric day(s) of the month the event occurred
    #     - The user is prompted to enter a number from 1 through N which identifies the rule category
    #       to add a code for, or the user can enter 'u', 'n', or 'e'
    #         - 'u': undo the last creation of rule or addition of regex code to rule, depending
    #                on the user's previous selection
    #         - 'n': create an entirely new rule
    #              - the user is prompted three times:
    #                   - first for the project id
    #                   - second for the rule description
    #                   - third for the first regex code to add
    #         - 'e': to exit and stop categorizing events
    rules = prompt_user_for_categorization(events, rules)
    categorized_events = aw_transform.categorize(events, rules)
    convert_categorized_data_to_csv(categorized_events)


if __name__ == "__main__":
    main()
