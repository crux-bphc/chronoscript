import json
from itertools import product, combinations
from operator import itemgetter
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

    Args:
        json (dict): main timetable json file
        CDCs (list[str]): list of BITS codes for CDCs selected
        DEls (list[str]): list of BITS codes for DEls selected
        HUELs (list[str]): list of BITS codes for HUELs selected
        OPELs (list[str]): list of BITS codes for OPELs selected

    Returns:
        dict: filtered json file, i.e, with only courses selected
    """
    json = json["courses"]
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

    Args:
        filtered_json (dict): filtered json file, i.e, with only courses selected

    Returns:
        dict: dictionary of courses' sections separated into lectures, tutorials and practicals
    """
    sep = {}

    for type in filtered_json:
        sep[type] = {}
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
            sep[type][course] = {
                "L": lectures,
                "T": tutorials,
                "P": practicals,
            }
            # if list is empty remove the key-value pair
            # we need to remove it as it causes problems when using woth itertools.product()
            if not lectures:
                del sep[type][course]["L"]
            if not tutorials:
                del sep[type][course]["T"]
            if not practicals:
                del sep[type][course]["P"]
    return sep


def generate_intra_combinations(
    filtered_json: Annotated[
        dict, "filtered json file, i.e, with only courses selected"
    ],
) -> dict:
    """
    Function that generates all possible combinations of sections within each course

    Args:
        filtered_json (dict): filtered json file, i.e, with only courses selected

    Returns:
        dict: dictionary of all possible combinations of sections within each course
    """

    sep = separate_sections_into_types(filtered_json)
    combs = {}
    for type in sep:
        combs[type] = {}
        for course in sep[type]:
            sections = []
            # first check is the type of section (L, T or P) is present in the course
            if sep[type][course].get("L") is not None:
                # list of lecture sections
                sections.append(sep[type][course]["L"])
            if sep[type][course].get("P") is not None:
                # list of practical sections
                sections.append(sep[type][course]["P"])
            if sep[type][course].get("T") is not None:
                # list of tutorial sections
                sections.append(sep[type][course]["T"])
            # generate all possible combinations of sections (exhaustive and inclusive of clashes)
            combs[type][course] = list(product(*sections))
    return combs


def generate_exhaustive_timetables(
    filtered_json: Annotated[
        dict, "filtered json file, i.e, with only courses selected"
    ],
    n_dels: Annotated[int, "number of DELs selected"],
    n_opels: Annotated[int, "number of OPELs selected"],
    n_huels: Annotated[int, "number of HUELs selected"],
) -> list:
    """
    Function that generates all possible timetables (exhaustive and inclusive of clashes)

    Args:
        filtered_json (dict): filtered json file, i.e, with only courses selected

    Returns:
        list: list of all possible timetables (exhaustive and inclusive of clashes)
    """

    combs = generate_intra_combinations(filtered_json)
    timetables = []
    cdcs = []
    dels = []
    opels = []
    huels = []
    for type in combs:
        for course in combs[type]:
            # format (course, section combination for that course)
            if type == "CDCs":
                cdcs.append([(str(course), comb) for comb in combs[type][course]])
            elif type == "DEls":
                dels.append([(str(course), comb) for comb in combs[type][course]])
            elif type == "OPELs":
                opels.append([(str(course), comb) for comb in combs[type][course]])
            elif type == "HUELs":
                huels.append([(str(course), comb) for comb in combs[type][course]])
            else:
                raise Exception("Course type not found in any category")

    # choose n_dels from dels
    if dels:
        dels = list(combinations(dels, n_dels))
        dels = [[j[0] for j in i] for i in dels]
    if huels:
        huels = list(combinations(huels, n_huels))
        huels = [[j[0] for j in i] for i in huels]
    if opels:
        opels = list(combinations(opels, n_opels))
        opels = [[j[0] for j in i] for i in opels]

    required = [dels, huels, opels]
    required = [i for i in required if i]
    possible_combinations_temp = list(product(*required))
    possible_combinations = []
    for i in possible_combinations_temp:
        combination = []
        for j in i:
            combination.extend(j)
        possible_combinations.append(combination)
    courses = []

    for comb in possible_combinations:
        poss = []
        poss.extend(cdcs)
        poss.extend([[c] for c in comb])
        courses.append(poss)

    timetables = list(product(*courses))
    timetables = []
    for i in range(len(courses)):
        timetables.extend(list(product(*courses[i])))
    return timetables

    # timetables = list(product(cdcs, dels, huels, opels))
    # return timetables


