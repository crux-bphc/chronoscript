import pandas as pd


def parse_time(time: str, year: int, midsem=True) -> str:
    """
    Function to parse the time from the string given by ttd, to ISO format for easier consumption in the web site.

    Args:
        time (str): The string given by ttd for the time. (Format: "13/03 11.30 - 1.00PM")
        year (int): The year of the timetable. (example: 2023)

    Returns:
        str: The time in ISO format. (example: "2023-03-13T11:30:00|2023-03-13T13:00:00")
    """
    if midsem:
        time = time.split()
        time.pop(1)
        time = " ".join(time)

    parts = time.split()

    date_in_year = parts[0].split("/")

    date = date_in_year[0] + "-" + date_in_year[1] + "-" + str(year)

    start = parts[1].split(".")
    end = parts[3].split(".")

    end_time = end[1][-2:]
    end[1] = end[1][:-2]

    start_pm = start.copy()

    if end_time == "PM":
        # as hours are from 0 to 23, we add 12 to the hours to get the correct time
        if end[0] != "12":
            end[0] = str(int(end[0]) + 12)
        if start_pm[0] != "12":
            start_pm[0] = str(int(start_pm[0]) + 12)

    # mostly unnecessary, but for the sake of completeness
    if end_time == "AM" and end[0] == "12":
        end[0] = "00"

    # consider both cases if end time is PM
    # assumption is exam doesn't last longer than 12 hours (sane)
    # so if end time is PM and start_pm is less than end, then start_pm is correct start
    # otherwise start/start_am is correct start
    start_date_am = date + "T" + start[0] + ":" + start[1] + ":00"
    start_date_pm = date + "T" + start_pm[0] + ":" + start_pm[1] + ":00"
    end_date = date + "T" + end[0] + ":" + end[1] + ":00"

    end_date = pd.to_datetime(end_date, dayfirst=True).isoformat()
    start_date_am = pd.to_datetime(start_date_am, dayfirst=True).isoformat()
    start_date_pm = pd.to_datetime(start_date_pm, dayfirst=True).isoformat()

    # print(start_date_am, start_date_pm, end_date)

    if end_time == "PM":
        if pd.Timestamp(start_date_pm) > pd.Timestamp(end_date):
            start_date_am = pd.Timestamp(start_date_am)
            return (
                (
                    pd.Timestamp(start_date_am) - pd.Timedelta(hours=5, minutes=30)
                ).isoformat()
                + "|"
                + (
                    pd.Timestamp(end_date) - pd.Timedelta(hours=5, minutes=30)
                ).isoformat()
            )

        else:
            start_date_pm = pd.Timestamp(start_date_pm)
            return (
                str(
                    (
                        pd.Timestamp(start_date_pm) - pd.Timedelta(hours=5, minutes=30)
                    ).isoformat()
                )
                + "|"
                + (
                    pd.Timestamp(end_date) - pd.Timedelta(hours=5, minutes=30)
                ).isoformat()
            )

    else:
        start_date_am = pd.Timestamp(start_date_am)
        return (
            (
                pd.Timestamp(start_date_am) - pd.Timedelta(hours=5, minutes=30)
            ).isoformat()
            + "|"
            + (pd.Timestamp(end_date) - pd.Timedelta(hours=5, minutes=30)).isoformat()
        )


def parse_compre_time(compre_time: str, year: int):
    """
    Function to parse the compre time from the string given by ttd, to ISO format for easier consumption in the web site.

    Args:
        compre_time (str): The string given by ttd for the compre time. (Format: "19/05 FN")
        year (int): The year of the timetable. (example: 2023)

    Returns:
        str: The compre time in ISO format. (example: "2023-05-19T09:30:00|2023-05-19T12:30:00")
    """
    lookup = {"FN": "9.30 - 12.30PM", "AN": "2.00 - 5.00PM"}
    if compre_time != "null":
        time = compre_time.split()[0] + " " + lookup[compre_time.split()[1]]
        return parse_time(time, year, False)
    else:
        return "null"


if __name__ == "__main__":
    print(parse_time("14/10 - 4.00 - 5.30PM", 2023))
    print(parse_compre_time("21/12 AN", 2023))
