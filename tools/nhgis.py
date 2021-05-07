"""
    Written by @gomotopia, May 2021, with heavy credit due to
    @InnovativeInventor/MGGG-Tooling for the data processing techniques
    and in turn @jenni-niels.

    The National Historical Geographic Information System seeks to
    simpify the collection of Census data. NHGIS data is easy to find,
    but is not available by API and must be downloaded. Furthermore,
    this download requires an account and a pledge not to distribute the
    information.

    For the 2019 ACS, MGGG uses B03002, "Hispanic or Latino Origin by
    Race" to populate information for the Districtr App. The filename
    for downloads from NHGIS, follow a pattern.

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

    Within the NHGIS folder, the data is a csv and comes with useful
    metadata. For NHGIS, estimates from table B30002 are prefixed with
    ALUKE.

    Ultimately, a pandas.DataFrame is returned by get_nhgis_race_bgs
    carrying data in MGGG name standard columns indexed by the simple
    GEOID.

    !!! Import and set the settings.get_race with this module's function
    if you're using NHGIS data! Other people use modules written to take
    data directly from the Census API.

"""
# import os
import us
import polars as pl # Polars reads csv's faster than pandas!

import settings as SET

# LOCAL_DATA_FOLDER = "census"
# NHGIS_PREFIX = "nhgis0004"
# NHGIS_DATA_NAME = "_ds244_20195_2019_blck_grp"

## Clean up and relabel NHGIS race data
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

# # def check_nhgis_data():
#     """
#         Doc string
#     """
#     # Checks for nhgis0001 file
#         if not os.path.isfile("census/nhgis0001_ds244_20195_2019_blck_grp.csv"):
#     # NB: you need to get this file manually
#         raise ValueError(
#             "You need to manually fetch nhgis0001_ds244_20195_2019_blck_grp.csv from NHGIS"
#     )

def get_nhgis_race_bgs(state_abbrev: str):
    """
        Doc string
    """
    state = us.states.lookup(state_abbrev)

    # check_nhgis_data()

    # Create pandas DataFrame of Blockgroup Race Data from NHGIS
    nhgis_bgs_pl = pl.scan_csv(
        f"{SET.LOCAL_DATA_FOLDER}/" +
        f"{SET.NHGIS_PREFIX}_csv/" +
        f"{SET.NHGIS_PREFIX}{SET.NHGIS_DATA_NAME}.csv"
    )

    # Filter for specific state
    state_nhgis_bgs = (
        nhgis_bgs_pl.filter(pl.lazy.col("STATE").str_contains(state.name))
        .collect()
        .to_pandas()
    )

    # Use only last part of long GEOID, rename columns
    state_nhgis_bgs["GEOID"] = state_nhgis_bgs["GEOID"].apply(lambda x: x[7:])
    state_nhgis_bgs = state_nhgis_bgs.rename(columns=NHGIS_RACE_NAMES)

    #Keep only GEOID and named columns
    state_nhgis_bgs = (state_nhgis_bgs[ ["GEOID"]
        + list(NHGIS_RACE_NAMES.values())])

    return state_nhgis_bgs
