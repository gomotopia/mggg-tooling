"""
Generating CVAP and ACS tigerfiles requires three sets of data, which
are both found remotely and stored locally. The settings for these
locations are listed here.

Refactored by @gomotopia, May 2021, in debt to the original MGGG-Tooling
by @InnovativeInventor's with heavy credit due to @jenni-niels for the
data processing techniques.

The default file structure is as follows...

mggg-tools/
├── tools/
│   ├── settings.py
│   ├── tiger.py
│   ├── nhgis.py
│   ├── cvap2019.py
│   └── census_adder.py
├── data/
│   ├── CVAP5Y2019/
│   |   ├── CVAP5Y2019/
│   |   |   ├──CVAP_2015-2019_ACS_csv_files
│   |   |   |   ├── BlockGr.csv
│   |   |   |   └── ...
│   ├── nhgis0004_csv/
│   |   ├── nhgis0004_ds244_20195_2019_blck_grp.csv
│   |   └── ...
│   ├── Tiger19_bgs/
│   |   ├── tl_2019_01_bg
│   |   |   ├── tl_2019_01_bg.shp
|   |   |   └── ...
│   |   ├── tl_2019_01_bg.zip
│   |   └── ...
│   ├── cvap_acs-output/
|   |   ├── AL_cvap_acs/
|   |   |   ├── AL_cvap_acs.shp
│   |   |   └── ...
│   |   └── ...
|   └── ...
└── ...
"""

##### Local Settings #####

OUTPUT_FILE = "output.shp"
LOCAL_DATA_FOLDER = "./data/"
DEFAULT_OUPUT_FOLDER = LOCAL_DATA_FOLDER + "cvap_acs_output/"
DEFAULT_OUTPUT = "cvap_acs"

##### Census CVAP Data, 2015-2019 Estimates, Released Feb. 2021 #####

# Settings for 2019 Census CVAP Data
# See... https://www.census.gov/programs-surveys/decennial-census/
#                   about/voting-rights/cvap.html
# mggg-tools/
# ├── data/
# │   ├── CVAP5Y2019/
# │   |   ├── CVAP5Y2019/
# │   |   |   └──CVAP_2015-2019_ACS_csv_files
# │   |   |       ├── BlockGr.csv
# │   |   |       └── ...
# │   |   └── ...
# |   └── ...
# └── ...

CENSUS_URL = "https://www2.census.gov/"
CVAP_NAME = "CVAP_2015-2019_ACS_csv_files"
CVAP_FOLDER = "CVAP5Y2019/"

CVAP_URL = "programs-surveys/decennial/rdo/datasets/2019/2019-cvap/"
CVAP_ZIP_URL = CENSUS_URL + CVAP_URL + CVAP_NAME + ".zip"
BG_CSV = "BlockGr.csv"
LOCAL_CVAP_FOLDER = "CVAP"

# e.g. data/CVAP/CVAP_2015-2019_ACS_csv_files/BlockGr.csv
LOCAL_CVAP_CSV = LOCAL_DATA_FOLDER + CVAP_FOLDER + CVAP_NAME + "/" + BG_CSV

##### Census Tiger Data, from 2019 #####

# 2019 Block Group shapefiles. Use 2019 data for 2019 ACS and CVAP data.
# e.g. https://www2.census.gov/geo/tiger/TIGER2019/BG/tl_2019_19_bg.zip
#
# mggg-tools/
# ├── data/
# │   ├── Tiger19_bgs/
# │   |   ├── tl_2019_01_bg
# │   |   |   ├── tl_2019_01_bg.shp
# |   |   |   └── ...
# │   |   ├── tl_2019_01_bg.zip
# │   |   └── ...
# |   └── ...
# └── ...

LOCAL_TIGER_FOLDER = LOCAL_DATA_FOLDER + "Tiger19_bgs/"

TIGER_URL = CENSUS_URL + "geo/tiger/"
# Specific to year and block group geography
TIGER_BG_URL = TIGER_URL + "TIGER2019/BG/"
TIGER_PREFIX = "tl_2019_"
BG_POSTFIX = "_bg"


##### Census ACS Data on Race and Origin, 2019 5-Y Estimates #####

"""
There are different ways to collect ACS data. Import and select your
preferred function when using get_race_bgs. The function is specified
as follows and is currently used in census_adder.py

def get_race_bgs(state_abbr: str)
    '''
    Returns 2019 ACS 5Y Race data from Census Table B03002 for the
    block groups of a selected state.

    Parameters
    ----------
    state_abbr: str
        Two digit state FIPS state or territory code.

    Returns
    -------
    pandas.DataFrame
        Containing GEOID, short ID, i.e. State, County, Tract... codes
        without 15000US geo. level and nation prfeix, and demographic
        columns using MGGG naming standards listed below.
    '''

For now, we use NHGIS data to get race ACS data. So in census_adder.py
we...

# Import your favorite ACS algorithm here
from nhgis import get_nhgis_race_bgs as get_race_origin_bgs

"""

# Currently NHGIS or CensusAPI
ACS_PLUGIN = "CensusAPI"

# Settings for using NHGIS Data for ACS. Must be downloaded manually
# from https://www.nhgis.org/. Select from table Census B03002, Hispanic
# or Latino Origin by Race, (NHGIS Code ALUK) for 2019 5Y ACS.

# mggg-tools/
# ├── data/
# │   ├── nhgis0004_csv/
# │   |   ├── nhgis0004_ds244_20195_2019_blck_grp.csv
# │   |   └── ...
# |   └── ...
# └── ...

# Watch here! NHGIS_PREFIX may differ for each user.
NHGIS_PREFIX = "nhgis0004"
NHGIS_DATA_NAME = "_ds244_20195_2019_blck_grp"

# Presumes that NHGIS zip data is extracted into a folder of its own
# name. e.g. /data/nhgis0004_csv/nhgis0004_ds244_20195_2019_blck_grp.csv
# For more information, see nhgis.py docs.
LOCAL_NHGIS_CSV = LOCAL_DATA_FOLDER + NHGIS_PREFIX + "_csv/" + \
                  NHGIS_PREFIX + NHGIS_DATA_NAME + ".csv"

# Settings for using downloading B03002 columns, Hispanic or Latino
# Origin by Race data from the Census API directly.
#
# mggg-tools/
# ├── data/
# │   ├── ACS5Y2019Race/
# |   |   ├── AL_race_origin_bg.csv
# │   |   └── ...

CENSUS2019_API_URL = "https://api.census.gov/data/2019/acs/acs5"

LOCAL_CENSUS_FOLDER = LOCAL_DATA_FOLDER + "ACS5Y2019Race/"
LOCAL_CENSUS_SUFFIX = "_race_origin_bg"
CENSUS_BATCH_SIZE = 50

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
