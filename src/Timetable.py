from enum import Enum


class Type(str, Enum):
    CDC = "CDC"
    DEL = "DEL"
    HUEL = "HUEL"
    OPEL = "OPEL"


class TimetableCell:
    def __init__(self, code: str, section: str, type: Type):
        self.code = code
        self.section = section
        self.type = type


class Timetable:
    def __init__(self, num, n_days, n_hours):
        self.num = num
        self.timetable = [[None for _ in range(n_days)] for _ in range(n_hours)]
        self.daily_tally = {
            "Monday": 0,
            "Tuesday": 0,
            "Wednesday": 0,
            "Thursday": 0,
            "Friday": 0,
            "Saturday": 0,
            "Sunday": 0,
        }

    def add(self, cell: TimetableCell, day: str, hour: int):
        if self.timetable[hour][day] is not None:
            return False
        self.timetable[hour][day] = cell
        self.daily_tally[day] += 1
        return True
