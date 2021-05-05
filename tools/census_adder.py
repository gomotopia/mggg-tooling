
"""
    ~~ tools/census_adder.py ~~
    Written by @InnovativeInventor, April 2021
    Based on code by @jenni-niels
    Commentary by @gomotopia

    Notes
    -----
    Requires...
        typer, for building CLI applications
        geopandas and pandas, for geographic data manipulation
        maup, for aggregating and disaggregating
        os, to access operating system
        us, US and state metadata
        subprocess, for managing multiple processes
        polars, for faster DataFrame manipulation

    Consider https://www.census.gov/programs-surveys/decennial-census/about/voting-rights/cvap.html

        * This digit will change! 
nhgis0003_ds244_20195_2019_blck_grp
nhgis0001_ds244_20195_2019_blck_grp.csv

I downloaded...

1. Detailed Race
   Universe:    Total population
   Source code: C02003
   NHGIS code:  ALUD
 
2. Hispanic or Latino Origin by Race
   Universe:    Total population
   Source code: B03002
   NHGIS code:  ALUK
 
Original code for ALUC, Source B02001, Race
which does not include Hispanic Origin!

Should use B03002, ALUK!

Does 2019 use 2010 or 2020 Block Groups???

"""

import typer
import geopandas as gpd
import maup
import os
import us
import subprocess
import polars as pl
import pandas as pd

"""
Example: python main.py tests/PA_final.shp output.shp PA

Usage: main.py [OPTIONS] FILENAME OUTPUT POSTAL_CODE

  Adds CVAP and ACS data to an arbitrary state-level shapefile

Arguments:
  FILENAME     [required]
  OUTPUT       [required]
  POSTAL_CODE  [required]

Options:
  --overwrite / --no-overwrite    [default: False]
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.

  --help                          Show this message and exit.
"""

import warnings

# Filters extraneous warnings
warnings.filterwarnings(
    "ignore", "GeoSeries.isna", UserWarning
)  # TODO: make PR to maup to silence this


