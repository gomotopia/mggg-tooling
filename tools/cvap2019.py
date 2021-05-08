"""
Released in February, 2021, CVAP data based on the 2019 ACS is
reported in an unusual format. These functions can read this unusual
release and report CVAP information fo each block group as a pandas
dataframe.

Examples
--------
There are two stand alone functions contained within this module.

    First, check_download_tiger_file checks the CVAP information
    found on the Census website. For now, this function will rely
    that you can download this information manually from
    https://www.census.gov/programs-surveys/
                        decennial-census/about/voting-rights/cvap.html
    and place it in the location you've specified in the settings.

    Second, get_cvap_bgs relies on incredible data gymnastics to
    read and report the data. Ultimately, a pandas.DataFrame is returned
    by get_cvap_bgs with block group data in MGGG name standard columns
    listed with simple GEOID, i.e. shorter ones that start with
    STATEFIPS and not geographic level like they do in this file. We
    need the only the numbers after the 'US' in longer GEOIDs.

    cvap_bgs = ""
    try:
        cvap_bgs = def get_cvap_bgs("HI")
    except:
        print("We cannot produced CVAP data for Hawaii")

    Many thanks to @InnovativeInventor and @jenni-niels for the insight.

Notes
-----
Refactored by @gomotopia, May 2021, in debt to the original MGGG-Tooling
by @InnovativeInventor's with heavy credit due to @jenni-niels for the
data processing techniques.

So unusual! Rather than each geographic unit having many columns
representing totals for each Race/Origin, every unit has many rows to
achieve the same. Thus, one Block Group may have many rows, rather than
just one in regular ACS data.

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

Details on the data gymnastics will be described in ../cvap_docs.md,
with due credit to the creators above for solving the puzzle.

"""
import os
import us
import polars as pl
# To make work in project or editor namespace
try: import settings as SET
except: import tools.settings as SET


# A dictionary that converts CVAP lntitle to MGGG-standard names
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

def check_download_cvap19_data():
    """
    Checks if the CVAP 2019 csv file exists in the location specified by
    the settings. If none found, an exception is raised.

    In the future, we'll have the code will have the ability to donwload
    this directly to your local machine.

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
    if os.path.isfile(SET.LOCAL_CVAP_CSV):
        file_exists = True
    else:
        # NB: you need to get this file manually
        raise ValueError("No CVAP file found. " + \
                                            "Please fetch CVAP data manually.")
    return SET.LOCAL_CVAP_CSV if file_exists else ""

def get_cvap_bgs(state_abbr: str):
    """
    This returns a pandas DataFrame of the Citizens of Voting Age
    Population in each Block Group of the specified state.

    This is extracted from Census CVAP data based on the 2019 5Y ACS.
    A pandas data frame is returned with columns following MGGG naming
    standards.

    Those interested in learning more about the pandas functions used
    are invited to visit docs/cvap2010.md.

    Notes
    -----
    No Exceptions are thrown in case the csv reader has any problems.
    Does not verify that this csv file has the proper structure and
    headings of an CVAP file.

    Parameters
    ----------
    state_abbr: str
        Two-letter state abbriation of target state.

    Returns
    -------
    pandas.dataFrame or null
        dataFrame of state BGs CVAP data from the Census 2019 5Y ACS
        CVAP in mggg-standard columns.

    """
    state = us.states.lookup(state_abbr)
    state_cvap_bgs = ""

    if check_download_cvap19_data():
        cvap_bgs_pl = pl.scan_csv(SET.LOCAL_CVAP_CSV)
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
