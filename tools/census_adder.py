
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

import settings as SET

from cvap2019 import get_cvap_bgs
from tiger import get_tiger_bgs

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

def race_cvap_merge(race_data, cvap_data):
    """
    Credit: Modified from the original code by JN (https://github.com/jenni-niels)
    """
    
    # Mere together cvap blockgroups and race data together using GEOID
    race_cvap_data = pd.merge(
        left=cvap_data, right=race_data, left_on="GEOID", right_on="GEOID"
    )

    # Ensure numeric columns
    numeric_cols = list(
        set(race_cvap_data.columns)
        .intersection(set(SET.NAME_CONVENTION.keys()))
    )
    race_cvap_data[numeric_cols] = race_cvap_data[numeric_cols].apply(
        pd.to_numeric, errors="coerce"
    )

    return race_cvap_data

def read_and_maup_old_file():
    """
        Doc String
    """
    # """
    # ## Final merge/maupping
    # shapefile = gpd.read_file(filename)
    # # block_group_with_acs.to_crs(shapefile.crs)
    # # shapefile.to_crs(block_group_with_acs.crs)
    # # shapefile.to_crs("epsg:4269")
    # shapefile.crs = "epsg:4269"  # figure out why this works

    # # Take set of acs_blocks columns included in this list
    # bgs_to_blocks_cols = list(
    #     set(
    #         [
    #             "HCVAP",
    #             "HCPOP",
    #             "HPOP",
    #             "NHCVAP",
    #             "NHCPOP",
    #             "NHPOP",
    #             "2MORECVAP",
    #             "2MORECPOP",
    #             "2MOREPOP",
    #             "AMINCVAP",
    #             "AMINCPOP",
    #             "AMINPOP",
    #             "ASIANCVAP",
    #             "ASIANCPOP",
    #             "ASIANPOP",
    #             "BCVAP",
    #             "BCPOP",
    #             "BPOP",
    #             "NHPICVAP",
    #             "NHPICPOP",
    #             "NHPIPOP",
    #             "WCVAP",
    #             "WCPOP",
    #             "WPOP",
    #             "CVAP",
    #             "CPOP",
    #             "TOTPOP",
    #         ]
    #     ).intersection(set(block_group_with_acs.columns))
    # )
    # """

    # # Delete original data if Overwrite
    # if overwrite:
    #     for col in bgs_to_blocks_cols:
    #         if col in shapefile:
    #             del shapefile[col]

    # save
    # cols = set(bgs_to_blocks_cols)
    # with maup.progress():
    #     """Using a progress bar, find pieces in the block group that match those
    #     in the original shapefile. 
    #    """"""
    #     pieces = maup.intersections(block_group_with_acs, shapefile, area_cutoff=0)
    #     """""" For each set of CVP, CPOP and TOTPOP columns, select the relevant columns,
    #     Remove from the outstanding list. 
    #     """"""
    #     for unit, suffix in [("CVAP", "CVAP"), ("CPOP", "CPOP"), ("TOTPOP", "POP")]:
    #         current_cols = {x for x in cols if x.endswith(suffix)}
    #         cols -= current_cols
    #         current_cols = list(current_cols)
    #         """"""Create weights based off of total within category,
    #         Then prorate the total back.
    #         """"""

    #         weights = (
    #             block_group_with_acs[unit]
    #             .groupby(maup.assign(block_group_with_acs, pieces))
    #             .sum()
    #         )
    #         weights = maup.normalize(weights, level=0)
    #         shapefile[current_cols] = maup.prorate(
    #             pieces, block_group_with_acs[current_cols], weights=weights,
    #         )
    #         """
            
# def make_race_cvap_shp(filename: str, output: str, postal_code: str, overwrite: bool = False):
def make_race_cvap_shp(state_abbrev: str):
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

    # Load Settings

    state = us.states.lookup(state_abbrev)
    # try:
    #     state = us.states.lookup(state_abbrev)
    # except: 
    #     ValueError ("Must be a state or territory postal code")
    
    # Ensure that local Data Folder exists.
    if not os.path.isdir(f"../{SET.LOCAL_DATA_FOLDER}"):
        os.makedirs(f"../{SET.LOCAL_DATA_FOLDER}")

    # These variables are simple pandas.DataFrames
    cvap_bgs = get_cvap_bgs(state_abbrev)
    race_bgs = SET.get_race_bgs(state_abbrev)
    race_cvap_bgs = race_cvap_merge(race_bgs, cvap_bgs)

    # These follwing variables are geopandas.DataFrames 
    tiger_bgs = get_tiger_bgs(state_abbrev)
    geo_race_cvap_bgs = tiger_bgs.merge(
        race_cvap_bgs,
        on="GEOID",
        how="left"
    )
    geo_race_cvap_bgs.to_file("../census/HI_Test/HAWAII.shp")

def main(filename: str, output: str, postal_code: str, overwrite: bool = False):
    make_race_cvap_shp(filename, output, postal_code, overwrite)

if __name__ == "__main__":
    typer.run(main)

    """
Test enviornment... 

import os; os.chdir('tools'); from cvap2019 import *; from nhgis import *; from tiger import *; import settings as SET
import pandas as pd; import numpy as np; import geopandas as gpd; import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon

import os; os.chdir('tools'); from census_adder import *
    """