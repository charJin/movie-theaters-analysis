import os
import sys
import requests
import datetime
import pandas as pd
from requests_html import HTML
import re

BASE_DIR = os.path.dirname(__file__)


def url_to_txt(url):
    r = requests.get(url)
    if r.status_code == 200:
        html_text = r.text
        return html_text
    return None

def parse_and_extract(url):
    html_text = url_to_txt(url)
    if html_text == None:
        return False
    year = re.search(r'\d{4}', url).group()
    requests_html = HTML(html=html_text)
    table_class_str = ".imdb-scroll-table"
    requests_table = requests_html.find(table_class_str)
    if len(requests_table) == 0:
        return None

    parsed_table = requests_table[0]
    table_data = []
    header_names = ["Year"]
    # 'tr' is for each row element and 'th' is for the header titles and 'td' is for the values 
    rows = parsed_table.find("tr")
    header_row = rows[0]
    header_cols = header_row.find('th')
    header_names.extend([x.text for x in header_cols])
    for row in rows[1:]:
        value_cols = row.find("td")
        value_cols_with_year = [year] + [val.text for val in value_cols] 
        row_data = []
        for i, val in enumerate(value_cols_with_year):
            if isinstance(val, str):
                row_data.append(val)
            else:
                row_data.append(val.text)
        table_data.append(row_data)
    df = pd.DataFrame(table_data, columns=header_names)
    df = df[::-1].reset_index(drop=True) #  Reverse rows to convert from reverse chronological order (Dec to Jan) to chronological (Jan to Dec).
    return df


def run_scrape(start_year=None, end_year=None):
    dataframes = []
    if start_year == None:
        start_year = 2014
    if end_year == None:
        end_year = 2024
    now = datetime.datetime.now()
    assert 1977 <= start_year <= now.year, f"start_year must be between 1977 and {now.year}."
    assert 1977 <= end_year <= now.year, f"end_year must be between 1977 and {now.year}."
    assert start_year <= end_year, "start_year must be equal to or less than end_year."

    for year in range(start_year, end_year + 1):
        url = f'https://www.boxofficemojo.com/daily/{year}/?view=year'
        parsed_df = parse_and_extract(url)
        if parsed_df is not None and not parsed_df.empty:
            print(f"Data for {year} has been extracted successfully.")
            dataframes.append(parsed_df)
        else:
            print(f"Failed to parse and extract data for {year}")

    combined_df = pd.concat(dataframes, ignore_index=True)
    path = os.path.join(BASE_DIR, 'data')
    os.makedirs(path, exist_ok=True)
    filepath = os.path.join(path, 'movies_data.csv')
    combined_df.to_csv(filepath, index=False)

if __name__ == "__main__":
    start = int(sys.argv[1]) if len(sys.argv) > 1 else None
    end = int(sys.argv[2]) if len(sys.argv) > 2 else None

    run_scrape(start_year=start, end_year=end)