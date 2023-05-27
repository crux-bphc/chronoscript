import pandas as pd
import json

# global variables

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


def convert_all_sets_to_list_recursive(obj: dict) -> dict:
    """
    To make the json file serializable, we need to convert all the sets to lists
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = convert_all_sets_to_list_recursive(value)
    elif isinstance(obj, set):
        obj = list(obj)
    return obj


if __name__ == "__main__":
    # Read the csv file
    tt = pd.read_csv("output.csv")
    final_json = {}
    tt.columns = columns
    tt.drop(columns=["L", "P", "U"], inplace=True)
    tt.fillna(method="ffill", inplace=True)

    for _, row in tt.iterrows():
        course_code = row["course_code"]

        if final_json.get(course_code) is None:
            final_json[course_code] = {}
        final_json[course_code]["name"] = row["course_name"]

        if final_json[course_code].get("sections") is None:
            final_json[course_code]["sections"] = {}

        section = int(row["section"])

        if final_json[course_code]["sections"].get(section) is None:
            final_json[course_code]["sections"][section] = {}

        if final_json[course_code]["sections"][section].get("instructor") is None:
            final_json[course_code]["sections"][section]["instructor"] = set()

        final_json[course_code]["sections"][section]["instructor"].add(
            row["instructor"]
        )

        if final_json[course_code]["sections"][section].get("schedule") is None:
            final_json[course_code]["sections"][section]["schedule"] = dict()

        final_json[course_code]["sections"][section]["schedule"].update(
            {
                "room": row["room"],
                "days": list(row["days"].split()),
                "hours": list(row["hours"].split()),
            }
        )

        if final_json[course_code]["sections"][section].get("exams") is None:
            final_json[course_code]["sections"][section]["exams"] = dict()

        final_json[course_code]["sections"][section]["exams"].update(
            {
                "midsem": row["midsem"],
                "compre": row["compre"],
            }
        )

    # pretty print the json file
    convert_all_sets_to_list_recursive(final_json)
    # output the json file
    json.dump(final_json, open("timetable.json", "w"), indent=4)
