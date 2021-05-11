"""
This module takes a specific set of information from the 2019 Census 5Y
ACS using the Census API and returns a pandas DataFrame that follows
MGGG naming conventions.

This is one of a few ways we can collect 2019 5Y ACS data from the
census. Forunately, one file contains ACS Race and Origin infomation for
all Block Groups in the country.

Finally, in the settings, we set as the get_censusapi_race_bgs as the
engine for get_race_origin_bgs.

Examples
--------
This module has two function that can be used separately.

    We can check to see if a proper NHGIS file specified by the settings
    exist using check_nhgis_data. If there is not, an exception occurs.

    This function is used by get_nhgis_race_bgs for a given state which
    returns a pandas dataFrame of ACS data properly specified by MGGG
    names with a GEOID, i.e. shorter ones that start with STATEFIPS and
    not geographic level like the ones found in this file. We need only
    the numbers after the 'US' in longer GEOIDs.

    state_dataframe = ""
    try:
        state_dataframe = get_nhgis_race_bgs("HI")
    except:
        print ("We cannot get NHGIS data for Hawaii")

    In the future, we should be able to return the whole set to keep
    from generating a new dataframe for each state in a batch.

Notes
-----
Refactored by @gomotopia, May 2021, based on a presentation given and
based on code written by @jenni-niels in the MGGG orientation of early
2021. See census2019.md for more docs.

With a focus on 2019 ACS CVAP data, these scripts use B03002, "Hispanic
or Latino Origin by Race" to populate information for the Districtr App.

The Census API for the 2019 5Y ACS Data is as follows...

https://api.census.gov/data/2019/acs/acs5
    ?get=GEO_ID,B03002_001E,B03002_002E
    &for=block%20group:*
    &in=state:01%20county:*

Which returns a header of...
[["GEO_ID","B03002_001E","B03002_002E","state",
                                        "county","tract","block group"]

For each tract in the state.

Where "get" is the information we require, "for" is the specific
geography and in is the specific state or county. The API can only
return one state at a time and the request is limited by finite URL
length.

"""

import os
import us
import pandas as pd
import numpy as np
import requests

try: import settings as SET
except: import tools.settings as SET

# Full Column name e.g. B03002_001E
CENSUS_TABLE = "B03002"
CENSUS_COLUMNS = {
    "001E": "TOTPOP",
    "003E": "NH_WHITE",
    "004E": "NH_BLACK",
    "005E": "NH_AMIN",
    "006E": "NH_ASIAN",
    "007E": "NH_NHPI",
    "008E": "NH_OTHER",
    "009E": "NH_2MORE",
    "012E": "HISP" }

# To convert Census to MGGG naming standards

CENSUS_NAMES = { (CENSUS_TABLE+"_"+col):CENSUS_COLUMNS[col] \
                     for col in CENSUS_COLUMNS}

# Is there no Census folder? Get one.
if not os.path.isdir(SET.LOCAL_CENSUS_FOLDER):
    os.makedirs(SET.LOCAL_CENSUS_FOLDER)

def make_column_chunks(cols: list):
    """
    Takes a list of Census API column names and returns batches, i.e.
    lists, under a certain default CENSUS_BATCH_SIZE

    Notes
    -----
    This creates separate lists of column names because the Census API
    is limited by the finite length of the get URI and we may need to
    make several calls. 

    Parameters
    ----------
    cols: list of str
        A list of lists of size CENSUS_BATCH_SIZE or under partioning
        out the input list of cols.
    """
    num_col_chunks = int(np.ceil(len(cols) / SET.CENSUS_BATCH_SIZE))
    return [cols[i::num_col_chunks] for i in range(num_col_chunks)]

# def check_

