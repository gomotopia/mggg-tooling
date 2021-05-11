"""
For now, this module create a shapefile for a given state based on
2019 ACS CVAP and Race/Origin data.

The Census Adder is a transitional module that bridges the original
@/InnovativeInventor mggg-tools with this current version. The original
version was convieved as a Command Line Application that combined all
functions of checking and downloading data, processing data and even
maup-style proration of CVAP and ACS data on extant shapefiles of
smaller units.

We retain the ability to create a shapefile for a given state based on
2019 ACS CVAP and Race/Origin data. This rests upon the ability to merge
separate CVAP and Race/Origin dataframes, provided that they conform to
MGGG naming standards.

We've attempted to retain some CLI functionality, but leave advanced
data merging and mauping on older files for a later time. The original
CLI description from @InnovativeInventor/MGGG-tooling is as follows.

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

Notes
-----
Written by @InnovativeInventor, April 2021 based very much on original
code by JN, @jenni-niels.
New fork by @gomotopia, May 2021

Requires...
    typer, for building CLI applications
    geopandas and pandas, for geographic data manipulation
    maup, for aggregating and disaggregating
    os, to access operating system
    us, US and state metadata
    subprocess, for managing multiple processes
    polars, for faster DataFrame manipulation

Examples
--------
We can return a geopandas DataFrame of merged CVAP and Race/Origin
data over all Block Groups in a given state.

    hi_race_cvap_gdf = make_race_cvap("HI").

We can use geopandas own shapefile function to save the information.

    make_race_cvap_gdf.to_file("hi_race_cvap.shp")

We can take two pandas dataframes with mggg-standardized columns of
ACS Race/Origin and CVAP data and generate a new DataFrame. The pair are
inner-joined on short GEOID.

    from settings import get_race_origin
    from cvap2019 import get_cvap_bgs
    cvap_bgs = get_cvap_bgs("HI")
    race_origin_bgs = get_race_origin_bgs("HI")
    race_cvap_bgs = race_cvap_merge(race_origin_bgs, cvap_bgs)

We have no mauping abilities and overwriting of files as of yet. We can
generate new state shapefiles of block groups based on 2019 TIGER files
with preloaded data from the 2019 5Y 2019 ACS and CVAP.

"""

import os
import warnings

# import geopandas as gpd
import us
# import subprocess
# import polars as pl
import pandas as pd

# To make work in project or editor namespace
try: import settings as SET
except: import tools.settings as SET

try: from cvap2019 import get_cvap_bgs
except: from tools.cvap2019 import get_cvap_bgs

try: from tiger import get_tiger_bgs
except: from tools.tiger import get_tiger_bgs

# Import your favorite ACS algorithm here
try: from acs_plugin_loader import set_race_origin_bgs
except: from tools.acs_plugin_loader import set_race_origin_bgs

get_race_origin_bgs = set_race_origin_bgs(SET.ACS_PLUGIN)


"""
try: from nhgis import get_nhgis_race_bgs as get_race_origin_bgs
except: from tools.nhgis import get_nhgis_race_bgs as get_race_origin_bgs
"""



# Filters extraneous warnings
warnings.filterwarnings(
    "ignore", "GeoSeries.isna", UserWarning
)  # TODO: make PR to maup to silence this

def race_cvap_merge(race_data, cvap_data):
    """
    Conducts inner join of mggg-standardized race and cvap data.

    We can take two pandas dataframes with mggg-standardized columns of
    ACS Race/Origin and CVAP data and generate a new DataFrame. The pair
    are inner-joined on short GEOID. With credit to @InnovativeInventor
    and @jenni-niels.

    Parameters
    ----------

    filename: str
        The filename of a Shapefile that carries older data that we use
        to prorate.
    output: str
        The filename for a new Shapefile created to store the results of
        the merge operations.
    postal_code: str
        Used to indicate relevant shape.
    overwrite: str
        Toggles whether data in the original filename is replaced by new
        data. The default is not to overwrite.

    Returns
    -------
        Null

    Raises
    ------

    """

    # Merge together cvap blockgroups and race data together using GEOID
    race_cvap_data = pd.merge(
        left=cvap_data,
        right=race_data,
        left_on="GEOID",
        right_on="GEOID"
    )

    # Ensure numeric columns
    numeric_cols = list(
        set(race_cvap_data.columns)
        .intersection(set(SET.NAME_CONVENTION.keys()))
    )
    race_cvap_data[numeric_cols] = race_cvap_data[numeric_cols].apply(
        pd.to_numeric, errors="coerce"
    )

    # Remove extraneous index column if necessary
    try:
        race_cvap_data = race_cvap_data.drop(columns='index')
    except:
        pass

    return race_cvap_data

