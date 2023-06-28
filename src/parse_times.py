import pandas as pd


def parse_midsem_time(midsem_time: str, year: int) -> str:
    """
    Function to parse the midsem time from the string given by ttd, to ISO format for easier consumption in the web site.

    Args:
        midsem_time (str): The string given by ttd for the midsem time. (Format: "13/03 11.30 - 1.00PM")
        year (int): The ayear of the timetable. (example: 2021)

    Returns:
        str: The midsem time in ISO format. (example: "2021-03-13T11:30:00|2021-03-13T13:00:00")
    """
    parts = midsem_time.split()

    date_in_year = parts[0].split("/")

    date = date_in_year[0] + "-" + date_in_year[1] + "-" + str(year)

    start = parts[1].split(".")
    end = parts[3].split(".")

    end_time = end[1][-2:]
    end[1] = end[1][:-2]

    start_pm = start.copy()

    if end_time == "PM":
        end[0] = str(int(end[0]) + 12)
        start_pm[0] = str(int(start_pm[0]) + 12)

    start_date_am = date + "T" + start[0] + ":" + start[1] + ":00"
    start_date_pm = date + "T" + start_pm[0] + ":" + start_pm[1] + ":00"

    end_date = date + "T" + end[0] + ":" + end[1] + ":00"
    end_date = pd.to_datetime(end_date, dayfirst=True).isoformat()
    end_date = pd.Timestamp(end_date) - pd.Timedelta(hours=5, minutes=30)

    start_date_am = pd.to_datetime(start_date_am, dayfirst=True).isoformat()
    start_date_pm = pd.to_datetime(start_date_pm, dayfirst=True).isoformat()

    if end_time == "PM":
        if pd.Timestamp(start_date_pm) > pd.Timestamp(end_date):
            start_date_am = pd.Timestamp(start_date_am) - pd.Timedelta(
                hours=5, minutes=30
            )
            return str(start_date_am.isoformat()) + "|" + str(end_date.isoformat())

        else:
            start_date_pm = pd.Timestamp(start_date_pm) - pd.Timedelta(
                hours=5, minutes=30
            )
            return str(start_date_pm.isoformat()) + "|" + str(end_date.isoformat())

    else:
        start_date_am = pd.Timestamp(start_date_am) - pd.Timedelta(hours=5, minutes=30)
        return str(start_date_am.isoformat()) + "|" + str(end_date.isoformat())
