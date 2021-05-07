"""
    Written by @gomotopia, May 2021, with heavy credit due to
    @InnovativeInventor/MGGG-Tooling for the data processing techniques
    and in turn, @jenni-niels.

    See...
    https://www.census.gov/programs-surveys/
        decennial-census/about/voting-rights/cvap.html

    CVAP data is published in an unusual format.

    Rather than each geographic unit having many columns representing
    totals for Race/Origin, every unit has many rows to achieve the
    same.

    Each Block Group is identified by...
        geoname e.g.
            "Block Group 1, Census Tract 201, Autauga County,..."
        geoid  e.g. "15000US010010201001"

    ... copied over...
        lntitle e.g. "Total","Asian Alone"...
        lnnumber e.g. "1","4"

    ...listing the following data:
        cit_est, The estimates of the number of Citizens
        cit_moe, The margin of error of Citizens
        cvap_est, Estimate of Citzens over 18, the Voting Age
        cvap_moe, Margin of error for Citzens of Voting Age Population.

    Details on the data gymnastics are described in docs/cvap2010.md,
    with full credit to @InnovativeInventor for soving this puzzle.

    Ultimately, a pandas.DataFrame is returned by get_cvap_bgs with
    block group data in MGGG name standard columns indexed by the simple
    GEOID.

"""

import us
import polars as pl
import settings as SET

# CENSUS_URL = "https://www2.census.gov/"
# CVAP_NAME = "CVAP_2015-2019_ACS_csv_files"
# CVAP_URL = "programs-surveys/decennial/rdo/datasets/2019/2019-cvap/"
# CVAP_ZIP_URL = CENSUS_URL + CVAP_URL + CVAP_NAME + ".zip"
# BG_CSV = "BlockGr.csv"
# LOCAL_DATA_FOLDER = "census"


CVAP_RACE_NAMES = {
        "Total": "TOTPOP",
        "Not Hispanic or Latino": "NH", # unused?
        "American Indian or Alaska Native Alone": "NH_AMIN",
        "Asian Alone": "NH_ASIAN",
        "Black or African American Alone": "NH_BLACK",
        "Native Hawaiian or Other Pacific Islander Alone": "NH_NHPI",
        "White Alone": "NH_WHITE",

        # 2 or more is summed together
        "American Indian or Alaska Native and White": "NH_2MORE",
        "Asian and White": "NH_2MORE",
        "Black or African American and White": "NH_2MORE",
        "American Indian or Alaska Native and Black or African American": "NH_2MORE",
        "Remainder of Two or More Race Responses": "NH_2MORE",

        "Hispanic or Latino": "HISP",
    }

    # Demographics are listed in triplicate bewteen CVAP, CPOP
    # and POP. Only CVAP is needed, and must be renamed to follow
    # MGGG naming standards.
RENAME_AGAIN = {
        "POP_TOT": "TOTPOP", # Future check?

        "CVAP_TOTPOP": "CVAP",
        "CVAP_HISP": "HCVAP",
        "CVAP_NH_WHITE": "WCVAP",
        "CVAP_NH_BLACK": "BCVAP",
        "CVAP_NH_AMIN": "AMINCVAP",
        "CVAP_NH_ASIAN": "ASIANCVAP",
        "CVAP_NH_NHPI": "NHPICVAP",
        # OTHER not a category in 2019 CVAP
        "CVAP_NH_2MORE": "2MORECVAP",

        # Not Used
        "CVAP_NH": "NHCVAP",

        "CPOP_HISP": "HCPOP",
        "POP_HISP": "HPOP",
        "CPOP_NH": "NHCPOP",
        "POP_NH": "NHPOP",
        "CPOP_NH_2MORE": "2MORECPOP",
        "POP_NH_2MORE": "2MOREPOP",
        "CPOP_NH_AMIN": "AMINCPOP",
        "POP_NH_AMIN": "AMINPOP",
        "CPOP_NH_ASIAN": "ASIANCPOP",
        "POP_NH_ASIAN": "ASIANPOP",
        "CPOP_NH_BLACK": "BCPOP",
        "POP_NH_BLACK": "BPOP",
        "CPOP_NH_NHPI": "NHPICPOP",
        "POP_NH_NHPI": "NHPIPOP",
        "CPOP_NH_WHITE": "WCPOP",
        "POP_NH_WHITE": "WPOP",
        "CPOP_TOT": "CPOP",
    }

# # def check_cvap_data():
# if not os.path.isfile(f"../{LOCAL_DATA_FOLDER}/{BG_CSV}"):
#     print("Here1")
#     if not os.path.isfile(f"../{LOCAL_DATA_FOLDER}/{CVAP_FOLDER}/{CVAP_ZIP}"):
#         subprocess.run(
#             f"aria2c {CVAP_ZIP_URL} -d census",
#             shell=True,
#         )
#     else:
#         subprocess.run(f"cd census && unzip {CVAPFILE}") #, shell=True)  # unzip

def get_cvap_bgs(state_abbrev: str):
    """
        Doc String
    """
    # Check if the data is there.

    state = us.states.lookup(state_abbrev)
    cvap_bgs_pl = pl.scan_csv(f"{SET.LOCAL_DATA_FOLDER}/"+
                              f"{SET.CVAP_NAME}/BlockGr.csv")
    state_cvap_bgs = (
        cvap_bgs_pl.filter(pl.lazy.col("geoname").str_contains(state.name))
        .collect()
        .to_pandas()
    )

    state_cvap_bgs.replace(to_replace=CVAP_RACE_NAMES, inplace=True)
    # Sum cit estimate and cvap estimate in each geoid block group
    state_cvap_bgs = (
        state_cvap_bgs.groupby(["geoname", "lntitle", "geoid"])
        .agg({"cit_est": "sum","cvap_est": "sum"})
        .reset_index()
    )

    # Pivot table such that new index is geoid
    state_cvap_bgs = state_cvap_bgs.pivot(
        index="geoid",
        columns="lntitle",
        values=["cvap_est", "cit_est"],
    )

    # Reset index to make geoid a column
    state_cvap_bgs = state_cvap_bgs.reset_index()

    state_cvap_bgs.rename(columns={"cvap_est": "CVAP", "cit_est": "CPOP"},
                                    inplace=True)

    # CPOP columns measure Total Citizens.
    # We only want Total Citizens over 18: CVAP
    # state_cvap_bgs.drop(columns=['CPOP'])
    state_cvap_bgs = state_cvap_bgs.drop('CPOP', axis=1, level=0)

    # Demographics are listed in triplicate bewteen CVAP, CPOP
    # and POP. This is how we separate them out into columns.
    state_cvap_bgs.columns = [
        "_".join(col).strip() for col in state_cvap_bgs.columns.values
    ]

    state_cvap_bgs = state_cvap_bgs.drop("CVAP_NH", axis=1)

    # Clean up to conform to MGGG Naming Standards
    state_cvap_bgs = state_cvap_bgs.rename(columns={"geoid_": "GEOID"})

    state_cvap_bgs["GEOID"] = state_cvap_bgs["GEOID"].apply(lambda x: x[7:])
    state_cvap_bgs = state_cvap_bgs.rename(columns=RENAME_AGAIN)
    state_cvap_bgs.reset_index(inplace=True)

    return state_cvap_bgs