def check_censusapi_data(state_abbr: str):
    """
    Checks if the API data of a given state is stored locally. Returns
    filename or null.

    Notes
    -----
    No Exceptions are thrown in case the csv reader has any problems.
    Does not verify that this csv file has the proper structure and
    headings of a Census API resposne.

    Parameters
    ----------
    state_abbr: str
        Two-letter state abbreviation of target state.
    save_allowed: bool
        Flag as to whether to save Census data for later use. If save is
        not enabled, then data from the Census API won't be saved to
        file.

    Returns
    -------
    str or null
        Filename of found data or null if no data is found
    """
    filename = (SET.LOCAL_CENSUS_FOLDER + 
                f"{state_abbr}{SET.LOCAL_CENSUS_SUFFIX}.csv")
    if not os.path.isfile(filename):
        filename = ""
    return filename

def get_censusapi_race_bgs(state_abbr: str, save_allowed = True):
    """
    This returns a pandas DataFrame of ACS 2019 Race and Origin for the
    given state in columns following MGGG naming standards source
    directly from the Census API.

    Will check for local copies of data. Option to save information
    found on API locally. Based on code presented bt @jenni-niels during
    the 2021 MGGG orientation.

    Notes
    -----
    No Exceptions are thrown in case the csv reader has any problems.
    Does not verify that this csv file has the proper structure and
    headings of an NHGIS file.

    Parameters
    ----------
    state_abbr: str
        Two-letter state abbreviation of target state.
    save_allowed: bool
        Flag as to whether to save Census data for later use. If save is
        not enabled, then data from the Census API won't be saved to
        file. 

    Returns
    -------
    pandas.dataFrame or null
        dataFrame of state BGs Race and Origin data from NHGIS following
        MGGG naming standards.

    """
    state = us.states.lookup(state_abbr)
    filename = check_censusapi_data(state_abbr)
    if filename:
        # Load state data saved previously, prevent from rewriting redundantly
        state_data = pd.read_csv(filename, index_col=0)

        # Assure Datatypes
        state_data = state_data.astypes(str)
        col_dtypes = {col:int for col in CENSUS_COLUMNS.values()}
        state_data = state_data.astypes(col_dtypes)
        save_allowed = False
    else: 
        # We must download data from Census directly. 
        # First, we make batches of columns such that we only feed so
        # many columns to the api at a time.
        chunks = make_column_chunks(list(CENSUS_NAMES.keys()))
        state_data = pd.DataFrame()
        for chunk in chunks:
            # Get JSON response of chunk
            column_string = "GEO_ID," + ",".join(chunk)
            url = (
                SET.CENSUS2019_API_URL +
                f"?get={column_string}" +
                f"&for=block%20group:*" + 
                f"&in=state:{state.fips}%20county:*"
            )
            resp = requests.get(url)
            header, *rows = resp.json()

            # Rename and Assure Datatypes
            dtypes = {}
            columns = []
            for json_col in header:
                if json_col in CENSUS_NAMES.keys():
                    columns.append(CENSUS_NAMES[json_col])
                    dtypes[CENSUS_NAMES[json_col]] = int
                else:
                    columns.append(json_col)
                    dtypes[json_col] = str 
            # Merge 
            chunk_data =(pd.DataFrame.from_records(rows, columns=columns)
                            .astype(dtypes))
            if state_data.empty: 
                state_data = chunk_data
            else:
                state_data = pd.merge(state_data, chunk_data, on=["GEO_ID"])

        # Shorten GEO_ID and rename GEOID, ensure as string
        state_data["GEO_ID"] = (state_data["GEO_ID"].apply(lambda x: x[9:]))
        state_data = state_data.rename(columns={"GEO_ID":"GEOID"})
        state_data = state_data.astype({'GEOID': str})

        # Remove state, county, track and block group columns
        # We want to keep GEOID 
        remove_cols = list(
                        set(state_data.columns)-set(CENSUS_COLUMNS.values()))
        remove_cols.remove('GEOID')
        state_data = state_data.drop(columns=remove_cols)

    if save_allowed:
        state_data.to_csv((SET.LOCAL_CENSUS_FOLDER + 
                            f"{state_abbr}{SET.LOCAL_CENSUS_SUFFIX}.csv"))

    return state_data