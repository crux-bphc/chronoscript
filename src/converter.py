import pdfplumber  # https://github.com/jsvine/pdfplumber
import polars as pl  # https://www.pola.rs/


def formatted_table(table):
    """
    Checks if the table is empty
    -----------------------------------------------------------------------
    Formats the table to:
    1) remove column headers
    2) replaces \\n with whitespace to avoid formatting issues in final csv
            e.g.  10/07\\n9:30 - 11:00AM  -->    10/07   9:30 - 11:00AM

    """
    if table:
        table = table[2:]
        for item in table:
            if "\n" in item[-2]:
                item[-2] = item[-2].replace("\n", "  ")
                return table
    else:
        return []


def extract_from_multiple_pages(pages):
    """

    Takes a list of pdfplumber.page objects as input then
    Iterates through the list of pages extracting tables on each page
    and adding it to the final dataframe to be converted into csv file

    """
    df = pl.DataFrame()
    for page in pages:
        table = page.extract_table()
        table = formatted_table(table)
        df = df.vstack(pl.DataFrame(table, orient="row"))
    return df


file = r""  # input pdf filepath
pdf = pdfplumber.open(file)
pages = pdf.pages[:]  # pages to be converted

data = extract_from_multiple_pages(pages)

data.write_csv(file.split(".")[0] + ".csv")
