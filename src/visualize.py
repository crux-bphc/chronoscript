import pandas as pd
import json
import tabulate

conversion_dict = {
    1: "8 - 8:50AM",
    2: "9 - 9:50AM",
    3: "10 - 10:50AM",
    4: "11 - 11:50AM",
    5: "12 - 12:50PM",
    6: "1 - 1:50PM",
    7: "2 - 2:50PM",
    8: "3 - 3:50PM",
    9: "4 - 4:50PM",
    10: "5 - 5:50PM",
    11: "6 - 6:50PM",
    12: "7 - 7:50PM",
    13: "8 - 8:50PM",
    14: "9 - 9:50PM",
}


def convert_timetable_to_pandas_dataframe(
    timetables: list[dict], index: int, condensed: bool = True
):
    """
    Function to convert timetable to pandas dataframe for better visualization

    Args:
        timetables (list[dict]): List of timetables
        index (int): Index of timetable to be converted to pandas dataframe
        condensed (bool, optional): Whether to condense the dataframe or not. Defaults to True.

    Returns:
        class_df (pd.DataFrame): Dataframe containing class schedule
        midsem_df (pd.DataFrame): Dataframe containing midsem schedule
        compre_df (pd.DataFrame): Dataframe containing compre schedule
    """
    timetable = timetables[index]
    timetable = timetable["timetable"]
    if condensed:
        class_df = pd.DataFrame(columns=["Course", "Section", "Days", "Time"])
    else:
        class_df = pd.DataFrame(
            columns=[
                "8 - 8:50AM",
                "9 - 9:50AM",
                "10 - 10:50AM",
                "11 - 11:50AM",
                "12 - 12:50PM",
                "1 - 1:50PM",
                "2 - 2:50PM",
                "3 - 3:50PM",
                "4 - 4:50PM",
                "5 - 5:50PM",
                "6 - 6:50PM",
                "7 - 7:50PM",
                "8 - 8:50PM",
                "9 - 9:50PM",
            ],
            index=["M", "T", "W", "Th", "F", "S"],
        )
    midsem_df = pd.DataFrame(columns=["Course", "Date", "Time"])
    compre_df = pd.DataFrame(columns=["Course", "Date", "Time"])

    for course in timetable:
        for section in timetable[course]["sections"]:
            for schedule in timetable[course]["sections"][section]["schedule"]:
                if condensed:
                    temp = pd.DataFrame(
                        {
                            "Course": course,
                            "Section": section,
                            "Days": " ".join(schedule["days"]),
                            "Time": ", ".join(
                                [conversion_dict[i] for i in schedule["hours"]]
                            ),
                        },
                        index=[0],
                    )
                    class_df = pd.concat([class_df, temp])
                else:
                    for day in schedule["days"]:
                        for hour in schedule["hours"]:
                            class_df.loc[day, conversion_dict[hour]] = (
                                course + " " + section
                            )
        exam_details = timetable[course]["exams"]

        temp = pd.DataFrame(
            {
                "Course": course,
                "Date": exam_details["midsem"].split(" ")[0],
                "Time": " ".join(exam_details["midsem"].split(" ")[1:]),
            },
            index=[0],
        )

        midsem_df = pd.concat([midsem_df, temp])

        temp = pd.DataFrame(
            {
                "Course": course,
                "Date": exam_details["compre"].split(" ")[0],
                "Time": " ".join(exam_details["compre"].split(" ")[1:]),
            },
            index=[0],
        )

        compre_df = pd.concat([compre_df, temp])
    if condensed:
        class_df = class_df.sort_values(by=["Days", "Time"])
        class_df.reset_index(drop=True, inplace=True)
        class_df.index += 1

    else:
        class_df.fillna("", inplace=True)

    midsem_df = midsem_df.sort_values(by=["Date"])
    midsem_df.reset_index(drop=True, inplace=True)
    midsem_df.index += 1

    compre_df = compre_df.sort_values(by=["Date"])
    compre_df.reset_index(drop=True, inplace=True)
    compre_df.index += 1

    return class_df, midsem_df, compre_df


if __name__ == "__main__":
    index = 0
    with open("my_timetables.json", "r") as f:
        timetables = json.load(f)
    dfs = convert_timetable_to_pandas_dataframe(timetables, index, False)
    print("======================================================\n")
    print("Class Schedule:\n\n")
    print(tabulate.tabulate(dfs[0], headers="keys", tablefmt="fancy_grid"))
    print("------------------------------------------------------\n")
    print("\nMidsem Schedule:\n\n")
    print(tabulate.tabulate(dfs[1], headers="keys", tablefmt="fancy_grid"))
    print("------------------------------------------------------\n")
    print("\nCompre Schedule:\n\n")
    print(tabulate.tabulate(dfs[2], headers="keys", tablefmt="fancy_grid"))
    print("======================================================\n")