def remove_clashes(
    timetables: Annotated[list, "exhaustive list of all possible timetables"],
    json: Annotated[dict, "filtered json file"],
) -> list:
    """
    Function that filters out timetables with clashes

    Args:
        timetables (list): exhaustive list of all possible timetables
        json (dict): filtered json file

    Returns:
        list: list of timetables without clashes
    """
    filtered = []
    for timetable in timetables:
        # times currently held as "in use" by some course's section
        # format "DH" where D is the day and H is the hour
        times: dict[str, bool] = dict()
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
                    if times.get(t) is not None:
                        clashes = True
                        break
                    else:
                        times[t] = True
                if clashes:
                    break
            if clashes:
                break
        # if no clashes, add it to the filtered list
        if not clashes:
            filtered.append(timetable)

    return filtered


def remove_exam_clashes(
    timetables: Annotated[list, "list of timetables without any clashes (classes)"],
    json: Annotated[dict, "filtered json file"],
):
    """
    Function that filters out timetables with exam clashes.

    Args:
        timetables (list): list of timetables without any clashes (classes)
        json (dict): filtered json file

    Returns:
        list: list of timetables without any clashes (classes and exams)
    """
    no_exam_clashes = []
    for timetable in timetables:
        mids_times: dict[str, int] = dict()
        compres_times: dict[str, int] = dict()
        clashes = False
        for course in timetable:
            # get exam times
            if course[0] in json["CDCs"]:
                mid = json["CDCs"][course[0]]["exams"][0]["midsem"]
                compre = json["CDCs"][course[0]]["exams"][0]["compre"]
            elif course[0] in json["DEls"]:
                mid = json["DEls"][course[0]]["exams"][0]["midsem"]
                compre = json["DEls"][course[0]]["exams"][0]["compre"]
            elif course[0] in json["HUELs"]:
                mid = json["HUELs"][course[0]]["exams"][0]["midsem"]
                compre = json["HUELs"][course[0]]["exams"][0]["compre"]
            elif course[0] in json["OPELs"]:
                mid = json["OPELs"][course[0]]["exams"][0]["midsem"]
                compre = json["OPELs"][course[0]]["exams"][0]["compre"]
            else:
                raise Exception("Course code not found in any category")
            mids_times[mid] = mids_times.get(mid, 0) + 1
            compres_times[compre] = compres_times.get(compre, 0) + 1
        # see if more than one course has the same exam time
        for time in mids_times:
            if mids_times[time] > 1 and time != "":
                clashes = True
                break
        if not clashes:
            for time in compres_times:
                if compres_times[time] > 1:
                    clashes = True
                    break
        # for i in range(len(mids_times)):
        #     for j in range(i + 1, len(mids_times)):
        #         if mids_times[i] == mids_times[j]:
        #             clashes = True
        #             break
        #     if clashes:
        #         break
        # if not clashes:
        #     for i in range(len(compres_times)):
        #         for j in range(i + 1, len(compres_times)):
        #             if compres_times[i] == compres_times[j]:
        #                 clashes = True
        #                 break
        #         if clashes:
        #             break
        # add to filtered list only if no clashes
        if not clashes:
            no_exam_clashes.append(timetable)
    return no_exam_clashes


