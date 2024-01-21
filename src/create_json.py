import pandas as pd
import numpy as np
import json
from parse_times import parse_time, parse_compre_time


def isnan(value):
    """
    Function to check if a value is NaN.

    Args:
        value: The value to check.

    Returns:
        bool: True if the value is NaN, False otherwise.
    """
    try:
        import math

        return math.isnan(float(value))
    except:
        return False


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


def null_empty_exams(course_json: dict) -> dict:
    """
    Function to nullify empty exams in a course json.

    Args:
        course_json (dict): The course json to nullify empty exams in.

    Returns:
        dict: The course json with empty exams nullified.
    """
    for course_code in course_json["courses"]:
        course = course_json["courses"][course_code]
        if len(course.get("exams")) == 0:
            course["exams"] = [{}]
        if len(course.get("exams_iso")) == 0:
            course["exams_iso"] = [{}]
        if course["exams"][0].get("midsem") == None:
            course["exams"][0]["midsem"] = None
        if course["exams"][0].get("compre") == None:
            course["exams"][0]["compre"] = None
        if course["exams_iso"][0].get("midsem") == None:
            course["exams_iso"][0]["midsem"] = None
        if course["exams_iso"][0].get("compre") == None:
            course["exams_iso"][0]["compre"] = None

    return course_json


def create_json_file(
    timetable: pd.DataFrame,
    columns: list[str],
    output_file: str,
    year: int,
    academic_year: int,
    semester: int,
) -> None:
    """
    Function to create a json file from a timetable dataframe.

    Args:
        timetable (pd.DataFrame): The timetable dataframe to create the json file from.
        columns (list[str]): The columns of the dataframe.
        output_file (str): The name of the output json file.
        year (int): The academic year of the timetable. (example: 2023)
        academic_year (int): The academic year of the timetable. (example: 2021 is for acad year 2021-2022)
        semester (int): The semester of the timetable. (example: 1 is for odd semester, 2 is for even semester)
    """
    tt: pd.DataFrame = timetable
    course_json: dict = {}
    tt.columns = columns
    tt.drop(columns=["serial"], inplace=True)

    # Filling all empty rows with the previous row's value for simplicity
    # tt.fillna(method="ffill", inplace=True)

    cols = [
        "course_code",
        "course_name",
        "section",
        "instructor",
    ]
    tt.loc[:, cols] = tt.loc[:, cols].ffill()

    for _, row in tt.iterrows():
        course_code = row["course_code"]

        # initialize course and course details if not already initialized
        if course_json.get(course_code) is None:
            course_json[course_code] = {}
            course_json[course_code]["units"] = row["U"]
            course_json[course_code]["lecture units"] = row["L"]
            course_json[course_code]["practical units"] = row["P"]
        if course_json[course_code].get("course_name") is None:
            course_json[course_code]["course_name"] = row["course_name"]
        if course_json[course_code].get("sections") is None:
            course_json[course_code]["sections"] = {}

        # make sure sections of different kinds of classes (lecture, tutorial, practical) are not overwritten by each other
        # to make sure of that, and for common lingo, we add a prefix to the section number
        section = int(row["section"])
        if row["course_name"] == "Tutorial":
            section = "T" + str(section)
        elif (row["course_name"] == "Practical") or (
            course_json[course_code]["lecture units"] == "-"
            and course_json[course_code]["practical units"] != "-"
        ):
            section = "P" + str(section)
        else:
            section = "L" + str(section)

        # initialize section and section details if not already initialized
        if course_json[course_code]["sections"].get(section) is None:
            course_json[course_code]["sections"][section] = {}

        if course_json[course_code]["sections"][section].get("instructor") is None:
            course_json[course_code]["sections"][section]["instructor"] = set()

        # add instructor to the set of instructors for the section
        course_json[course_code]["sections"][section]["instructor"].add(
            row["instructor"]
        )

        # initialize schedule if not already initialized
        if course_json[course_code]["sections"][section].get("schedule") is None:
            course_json[course_code]["sections"][section]["schedule"] = []

        # add schedule to the list of schedules for the section
        # list of schedules is a list of dictionaries, where each dictionary is a schedule
        # we kept it as a list, as a class may have multiple schedules (eg: "T Th @ 4" and "S @ 2")
        dictionary = {}
        if not isnan(row["room"]):
            dictionary["room"] = row["room"]
        else:
            dictionary["room"] = np.nan

        if not isnan(row["days"]):
            dictionary["days"] = tuple(row["days"].split())
        else:
            dictionary["days"] = np.nan

        if not isnan(row["hours"]):
            dictionary["hours"] = tuple([int(x) for x in list(row["hours"].split())])
        else:
            dictionary["hours"] = np.nan

        if not (
            isnan(dictionary["room"])
            and isnan(dictionary["days"])
            and isnan(dictionary["hours"])
        ):
            course_json[course_code]["sections"][section]["schedule"].append(dictionary)

        # remove duplicate schedules
        course_json[course_code]["sections"][section][
            "schedule"
        ] = remove_duplicate_dicts(
            course_json[course_code]["sections"][section]["schedule"]
        )

        # initialize exams if not already initialized
        if course_json[course_code].get("exams") is None:
            course_json[course_code]["exams"] = []

        exam_dict = {}
        # add exams to the list of exams for the course
        if not isnan(row["midsem"]):
            exam_dict["midsem"] = row["midsem"]

        if not isnan(row["compre"]):
            exam_dict["compre"] = row["compre"]

        if exam_dict:
            course_json[course_code]["exams"].append(exam_dict)

        # remove duplicate exams
        course_json[course_code]["exams"] = remove_duplicate_dicts(
            course_json[course_code]["exams"]
        )

    # parse exam times
    for course_code in course_json:
        # remove lecture units, practical units
        del course_json[course_code]["lecture units"]
        del course_json[course_code]["practical units"]
        exams_list = course_json[course_code]["exams"]
        exams_iso = []
        for exam in exams_list:
            exam_iso = {}

            if exam.get("midsem"):
                exam_iso["midsem"] = parse_time(exam["midsem"], year)

            if exam.get("compre"):
                exam_iso["compre"] = parse_compre_time(exam["compre"], year)

            if exam_iso:
                exams_iso.append(exam_iso)
        # remove duplicate exams
        course_json[course_code]["exams_iso"] = remove_duplicate_dicts(exams_iso)

    # convert file to serializable format
    convert_all_sets_to_list_recursive(course_json)
    final_json = {}
    final_json["metadata"] = {
        "acadYear": academic_year,
        "semester": semester,
    }
    final_json["courses"] = course_json

    final_json = null_empty_exams(final_json)

    # output the json file
    json.dump(final_json, open(output_file, "w"), indent=4)


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

    timetable = pd.read_csv("./files/output.csv")

    create_json_file(timetable, columns, "./files/timetable.json", 2023, 2023, 1)
