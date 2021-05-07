"""

Written by @gomotopia, May 2021.

Based on @InnovativeInventor/MGGG-Tooling for the data processing
techniques and in turn, @jenni-niels.

"""

##### Local Settings #####

OUTPUT_FILE = "output.shp"
LOCAL_DATA_FOLDER = "../census"

##### Census CVAP Data, 2015-2019 Estimates, Released Feb. 2021 #####

# Settings for 2019 Census CVAP Data
# See... https://www.census.gov/programs-surveys/decennial-census/
#                   about/voting-rights/cvap.html

CENSUS_URL = "https://www2.census.gov/"
CVAP_NAME = "CVAP_2015-2019_ACS_csv_files"
CVAP_URL = "programs-surveys/decennial/rdo/datasets/2019/2019-cvap/"
CVAP_ZIP_URL = CENSUS_URL + CVAP_URL + CVAP_NAME + ".zip"
BG_CSV = "BlockGr.csv"
LOCAL_DATA_FOLDER = "census"

##### Census Tiger Data, from 2019 #####

# 2019 Block Group shapefiles. Use 2019 data for 2019 ACS and CVAP data.
#   e.g. https://www2.census.gov/geo/tiger/TIGER2019/BG/tl_2019_19_bg.zip

TIGER_PREFIX = "tl_2019_"
BG_POSTFIX = "_bg"

##### Census ACS Data on Race and Origin, 2019 5-Y Estimates #####

### There are different ways to collect ACS data. Import and select your
### preferred function here. The function is specified as follows...

### def get_race_bgs(state_abbrev: str)
### """
### Returns 2019 ACS 5Y Race data from Census Table B03002 for the
### block groups of a selected state.
###
### Parameters
### ----------
### state_abbrev: str
###     Two digit state FIPS state or territory code.
###
### Returns
### -------
### pandas.DataFrame
###     Containing GEOID, short ID, i.e. State, County, Tract... codes
###     without 15000US geo. level and nation prfeix, and demographic
###     columns using MGGG naming standards listed below.
### """

# Using API
"""
from 2019_census_api import get_api_race_bgs
get_race_bgs = get_api_race_bgs
"""

# Using NHGIS data
from nhgis import get_nhgis_race_bgs
get_race_bgs = get_nhgis_race_bgs

# Settings for NHGIS Data. Must be downloaded manually from
# https://www.nhgis.org/. Select from table Census B03002, Hispanic or
# Latino Origin by Race, (NHGIS Code ALUK) for 2019 5Y ACS.

# Watch here! NHGIS_PREFIX may differ for each user.
NHGIS_PREFIX = "nhgis0004"
NHGIS_DATA_NAME = "_ds244_20195_2019_blck_grp"



##### MGGG naming convention from @mggg/mggg-states-qa #####

# More categories in original file "naming_convention.json" found in
# repository listed above.

NAME_CONVENTION = {
    "TOTPOP":
        "Total population",
    "NH_WHITE":
        "White, non-Hispanic",
    "NH_BLACK":
        "Black, non-Hispanic ",
    "NH_AMIN":
        "American Indian and Alaska Native, non-Hispanic",
    "NH_ASIAN":
        "Asian, non-Hispanic",
    "NH_NHPI":
        "Native Hawaiian and Pacific Islander, non-Hispanic",
    "NH_OTHER":
        "Other race, non-Hispanic",
    "NH_2MORE":
        "Two or more races, non-Hispanic",
    "HISP":
        "Hispanic",
    "H_WHITE":
        "White, Hispanic",
    "H_BLACK":
        "Black, Hispanic",
    "H_AMIN":
        "American Indian and Alaska Native, Hispanic",
    "H_ASIAN":
        "Asian, Hispanic",
    "H_NHPI":
        "Native Hawaiian and Pacific Islander, Hispanic",
    "H_OTHER":
        "Other race, Hispanic",
    "H_2MORE":
        "Two or more races, Hispanic",

    "VAP":
        "Total voting age population",
    "HVAP":
        "Voting age population, Hispanic",
    "WVAP":
        "Voting age population, White, non-Hispanic",
    "BVAP":
        "Voting age population, Black, non-Hispanic",
    "AMINVAP":
        "Voting age population, American Indian and Alaska Native, non-Hispanic",
    "ASIANVAP":
        "Voting age population, Asian, non-Hispanic",
    "NHPIVAP":
        "Voting age population, Native Hawaiian and Pacific Islander, non-Hispanic",
    "OTHERVAP":
        "Voting age population, other race, non-Hispanic",
    "2MOREVAP":
        "Voting age population, two or more races, non-Hispanic",

    "CVAP":
        "Total voting age population, citizen",
    "HCVAP":
        "Voting age population, citizen, Hispanic",
    "WCVAP":
        "Voting age population, citizen, White, non-Hispanic",
    "BCVAP":
        "Voting age population, citizen, Black, non-Hispanic",
    "AMINCVAP":
        "Voting age population, citizen, American Indian and Alaska Native, non-Hispanic",
    "ASIANCVAP":
        "Voting age population, citizen, Asian, non-Hispanic",
    "NHPICVAP":
        "Voting age population, citizen, Native Hawaiian and Pacific Islander, non-Hispanic",
    "OTHERCVAP":
        "Voting age population, citizen, other race, non-Hispanic",
    "2MORECVAP":
        "Voting age population, citizen, two or more races, non-Hispanic"
}
