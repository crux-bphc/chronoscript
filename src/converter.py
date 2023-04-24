import pdfplumber
import polars as pl

file = ""  # input pdf filepath
pdf = pdfplumber.open(file)


pages = pdf.pages[:]  # pages to be converted


data = pl.DataFrame()

for page in pages:  # iterating through the list of pages
    table = page.extract_table()
    if table:
        table = table[2:]  # removing columns headers
    else:
        continue
    for (
        item
    ) in table:  # replacing \n with spaces to avoid formatting issues in csv files
        if "\n" in item[-2]:
            item[-2] = item[-2].replace("\n", "  ")
    data = data.vstack(
        pl.DataFrame(table, orient="row")
    )  # extending dataframes with data from each page


data.write_csv(file.split(".")[0] + ".csv")
