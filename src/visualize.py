import pandas as pd
import json
import tabulate


def convert_timetable_to_pandas_dataframe(timetables: list[dict], index: int):
    """
    Function to convert timetable to pandas dataframe for better visualization

    Args:
        timetables (list[dict]): List of timetables
        index (int): Index of timetable to be converted to pandas dataframe

    Returns:
        class_df (pd.DataFrame): Dataframe containing class schedule
        midsem_df (pd.DataFrame): Dataframe containing midsem schedule
        compre_df (pd.DataFrame): Dataframe containing compre schedule
    """
    timetable = timetables[index]
    timetable = timetable["timetable"]
    class_df = pd.DataFrame(columns=["Course", "Section", "Days", "Time"])
    midsem_df = pd.DataFrame(columns=["Course", "Date", "Time"])
    compre_df = pd.DataFrame(columns=["Course", "Date", "Time"])

    for course in timetable:
        for section in timetable[course]["sections"]:
            for schedule in timetable[course]["sections"][section]["schedule"]:
                temp = pd.DataFrame(
                    {
                        "Course": course,
                        "Section": section,
                        "Days": " ".join(schedule["days"]),
                        "Time": " ".join([str(i) for i in schedule["hours"]]),
                    },
                    index=[0],
                )
                class_df = pd.concat([class_df, temp])
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

    class_df = class_df.sort_values(by=["Days", "Time"])
    class_df.reset_index(drop=True, inplace=True)
    class_df.index += 1

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
    dfs = convert_timetable_to_pandas_dataframe(timetables, index)
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
