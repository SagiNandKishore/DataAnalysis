import numpy as np
import pandas as pd
from datetime import datetime
from urllib.error import HTTPError

# This program will attempt to read the USCIS monthly Visa bulletin's and extract the current
# status and future month Green Card processing status.
# Initialize empty DataFrames

india_final_action_dates_df: pd.DataFrame = pd.DataFrame()
india_filing_dates_df: pd.DataFrame = pd.DataFrame()

# Capture status of Employment Based statuses from January-2019 onwards. Additional years are simple
# modifications to below ranges.

for year in [2019, 2020, 2021]:
    for month_id, month in enumerate(["january", "february", "march", "april", "may", "june",
                                      "july", "august", "september", "october", "november", "december"], start=1):
        # In the USCIS visa bulletin page the tables don't use any captions. Hence the order of
        # the tables is being hardcoded into the code. The first table on the page that we want
        # is the final action dates and the second one is the filing dates
        final_action_dates: bool = True

        # Visa bulletins for future dates will not be available and hence we will stop processing if the year and
        # month combination falls in future.
        current_year_month = int(datetime.now().strftime("%Y%m"))
        loop_year_month = int(f"{year}{month_id:0>2}")
        if loop_year_month > current_year_month:
            continue

        # Generate the appropriate VISA bulletin URL and fetch the tables on the page using read_html method.
        visa_bulletin_url = f"https://travel.state.gov/content/travel/en/" \
                            f"legal/visa-law0/visa-bulletin/{year}/visa-bulletin-for-{month}-{year}.html"

        try:
            tables_list = pd.read_html(visa_bulletin_url)
            total = len(tables_list)
            print(f"Total tables found for the month of [{month:^20s}] and year [{year}] is [{total}]")

            for df in tables_list:
                if len(df) <= 1:
                    # Some of the tables on the page are invalid tables. Cleaning up the data for invalid tables
                    continue

                # The dataframe headers and indices are themselves rows and columns in the dataframe. Assigning the
                # header row as the new header.
                try:
                    temp_header = df.iloc[0]
                    df = df[1:]
                    df.columns = temp_header

                    # We are looking for tables that have the first row and first column as Employment- Based.
                    employment_based_df = df["Employment-  based"]

                    # The first table is the final action dates and second table is the filing dates.
                    if final_action_dates:
                        india_final_action_dates_df[f"{year}-{month}"] = df["INDIA"]
                        final_action_dates = False
                    else:
                        india_filing_dates_df[f"{year}-{month}"] = df["INDIA"]

                except KeyError:
                    pass
                except Exception as exc:
                    # print(f"[DF_ERROR_{year}_{month}]:{type(exc)}, {str(exc)}, {len(df)}")
                    pass
        except HTTPError:
            print(f"Visa Bulletin URL for month [{month}] and year [{year}] is invalid")

print(india_final_action_dates_df)
print(india_filing_dates_df)