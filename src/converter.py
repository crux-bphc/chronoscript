import pdfplumber
import pandas as pd


def remove_headers(
    table: list[list[str]], remove_rows_containing_any_of: list[str]
) -> list[list[str]]:
    new_table: list[list[str]] = []
    for row in table:
        transfer: bool = True
        for string in remove_rows_containing_any_of:
            if string in row:
                transfer: bool = False
                break
        if transfer:
            new_table.append(row)
    return new_table


def convert_timetable_to_csv(pages: list[pdfplumber.page.Page]) -> pd.DataFrame():
    df = pd.DataFrame()
    for page in pages:
        table = page.extract_table()
        table = remove_headers(
            table,
            [
                "TIMETABLE & EXAMS DIVISION TIMETABLE SECOND SEMESTER 2022-2023\nI YEAR FD(2022)",
                "COM\nCOD",
            ],
        )
        df = pd.concat([df, pd.DataFrame(table)])
    return df


file: str = r"Timetable_II_sem_2022_-23_of_FD_I_Year.pdf"  # input pdf filepath
pdf: pdfplumber.pdf.PDF = pdfplumber.open(file)
pages: list[pdfplumber.page.Page] = pdf.pages[7:19]  # pages to extract from

data: pd.DataFrame = convert_timetable_to_csv(pages)
data.to_csv("output.csv", index=False)  # output csv filepath