def main(filename: str, output: str, postal_code: str, overwrite: bool = False):
    """
    Adds CVAP and ACS data to an arbitrary state-level shapefile

    Parameters
    ----------
    filename: str

    output: str

    postal_code: str

    overwrite: bool

    Returns
    -------
    geopandas.geoDataFrame
        Of Block groups with appropriate information.

    Raises
    ------
    ValueError
        If nhgis0001 file is not downloaded.


    """

    # Derive state from input zip-code 
    state = us.states.lookup(postal_code)
    CVAPFILE = "CVAP_2015-2019_ACS_csv_files.zip"

    # Ensure there's a census directory, CVAP.zip and extracted contents
    if not os.path.isdir("census"):
        os.makedirs("census")

    if not os.path.isfile(f"census/{CVAPFILE}"):
        subprocess.run(
            f"aria2c https://www2.census.gov/programs-surveys/decennial/rdo/datasets/2019/2019-cvap/{CVAPFILE} -d census",
            shell=True,
        )

    if not os.path.isfile("census/BlockGr.csv"):
        subprocess.run(f"cd census && unzip {CVAPFILE}", shell=True)  # unzip

    # Checks for nhgis0001 file 
    if not os.path.isfile("census/nhgis0001_ds244_20195_2019_blck_grp.csv"):
        # NB: you need to get this file manually
        raise ValueError(
            "You need to manually fetch nhgis0001_ds244_20195_2019_blck_grp.csv from NHGIS"
        )

    # Downloads 2020 State Block Groups zip and extracted 
    state_cvap_shapes = load_state_cvap_shapes(state)
    if not os.path.isfile(f"census/tl_2020_{state.fips}_bg20.zip"):
        subprocess.run(
            f"aria2c https://www2.census.gov/geo/tiger/TIGER2020PL/STATE/{state.fips}_{state.name.upper()}/{state.fips}/tl_2020_{state.fips}_bg20.zip -d census",
            shell=True,
        )
    """
    if not os.path.isfile(f"census/tl_2019_{state.fips}_bg.zip"):
        subprocess.run(
            f"aria2c https://www2.census.gov/geo/tiger/TIGER2019/BG/tl_2019_{state.fips}_bg.zip -d census",
            shell=True,
        )
    if not os.path.isfile(f"census/tl_2019_{state.fips}_bg.shp"):
        subprocess.run(f"cd census && unzip tl_2019_{state.fips}_bg.zip", shell=True)
    """

    if not os.path.isfile(f"census/tl_2020_{state.fips}_bg20.shp"):
        subprocess.run(f"cd census && unzip tl_2020_{state.fips}_bg20.zip", shell=True)

    ##### Data merge and process

    # Reads in state block groups and merges columns with CVAP information
    block_group_shapes = gpd.read_file(f"census/tl_2020_{state.fips}_bg20.shp")
    block_group_with_acs = pd.merge(
        left=block_group_shapes,
        right=state_cvap_shapes,
        left_on="GEOID20",
        right_on="GEOID",
    )
    # Creates or reads old output file and sets crs

    ## Final merge/maupping
    shapefile = gpd.read_file(filename)
    # block_group_with_acs.to_crs(shapefile.crs)
    # shapefile.to_crs(block_group_with_acs.crs)
    # shapefile.to_crs("epsg:4269")
    shapefile.crs = "epsg:4269"  # figure out why this works

    # Take set of acs_blocks columns included in this list
    bgs_to_blocks_cols = list(
        set(
            [
                "HCVAP",
                "HCPOP",
                "HPOP",
                "NHCVAP",
                "NHCPOP",
                "NHPOP",
                "2MORECVAP",
                "2MORECPOP",
                "2MOREPOP",
                "AMINCVAP",
                "AMINCPOP",
                "AMINPOP",
                "ASIANCVAP",
                "ASIANCPOP",
                "ASIANPOP",
                "BCVAP",
                "BCPOP",
                "BPOP",
                "NHPICVAP",
                "NHPICPOP",
                "NHPIPOP",
                "WCVAP",
                "WCPOP",
                "WPOP",
                "CVAP",
                "CPOP",
                "TOTPOP",
            ]
        ).intersection(set(block_group_with_acs.columns))
    )

    # Delete original data
    if overwrite:
        for col in bgs_to_blocks_cols:
            if col in shapefile:
                del shapefile[col]

    cols = set(bgs_to_blocks_cols)
    with maup.progress():
        """Using a progress bar, find pieces in the block group that match those
        in the original shapefile. 
        """
        pieces = maup.intersections(block_group_with_acs, shapefile, area_cutoff=0)
        """ For each set of CVP, CPOP and TOTPOP columns, select the relevant columns,
        Remove from the outstanding list. 
        """
        for unit, suffix in [("CVAP", "CVAP"), ("CPOP", "CPOP"), ("TOTPOP", "POP")]:
            current_cols = {x for x in cols if x.endswith(suffix)}
            cols -= current_cols
            current_cols = list(current_cols)
            """Create weights based off of total within category,
            Then prorate the total back.
            """

            weights = (
                block_group_with_acs[unit]
                .groupby(maup.assign(block_group_with_acs, pieces))
                .sum()
            )
            weights = maup.normalize(weights, level=0)
            shapefile[current_cols] = maup.prorate(
                pieces, block_group_with_acs[current_cols], weights=weights,
            )

    shapefile.to_file(output)


