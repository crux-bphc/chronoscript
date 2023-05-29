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

    # currently written only for CDCs

    sep = {}
    for cdc in filtered_json["CDCs"]:
        lectures = []
        tutorials = []
        practicals = []
        # inner dictionary we'll be continuously referring to
        ref = filtered_json["CDCs"][cdc]
        for section in ref["sections"]:
            if section.startswith("L"):
                lectures.append(section)
            elif section.startswith("T"):
                tutorials.append(section)
            elif section.startswith("P"):
                practicals.append(section)
        sep[cdc] = {
            "L": lectures,
            "T": tutorials,
            "P": practicals,
        }
        # if list is empty remove the key-value pair
        # we need to remove it as it causes problems when using woth itertools.product()
        if not lectures:
            del sep[cdc]["L"]
        if not tutorials:
            del sep[cdc]["T"]
        if not practicals:
            del sep[cdc]["P"]


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

    # again, written only for CDCs as of now
    sep = separate_sections_into_types(filtered_json)
    combs = {}
    for cdc in sep:
        sections = []
        # first check is the type of section (L, T or P) is present in the course
        if sep[cdc].get("L") is not None:
            # number of lecture sections
            nLs = len(sep[cdc]["L"])
            # list of lecture sections
            Ls = ["L" + str(i + 1) for i in range(nLs)]
            sections.append(Ls)
        if sep[cdc].get("P") is not None:
            # number of practical sections
            nPs = len(sep[cdc]["P"])
            Ps = ["P" + str(i + 1) for i in range(nPs)]
            # list of practical sections
            sections.append(Ps)
        if sep[cdc].get("T") is not None:
            # number of tutorial sections
            nTs = len(sep[cdc]["T"])
            # list of tutorial sections
            Ts = ["T" + str(i + 1) for i in range(nTs)]
            sections.append(Ts)
        # generate all possible combinations of sections (exhaustive and inclusive of clashes)
        combs[cdc] = list(product(*sections))
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

    # written only for CDCs as of now

    combs = generate_intra_combinations(filtered_json)
    timetables = []
    cdcs = []
    for cdc in combs:
        # format (course, section combination for that course)
        cdcs.append([(str(cdc), comb) for comb in combs[cdc]])
    timetables = list(product(*cdcs))
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

    # written only for CDCs as of now

    filtered = []
    for timetable in timetables:
        # times currently held as "in use" by some course's section
        # format "DH" where D is the day and H is the hour
        times = []
        clashes = False
        for cdc in timetable:
            # cdc[1] as that has the section details, cdc[0] hold course code
            for sec in cdc[1]:
                # the schedule of the section from the main json file
                sched = json["CDCs"][cdc[0]]["sections"][sec]["schedule"]
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

    CDCs = ["CS F342", "CS F363", "CS F364"]

    # Currently not working with electives

    DEls = []

    OPELs = []

    HUELs = []

    # Load the json file created

    tt_json = json.load(open("timetable.json", "r"))

    filtered_json = get_filtered_json(tt_json, CDCs, DEls, HUELs, OPELs)

    exhaustive_list_of_timetables = generate_exhaustive_timetables(filtered_json)

    timetables_without_clashes = remove_clashes(
        exhaustive_list_of_timetables, filtered_json
    )

    print("Number of timetables without clashes:", len(timetables_without_clashes))