def day_wise_filter(
    timetables: Annotated[list, "list of timetables without clashes"],
    json: Annotated[dict, "filtered json file"],
    free_days: Annotated[list[str], "list of days to be free if possible"],
    lite_order: Annotated[
        list[str],
        "increasing order of how lite you want days to be (earlier means more lite)",
    ],
    filter: Annotated[bool, "whether to filter or to just sort"] = False,
    strong: Annotated[bool, "whether to use strong filter or not"] = False,
) -> list:
    """
    Function that filters out timetables based on the number of free days and the lite order. Lite order is the order in which you want the days to be lite. For example, if you want Saturday to be the most lite day, then lite_order = ["S", "Su", "M", "T", "W", "Th", "F"] (set the order of the other 6 accordingly))

    Args:
        timetables (list): list of timetables without clashes
        json (dict): filtered json file, i.e, with only courses selected
        free_days (list): list of days to be free if possible
        lite_order (list): increasing order of how lite you want days to be (earlier means more lite)
        filter (bool, optional): whether to filter or to just sort. Defaults to False.
        strong (bool, optional): whether to use strong filter or not. Defaults to False.

    Returns:
        list: list of timetables after filtering. They are sorted based on how many of the free days they have and how lite the days are.
    """
    # format: (n days matched free, timetable)
    matches_free_days: list[tuple] = []
    # format: (daily scores in a list [0, 4, 5, ...], timetable)
    others: list[tuple] = []

    day_dict = {
        "M": 0,
        "T": 1,
        "W": 2,
        "Th": 3,
        "F": 4,
        "S": 5,
        "Su": 6,
    }

    for timetable in timetables:
        # will contain the hours of each day where there is a class
        # used for calculating the daily scores and if it matches the free days
        schedule = {
            "M": [],
            "T": [],
            "W": [],
            "Th": [],
            "F": [],
            "S": [],
            "Su": [],
        }
        for course in timetable:
            for sec in course[1]:
                # getting the schedule of the selected section
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
                # since no clashes, we can just append the hours to the schedule
                for i in range(len(sched)):
                    for day in sched[i]["days"]:
                        schedule[day].append(sched[i]["hours"])
        # calculating the daily scores
        daily_scores = [len(v) for k, v in schedule.items()]
        # reordering the daily scores to match the lite order
        daily_scores = [daily_scores[day_dict[day]] for day in lite_order]

        n_free = 0
        for day in free_days:
            if len(schedule[day]) == 0:
                n_free += 1

        # if not strong filter, then if atleast some of the required free days are free, then add it to the list
        if n_free > 0 and not strong:
            matches_free_days.append((n_free, daily_scores, timetable))
        elif n_free == len(free_days):
            matches_free_days.append((n_free, daily_scores, timetable))
        else:
            others.append((n_free, daily_scores, timetable))

    # sorting based on the number of free days (descending) and then the daily scores (ascending)
    matches_free_days = sorted(matches_free_days, key=itemgetter(0), reverse=True)
    matches_free_days = sorted(matches_free_days, key=itemgetter(1))

    others = sorted(others, key=itemgetter(0), reverse=True)
    others = sorted(others, key=itemgetter(1))

    # reorder back to original order (M, T, W, Th, F, S, Su)
    original_order = {
        "M": lite_order.index("M"),
        "T": lite_order.index("T"),
        "W": lite_order.index("W"),
        "Th": lite_order.index("Th"),
        "F": lite_order.index("F"),
        "S": lite_order.index("S"),
        "Su": lite_order.index("Su"),
    }
    for i in range(len(matches_free_days)):
        matches_free_days[i] = (
            matches_free_days[i][0],
            [matches_free_days[i][1][original_order[day]] for day in original_order],
            matches_free_days[i][2],
        )

    for i in range(len(others)):
        others[i] = (
            others[i][0],
            [others[i][1][original_order[day]] for day in original_order],
            others[i][2],
        )

    if filter:
        return [i for i in matches_free_days]

    else:
        return [i for i in matches_free_days] + [i for i in others]


