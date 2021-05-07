"""
Doc String
"""

import nhgis

OUTPUT_FILE = "output.shp"

CENSUS_URL = "https://www2.census.gov/"
CVAP_NAME = "CVAP_2015-2019_ACS_csv_files"
CVAP_URL = "programs-surveys/decennial/rdo/datasets/2019/2019-cvap/"
CVAP_ZIP_URL = CENSUS_URL + CVAP_URL + CVAP_NAME + ".zip"
BG_CSV = "BlockGr.csv"
LOCAL_DATA_FOLDER = "census"

NHGIS_PREFIX = "nhgis0004"
NHGIS_DATA_NAME = "_ds244_20195_2019_blck_grp"

LOCAL_DATA_FOLDER = "../census"
TIGER_PREFIX = "tl_2019_"
BG_POSTFIX = "_bg"


get_race_bgs = nhgis.get_nhgis_race_bgs

# unit = BlockGroups?

# mggg-states-qa/src/naming_convention.json
# my_dict2 = {y:x for x,y in my_dict.iteritems()}

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