def make_race_cvap_gdf(state_abbr: str, download_allowed: bool = False):
    """
    Returns geoDataFrame of Block Groups in target State with CVAP and
    ACS Race information formatted to mggg-standards

    Parameters
    ----------
    state_abbr: str
        Two-letter state abbreviation of target state.

    download_allowed : bool
        Flag as to whether to download missing data or raise error.
        Set to avoid downloading by default.

    Returns
    -------
    geopandas.geoDataFrame
        GeoDataFrame of Block Groups in target State with CVAP and ACS
        Race information formatted to mggg-standards

    Raises
    ------
    ValueError
        State abbreviation must be valid.
    """
    geo_race_cvap_bgs = ""
    try:
        state = us.states.lookup(state_abbr)
    except ValueError:
        print("Must be a state or territory postal code")
        raise
    else:
        # Ensure that local Data Folder exists.
        if not os.path.isdir(f"../{SET.LOCAL_DATA_FOLDER}"):
            os.makedirs(f"../{SET.LOCAL_DATA_FOLDER}")

        # These variables are simple pandas.DataFrames
        cvap_bgs = get_cvap_bgs(state_abbr)
        race_origin_bgs = get_race_origin_bgs(state_abbr)
        race_cvap_bgs = race_cvap_merge(race_origin_bgs, cvap_bgs)

        # These follwing variables are geopandas.DataFrames
        tiger_bgs = get_tiger_bgs(state_abbr, download_allowed)
        geo_race_cvap_bgs = tiger_bgs.merge(
            race_cvap_bgs,
            on="GEOID",
            how="left"
        )
    return geo_race_cvap_bgs

def make_race_cvap_shp(state_abbr: str, output = "", \
                                        download_allowed: bool = False):
    """
    Creates Shapefile of Block Groups in target State with CVAP and ACS
    Race information formatted to mggg-standards as well

    Parameters
    ----------
    state_abbr: str
        Two-letter state abbreviation of target state.

    output: str
        Desire shapefile path and name for output.  
        Default, set in settings with State abbr prefix.

    download_allowed : bool
        Flag as to whether to download missing data or raise error.
        Set to avoid downloading by default.
        
    Returns
    -------
    Null

    Raises
    ------

    """
    actual_output = ""
    if output:
        actual_output = output
    else:
        # Ensure Output Folder
        if not os.path.isdir(SET.DEFAULT_OUPUT_FOLDER):
            os.makedirs(SET.DEFAULT_OUPUT_FOLDER)
        # State Folder for Output
        state_folder = SET.DEFAULT_OUPUT_FOLDER + \
                       f"{state_abbr}_{SET.DEFAULT_OUTPUT}/"

        if not os.path.isdir(state_folder):
            os.makedirs(state_folder)

        actual_output = state_folder + \
                                     f"{state_abbr}_{SET.DEFAULT_OUTPUT}.shp"
                                     
    make_race_cvap_gdf(state_abbr, download_allowed).to_file(actual_output)
    return

### Functions for Command Line Application ###
import typer

def main(filename: str, output: str, \
                    postal_code: str, overwrite: bool = False):
    """
    To ensure some compatibility, we retain the original CLI inputs from
    original MGGG-tooling repository.

    In the future, we will aim for complete backwards compatibility by
    including the overwriting and mauping functionality of the original
    CLI.

    Parameters
    ----------

    filename: str
        The filename of a Shapefile that carries older data that we use
        to prorate.
    output: str
        The filename for a new Shapefile created to store the results of
        the merge operations.
    postal_code: str
        Used to indicate relevant shape.
    overwrite: str
        Toggles whether data in the original filename is replaced by new
        data. The default is not to overwrite.

    Returns
    -------
        Null
    Raises
    ------

    """
    state = us.states.lookup(postal_code)
    new_race_cvap_bgs = make_race_cvap_gdf(state.abbriation, \
                                        download_allowed = True)

    ### !!! No maup-ing abilities right now
    ### Please see @InnovativeInventor/mggg-tooling/census_adder.py

    # return read_and_maup_old_file(filename, new_race_cvap_bgs):
    print (f"{filename} is ignored in this version of the CLI application.")
    new_race_cvap_bgs.to_file(output)

if __name__ == "__main__":
    typer.run(main)