def export_to_json(timetables: list, filtered_json: dict, n_export: int = 100) -> None:
    """
    Function that exports your timetables to a json file (in the sorted order)

    Args:
        timetables (list): list of timetables
        filtered_json (dict): filtered json file, i.e, with only courses selected
        n_export (int, optional): number of timetables to export. Defaults to 100.

    Returns:
        None
    """
    export = []
    for timetable in timetables:
        export_tt = {}
        export_tt["free_matched"] = timetable[0]
        export_tt["daily_scores"] = timetable[1]
        export_tt["timetable"] = {}
        for course in timetable[2]:
            export_tt["timetable"][course[0]] = {}
            export_tt["timetable"][course[0]]["sections"] = {}
            for sec in course[1]:
                export_tt["timetable"][course[0]]["sections"][sec] = {}
                export_tt["timetable"][course[0]]["sections"][sec]["schedule"] = []
                if course[0] in filtered_json["CDCs"]:
                    sched = filtered_json["CDCs"][course[0]]["sections"][sec][
                        "schedule"
                    ]
                elif course[0] in filtered_json["DEls"]:
                    sched = filtered_json["DEls"][course[0]]["sections"][sec][
                        "schedule"
                    ]
                elif course[0] in filtered_json["HUELs"]:
                    sched = filtered_json["HUELs"][course[0]]["sections"][sec][
                        "schedule"
                    ]
                elif course[0] in filtered_json["OPELs"]:
                    sched = filtered_json["OPELs"][course[0]]["sections"][sec][
                        "schedule"
                    ]
                else:
                    raise Exception("Course code not found in any category")
                for i in range(len(sched)):
                    export_tt["timetable"][course[0]]["sections"][sec][
                        "schedule"
                    ].append(
                        {
                            "days": sched[i]["days"],
                            "hours": sched[i]["hours"],
                        }
                    )
            if course[0] in filtered_json["CDCs"]:
                exam = filtered_json["CDCs"][course[0]]["exams"][0]
            elif course[0] in filtered_json["DEls"]:
                exam = filtered_json["DEls"][course[0]]["exams"][0]
            elif course[0] in filtered_json["HUELs"]:
                exam = filtered_json["HUELs"][course[0]]["exams"][0]
            elif course[0] in filtered_json["OPELs"]:
                exam = filtered_json["OPELs"][course[0]]["exams"][0]
            else:
                raise Exception("Course code not found in any category")
            export_tt["timetable"][course[0]]["exams"] = exam
        export.append(export_tt)
        if len(export) == n_export:
            break
    json.dump(export, open("my_timetables.json", "w"), indent=4)


if __name__ == "__main__":
    # need to get these as inputs
    CDCs = ["CS F301", "CS F342", "CS F351", "CS F372"]

    # Order the oreference of DELs, HUELs and OPELs

    DEls = ["CS F429", "CS F433"]

    OPELs = ["DE G611", "DE G631"]

    HUELs = []

    pref = ["DEls", "OPELs", "HUELs"]

    free_days = ["S"]

    lite_order = ["S", "Su", "M", "T", "W", "Th", "F"]

    # load the json file created
    tt_json = json.load(open("timetable.json", "r"))

    filtered_json = get_filtered_json(tt_json, CDCs, DEls, HUELs, OPELs)

    exhaustive_list_of_timetables = generate_exhaustive_timetables(
        filtered_json, 1, 0, 0
    )

    timetables_without_clashes = remove_clashes(
        exhaustive_list_of_timetables, filtered_json
    )

    print(
        "Number of timetables without clashes (classes):",
        len(timetables_without_clashes),
    )

    timetables_without_clashes = remove_exam_clashes(
        timetables_without_clashes, filtered_json
    )

    print(
        "Number of timetables without clashes (classes and exams):",
        len(timetables_without_clashes),
    )

    in_my_preference_order = day_wise_filter(
        timetables_without_clashes,
        filtered_json,
        free_days,
        lite_order,
        filter=False,
        strong=False,
    )

    print("Number of timetables after filter: ", len(in_my_preference_order))

    if len(in_my_preference_order) > 0:
        print(
            "-----------------------------------------------------",
            "\nHighest match:\n",
            in_my_preference_order[0],
            "\n\n",
            "-----------------------------------------------------",
            "\nLowest match:\n",
            in_my_preference_order[-1],
        )
    else:
        print("No timetables found")

    export_to_json(in_my_preference_order, filtered_json)
