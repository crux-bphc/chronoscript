import pdfplumber
import pandas as pd


def remove_headers(
    table: list[list[str]], remove_rows_containing_any_of: list[str]
) -> list[list[str]]:
    """
    Function to remove headers from the table. I.e. remove rows that contain any of the strings in the list which do not contribute to the content of the timetable.

    Args:
        table (list[list[str]]): The table to remove the headers from.
        remove_rows_containing_any_of (list[str]): The list of strings to check for in the table, and remove the row if any of the strings are found.

    Returns:
        list[list[str]]: The table with the headers removed.
    """
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
    """
    Function to convert the timetable to a pandas dataframe.

    Args:
        pages (list[pdfplumber.page.Page]): The pages to extract the timetable from.

    Returns:
        pd.DataFrame(): The timetable as a pandas dataframe.
    """
    df = pd.DataFrame()
    for page in pages:
        table = page.extract_table()
        table = remove_headers(
            table,
            headers,
        )
        df = pd.concat([df, pd.DataFrame(table)])
    return df


if __name__ == "__main__":
    # headers to remove from the table
    headers: list[str] = ["COM\nCOD"]

    # page range to extract the timetable from
    # [from, to]
    page_range: list[int] = [7, 68]

    # path to the pdf file
    file: str = r"timetable.pdf"

    pdf: pdfplumber.pdf.PDF = pdfplumber.open(file)

    # might need to play around with the +-1, depending on how the pdf is formatted and how pdfplumber extracts the pages
    pages: list[pdfplumber.page.Page] = pdf.pages[page_range[0] - 1 : page_range[1]]

    data: pd.DataFrame = convert_timetable_to_csv(pages)

    # output the dataframe to csv
    data.to_csv("output.csv", index=False)
