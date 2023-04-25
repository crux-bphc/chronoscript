---
sidebar_position: 2
---

# Converter.py

## Libraries

- [Pdfplumber](https://github.com/jsvine/pdfplumber) \- Extracting raw data from pdf
- [Polars](https://www.pola.rs/) \- formatting and converting data to csv

## formatted_table

Checks if the table is empty.

Formats the table to:

- remove column headers
- replaces \n with whitespace to avoid formatting issues in final csv
  e.g. 10/07\n9:30 - 11:00AM --> 10/07 9:30 - 11:00AM

## extract_from_multiple_pages

Takes a list of pdfplumber.page objects as input then
iterates through the list of pages extracting tables on each page
and adding it to the final dataframe to be converted into csv file
