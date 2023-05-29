import json
from itertools import product
from typing import Annotated


def get_filtered_json(
    json: Annotated[dict, "main timetable json file"],
    CDCs: Annotated[list[str], "list of BITS codes for CDCs selected"],
    DEls: Annotated[list[str], "list of BITS codes for DEls selected"],
    HUELs: Annotated[list[str], "list of BITS codes for HUELs selected"],
    OPELs: Annotated[list[str], "list of BITS codes for OPELs selected"],
) -> dict:
    """
    Function to filter the main timetable json file to only include the selected courses

    Returns:
        dict: filtered json file
    """
    filtered_json = {"CDCs": {}, "DEls": {}, "HUELs": {}, "OPELs": {}}
    for CDC in CDCs:
        filtered_json["CDCs"][CDC] = json[CDC]
    for DEL in DEls:
        filtered_json["DEls"][DEL] = json[DEL]
    for HUEL in HUELs:
        filtered_json["HUELs"][HUEL] = json[HUEL]
    for OPEL in OPELs:
        filtered_json["OPELs"][OPEL] = json[OPEL]
    return filtered_json


def separate_sections_into_types(
    filtered_json: Annotated[
        dict, "filtered json file, i.e, with only courses selected"
    ]
) -> dict:
    """
    Function to separate the sections into lectures, tutorials and practicals

    Returns:
        dict: dictionary of courses' sections separated into lectures, tutorials and practicals
    """
    sep = {}

    for type in filtered_json:
        for course in filtered_json[type]:
            lectures = []
            tutorials = []
            practicals = []
            # inner dictionary we'll be continuously referring to
            ref = filtered_json[type][course]
            for section in ref["sections"]:
                if section.startswith("L"):
                    lectures.append(section)
                elif section.startswith("T"):
                    tutorials.append(section)
                elif section.startswith("P"):
                    practicals.append(section)
            sep[course] = {
                "L": lectures,
                "T": tutorials,
                "P": practicals,
            }
            # if list is empty remove the key-value pair
            # we need to remove it as it causes problems when using woth itertools.product()
            if not lectures:
                del sep[course]["L"]
            if not tutorials:
                del sep[course]["T"]
            if not practicals:
                del sep[course]["P"]

    return sep


def generate_intra_combinations(
    filtered_json: Annotated[
        dict, "filtered json file, i.e, with only courses selected"
    ]
) -> dict:
    """
    Function that generates all possible combinations of sections within each course

    Returns:
        dict: dictionary of all possible combinations of sections within each course
    """

    sep = separate_sections_into_types(filtered_json)
    combs = {}
    for course in sep:
        sections = []
        # first check is the type of section (L, T or P) is present in the course
        if sep[course].get("L") is not None:
            # number of lecture sections
            nLs = len(sep[course]["L"])
            # list of lecture sections
            Ls = ["L" + str(i + 1) for i in range(nLs)]
            sections.append(Ls)
        if sep[course].get("P") is not None:
            # number of practical sections
            nPs = len(sep[course]["P"])
            Ps = ["P" + str(i + 1) for i in range(nPs)]
            # list of practical sections
            sections.append(Ps)
        if sep[course].get("T") is not None:
            # number of tutorial sections
            nTs = len(sep[course]["T"])
            # list of tutorial sections
            Ts = ["T" + str(i + 1) for i in range(nTs)]
            sections.append(Ts)
        # generate all possible combinations of sections (exhaustive and inclusive of clashes)
        combs[course] = list(product(*sections))
    return combs


def generate_exhaustive_timetables(
    filtered_json: Annotated[
        dict, "filtered json file, i.e, with only courses selected"
    ]
) -> list:
    """
    Function that generates all possible timetables (exhaustive and inclusive of clashes)

    Returns:
        list: list of all possible timetables (exhaustive and inclusive of clashes)
    """

    combs = generate_intra_combinations(filtered_json)
    timetables = []
    courses = []
    for course in combs:
        # format (course, section combination for that course)
        courses.append([(str(course), comb) for comb in combs[course]])
    timetables = list(product(*courses))
    return timetables


def remove_clashes(
    timetables: Annotated[list, "exhaustive list of all possible timetables"],
    json: Annotated[dict, "main timetable json file (or) filtered json file"],
):
    """
    Function that filters out timetables with clashes

    Returns:
        list: list of timetables without clashes
    """

    filtered = []
    for timetable in timetables:
        # times currently held as "in use" by some course's section
        # format "DH" where D is the day and H is the hour
        times = []
        clashes = False
        for course in timetable:
            # course[1] as that has the section details, course[0] hold course code
            for sec in course[1]:
                # the schedule of the section from the main json file
                if course[0] in json["CDCs"]:
                    sched = json["CDCs"][course[0]]["sections"][sec]["schedule"]
                elif course[0] in json["DEls"]:
                    sched = json["DEls"][course[0]]["sections"][sec]["schedule"]
                elif course[0] in json["HUELs"]:
                    sched = json["HUELs"][course[0]]["sections"][sec]["schedule"]
                elif course[0] in json["OPELs"]:
                    sched = json["OPELs"][course[0]]["sections"][sec]["schedule"]
                else:
                    raise Exception("Course code not found in any category")
                # ts denotes all slots needed for the section
                ts = []
                for i in range(len(sched)):
                    ts.extend(list(product(sched[i]["days"], sched[i]["hours"])))
                # converting it to the string of required format "DH"
                ts = [str(t[0]) + str(t[1]) for t in ts]
                # if any slot in ts is already in times, then there is a clash
                # if so, mark it as clashes and dont add it to the filtered list
                for t in ts:
                    if t in times:
                        clashes = True
                        break
                    else:
                        times.append(t)
                if clashes:
                    break
            if clashes:
                break
        # if no clashes, add it to the filtered list
        if not clashes:
            filtered.append(timetable)

    return filtered


if __name__ == "__main__":
    # Global Variables

    CDCs = ["CS F211", "CS F212", "CS F241"]

    DEls = ["BITS F464", "CS F469"]

    OPELs = []

    HUELs = ["HSS F346"]

    # Load the json file created

    tt_json = json.load(open("timetable.json", "r"))

    filtered_json = get_filtered_json(tt_json, CDCs, DEls, HUELs, OPELs)

    exhaustive_list_of_timetables = generate_exhaustive_timetables(filtered_json)

    timetables_without_clashes = remove_clashes(
        exhaustive_list_of_timetables, filtered_json
    )

    print("Number of timetables without clashes:", len(timetables_without_clashes))
