"""
This module takes a specific set of information from NHGIS and returns
a pandas DataFrame that follows MGGG naming conventions.

This is one of a few ways we can collect 2019 5Y ACS data from the
census. Forunately, one file contains ACS Race and Origin infomation for
all Block Groups in the country.

Since this data can only be downloaded manually from the NHGIS website,
per licensing rules, we can only check if the data exists.

Finally, in the settings, we set as the get_nhgis_race_bgs as the engine
for get_race_origin_bgs.

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
Refactored by @gomotopia, May 2021, in debt to the original MGGG-Tooling 
by @InnovativeInventor's with heavy credit due to @jenni-niels for the
data processing techniques.

The National Historical Geographic Information System seeks to
simpify the collection of Census data. NHGIS data is easy to find,
but is not available by API and must be downloaded. Furthermore,
this download requires an account and a pledge not to distribute the
information.

With a focus on 2019 ACS CVAP data, these scripts use B03002, "Hispanic
or Latino Origin by Race" to populate information for the Districtr App.
The filename for downloads from NHGIS, follow a pattern.

!!! Don't forget to set your own in settings.py !!!

/nhgis0004_ds244_20195_2019_blck_grp_csv.zip
|---(1)---|-----------(2)-----------|(3)|(4)

(1) Is sequential to each NHGIS account. Check the last digit!
    The download and folder is only named using this first part.
(2) This second part roughtly indicates that we want 5YrACS data
    ending in 2019 down to the Block Group level. We're able to
    download the whole nation at once.
(3) Reveals that these are stored in csv's.
(4) Finally, the extension indicates a zip or a csv.

Within the NHGIS folder, there is a csv and comes with useful
metadata. For NHGIS, estimates from table B30002 are prefixed with
ALUKE.
"""
import os
import us
import polars as pl # Polars reads csv's faster than pandas!

# To make work in project or editor namespace
try: import settings as SET
except: import tools.settings as SET


# A dictionary that converts NHGIS codes to MGGG-standard names
NHGIS_RACE_NAMES = {
    "ALUKE001": "TOTPOP",
    "ALUKE003": "NH_WHITE",
    "ALUKE004": "NH_BLACK",
    "ALUKE005": "NH_AMIN",
    "ALUKE006": "NH_ASIAN",
    "ALUKE007": "NH_NHPI",
    "ALUKE008": "NH_OTHER",
    "ALUKE009": "NH_2MORE",
    "ALUKE012": "HISP"
}

def check_nhgis_data():
    """
    Checks if NHGIS csv file exists in the location specified by the
    settings. If none found, an exception is raised.

    Returns
    -------
    str
        Filepath from settings of NHGIS file.

    Raises
    ------
    ValueError
        If no file exists at the NHGIS filepath found in the settings.

    """
    file_exists = False
    if os.path.isfile(SET.LOCAL_NHGIS_CSV):
        file_exists = True
    else:
        # NB: you need to get this file manually
        raise ValueError("No NHGIS file found. " + \
                                           "Please fetch NHGIS data manually.")
    return SET.LOCAL_NHGIS_CSV if file_exists else ""

def get_nhgis_race_bgs(state_abbr: str):
    """
    This returns a pandas DataFrame of NHGIS ACS 2019 Race and Origin
    data filtered by the given state in columns following MGGG naming
    standards.

    Notes
    -----
    No Exceptions are thrown in case the csv reader has any problems.
    Does not verify that this csv file has the proper structure and
    headings of an NHGIS file.

    Parameters
    ----------
    state_abbr: str
        Two-letter state abbreviation of target state.

    Returns
    -------
    pandas.dataFrame or null
        dataFrame of state BGs Race and Origin data from NHGIS following
        MGGG naming standards.

    """
    state = us.states.lookup(state_abbr)
    state_nhgis_bgs = ""
    if check_nhgis_data():

        # Create pandas DataFrame of Blockgroup Race Data from NHGIS
        nhgis_bgs_pl = pl.scan_csv(SET.LOCAL_NHGIS_CSV)

        # Filter for specific state
        state_nhgis_bgs = (
            nhgis_bgs_pl.filter(pl.lazy.col("STATE").str_contains(state.name))
            .collect()
            .to_pandas()
        )
        # Use only last part of long GEOID, rename columns
        state_nhgis_bgs["GEOID"] = (state_nhgis_bgs["GEOID"]
                                    .apply(lambda x: x[7:]))
        state_nhgis_bgs = state_nhgis_bgs.rename(columns=NHGIS_RACE_NAMES)

        #Keep only GEOID and named columns
        state_nhgis_bgs = (state_nhgis_bgs[ ["GEOID"]
            + list(NHGIS_RACE_NAMES.values())])

    return state_nhgis_bgs