def load_state_cvap_shapes(state):
    """
    Credit: Modified from the original code by JN (https://github.com/jenni-niels)
    """

    # Collect list of CVAP block groups
    state_name = state.name
    cvap_bgs = pl.scan_csv("census/BlockGr.csv")
    state_cvap_bgs = (
        cvap_bgs.filter(pl.lazy.col("geoname").str_contains(state_name))
        .collect()
        .to_pandas()
    )  

    # Replace the column names in NHGIS file 

    race_names = {
        "Total": "TOT",
        "Not Hispanic or Latino": "NH",
        "American Indian or Alaska Native Alone": "NH_AMIN",
        "Asian Alone": "NH_ASIAN",
        "Black or African American Alone": "NH_BLACK",
        "Native Hawaiian or Other Pacific Islander Alone": "NH_NHPI",
        "White Alone": "NH_WHITE",
        "American Indian or Alaska Native and White": "NH_2MORE",
        "Asian and White": "NH_2MORE",
        "Black or African American and White": "NH_2MORE",
        "American Indian or Alaska Native and Black or African American": "NH_2MORE",
        "Remainder of Two or More Race Responses": "NH_2MORE",
        "Hispanic or Latino": "HISP",
    }

    state_cvap_bgs.replace(to_replace=race_names, inplace=True)

    # Sum cit estimate and cvap estimate in each geoid block group
    state_cvap_bgs = (
        state_cvap_bgs.groupby(["geoname", "lntitle", "geoid"])
        .agg(
            {
                "cit_est": "sum",
                "cvap_est": "sum",
                # "tot_est": "sum",
            }
        )
        .reset_index()
    )

    # Pivot table such that new index is geoid
    state_cvap_bgs = state_cvap_bgs.pivot(
        index="geoid",
        columns="lntitle",
        values=["cvap_est", "cit_est"],
    )
    # state_cvap_bgs.rename(columns={"cvap_est": "CVAP", "cit_est": "CPOP", "tot_est": "POP"}, inplace=True)
    state_cvap_bgs.rename(columns={"cvap_est": "CVAP", "cit_est": "CPOP"}, inplace=True)

    # rename state cvap columns such that they have underscores
    state_cvap_bgs.columns = [
        "_".join(col).strip() for col in state_cvap_bgs.columns.values
    ]
    state_cvap_bgs = state_cvap_bgs.rename(columns={"GEOID_": "GEOID"})

    # Rename column names again
    to_rename = {
        "CVAP_HISP": "HCVAP",
        "CPOP_HISP": "HCPOP",
        "POP_HISP": "HPOP",
        "CVAP_NH": "NHCVAP",
        "CPOP_NH": "NHCPOP",
        "POP_NH": "NHPOP",
        "CVAP_NH_2MORE": "2MORECVAP",
        "CPOP_NH_2MORE": "2MORECPOP",
        "POP_NH_2MORE": "2MOREPOP",
        "CVAP_NH_AMIN": "AMINCVAP",
        "CPOP_NH_AMIN": "AMINCPOP",
        "POP_NH_AMIN": "AMINPOP",
        "CVAP_NH_ASIAN": "ASIANCVAP",
        "CPOP_NH_ASIAN": "ASIANCPOP",
        "POP_NH_ASIAN": "ASIANPOP",
        "CVAP_NH_BLACK": "BCVAP",
        "CPOP_NH_BLACK": "BCPOP",
        "POP_NH_BLACK": "BPOP",
        "CVAP_NH_NHPI": "NHPICVAP",
        "CPOP_NH_NHPI": "NHPICPOP",
        "POP_NH_NHPI": "NHPIPOP",
        "CVAP_NH_WHITE": "WCVAP",
        "CPOP_NH_WHITE": "WCPOP",
        "POP_NH_WHITE": "WPOP",
        "CVAP_TOT": "CVAP",
        "CPOP_TOT": "CPOP",
        "POP_TOT": "TOTPOP",
    }

    state_cvap_bgs = state_cvap_bgs.rename(columns=to_rename)
    state_cvap_bgs.reset_index(inplace=True)
    state_cvap_bgs["GEOID"] = state_cvap_bgs["geoid"].apply(lambda x: x[7:])

    # Create pandas DataFrame of Blockgroup Race Data from NHGIS
    race_data = pl.read_csv(
        "census/nhgis0001_ds244_20195_2019_blck_grp.csv",
        use_pyarrow=False,
        encoding="utf8-lossy",
    ).to_pandas()

    ## Clean up and relabel NHGIS race data
    race_nhgis_mappings = {
        "ALUCE001": "TOTPOP",
        "ALUCE002": "WPOP",
        "ALUCE003": "BPOP",
        "ALUCE004": "AMINPOP",
        "ALUCE005": "ASIANPOP",
        "ALUCE006": "NHPIPOP",
        "ALUCE008": "2MOREPOP",
        "ALUCE007": "OTHERPOP"
        # "ALUCE009":
        # "ALUCE010":
    }
    # Use only last part of long GEOID
    race_data["GEOID"] = race_data["GEOID"].apply(lambda x: x[7:])
    race_data = race_data.rename(columns=race_nhgis_mappings)
    # Remove anything else not renamed
    for key in race_data.columns:
        if "ALUC" in key:
            del race_data[key]

    # Mere together cvap blockgroups and race data together using GEOID
    state_all_bgs = pd.merge(
        left=state_cvap_bgs, right=race_data, left_on="GEOID", right_on="GEOID"
    )

    """Take all columns both in state_all_bgs and listed in either
    the nhgis set or the rename_set and ensure they're of numeric datatype"""
    numeric_cols = list(
        set(race_nhgis_mappings.values())
        .union(set(to_rename.values()))
        .intersection(set(state_all_bgs.columns))
    )
    state_all_bgs[numeric_cols] = state_all_bgs[numeric_cols].apply(
        pd.to_numeric, errors="coerce"
    )

    return state_all_bgs


if __name__ == "__main__":
    typer.run(main)
