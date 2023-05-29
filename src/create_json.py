import pandas as pd
import json


def convert_all_sets_to_list_recursive(obj: dict) -> dict:
    """
    Function to convert all sets in a dictionary to lists recursively. This is done because sets are not serializable.

    Args:
        obj (dict): The dictionary to convert the sets in.

    Returns:
        dict: The dictionary with all sets converted to lists.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = convert_all_sets_to_list_recursive(value)
    elif isinstance(obj, set):
        obj = list(obj)
    return obj


def remove_duplicate_dicts(l: list[dict]) -> list[dict]:
    """
    Function to remove duplicate dictionaries from a list of dictionaries.

    Args:
        l (list[dict]): The list of dictionaries to remove duplicates from.

    Returns:
        list[dict]: The list of dictionaries with duplicates removed.
    """
    seen = set()
    new_l = []
    for d in l:
        t = tuple(sorted(d.items()))
        if t not in seen:
            seen.add(t)
            new_l.append(d)

    return new_l


if __name__ == "__main__":
    # reorder the columns as and when needed
    columns = [
        "serial",
        "course_code",
        "course_name",
        "L",
        "P",
        "U",
        "section",
        "instructor",
        "room",
        "days",
        "hours",
        "midsem",
        "compre",
    ]

    tt: pd.DataFrame = pd.read_csv("output.csv")
    final_json: dict = {}
    tt.columns = columns
    tt.drop(columns=["serial", "L", "P", "U"], inplace=True)

    # Filling all empty rows with the previous row's value for simplicity
    tt.fillna(method="ffill", inplace=True)

    for _, row in tt.iterrows():
        course_code = row["course_code"]

        # initialize course and course details if not already initialized
        if final_json.get(course_code) is None:
            final_json[course_code] = {}
        if final_json[course_code].get("course_name") is None:
            final_json[course_code]["course_name"] = row["course_name"]
        if final_json[course_code].get("sections") is None:
            final_json[course_code]["sections"] = {}

        # make sure sections of different kinds of classes (lecture, tutorial, practical) are not overwritten by each other
        # to make sure of that, and for common lingo, we add a prefix to the section number
        section = int(row["section"])
        if row["course_name"] == "Tutorial":
            section = "T" + str(section)
        elif row["course_name"] == "Practical":
            section = "P" + str(section)
        else:
            section = "L" + str(section)

        # initialize section and section details if not already initialized
        if final_json[course_code]["sections"].get(section) is None:
            final_json[course_code]["sections"][section] = {}

        if final_json[course_code]["sections"][section].get("instructor") is None:
            final_json[course_code]["sections"][section]["instructor"] = set()

        # add instructor to the set of instructors for the section
        final_json[course_code]["sections"][section]["instructor"].add(
            row["instructor"]
        )

        # initialize schedule if not already initialized
        if final_json[course_code]["sections"][section].get("schedule") is None:
            final_json[course_code]["sections"][section]["schedule"] = []

        # add schedule to the list of schedules for the section
        # list of schedules is a list of dictionaries, where each dictionary is a schedule
        # we kept it as a list, as a class may have multiple schedules (eg: "T Th @ 4" and "S @ 2")
        final_json[course_code]["sections"][section]["schedule"].append(
            {
                "room": row["room"],
                "days": tuple(row["days"].split()),
                "hours": tuple([int(x) for x in list(row["hours"].split())]),
            }
        )

        # remove duplicate schedules
        final_json[course_code]["sections"][section][
            "schedule"
        ] = remove_duplicate_dicts(
            final_json[course_code]["sections"][section]["schedule"]
        )

        # initialize exams if not already initialized
        if final_json[course_code].get("exams") is None:
            final_json[course_code]["exams"] = []

        # add exams to the list of exams for the course
        final_json[course_code]["exams"].append(
            {
                "midsem": row["midsem"],
                "compre": row["compre"],
            }
        )

        # remove duplicate exams
        final_json[course_code]["exams"] = remove_duplicate_dicts(
            final_json[course_code]["exams"]
        )

    # convert file to serializable format
    convert_all_sets_to_list_recursive(final_json)
    # output the json file
    json.dump(final_json, open("timetable.json", "w"), indent=4)
