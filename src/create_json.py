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
    tt: pd.DataFrame = pd.read_csv("output.csv")
    final_json: dict = {}
    tt.columns = columns
    tt.drop(columns=["L", "P", "U"], inplace=True)

    # Filling all empty rows with the previous row's value for simplicity
    tt.fillna(method="ffill", inplace=True)
    tt.to_csv("output2.csv", index=False)

    for _, row in tt.iterrows():
        course_code = row["course_code"]

        if final_json.get(course_code) is None:
            final_json[course_code] = {}
        if final_json[course_code].get("course_name") is None:
            final_json[course_code]["course_name"] = row["course_name"]
        if final_json[course_code].get("sections") is None:
            final_json[course_code]["sections"] = {}

        section = int(row["section"])
        if row["course_name"] == "Tutorial":
            section = "T" + str(section)
        elif row["course_name"] == "Practical":
            section = "P" + str(section)
        else:
            section = "L" + str(section)
        if final_json[course_code]["sections"].get(section) is None:
            final_json[course_code]["sections"][section] = {}

        if final_json[course_code]["sections"][section].get("instructor") is None:
            final_json[course_code]["sections"][section]["instructor"] = set()

        final_json[course_code]["sections"][section]["instructor"].add(
            row["instructor"]
        )

        if final_json[course_code]["sections"][section].get("schedule") is None:
            final_json[course_code]["sections"][section]["schedule"] = []

        final_json[course_code]["sections"][section]["schedule"].append(
            {
                "room": row["room"],
                "days": list(row["days"].split()),
                "hours": [int(x) for x in list(row["hours"].split())],
            }
        )

        final_json[course_code]["sections"][section]["schedule"] = list(
            {
                v["room"]: v
                for v in final_json[course_code]["sections"][section]["schedule"]
            }.values()
        )

        if final_json[course_code].get("exams") is None:
            final_json[course_code]["exams"] = []

        final_json[course_code]["exams"].append(
            {
                "midsem": row["midsem"],
                "compre": row["compre"],
            }
        )

        final_json[course_code]["exams"] = list(
            {v["midsem"]: v for v in final_json[course_code]["exams"]}.values()
        )

    # convert file to serializable format
    convert_all_sets_to_list_recursive(final_json)
    # output the json file
    json.dump(final_json, open("timetable.json", "w"), indent=4)
