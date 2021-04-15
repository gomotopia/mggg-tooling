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

import warnings; warnings.filterwarnings('ignore', 'GeoSeries.isna', UserWarning) # TODO: make PR to maup to silence this

def main(filename: str, output: str, postal_code: str, overwrite: bool = False):
    """
    Adds CVAP and ACS data to an arbitrary state-level shapefile
    """

    ## Data fetch
    state = us.states.lookup(postal_code)
    CVAPFILE = "CVAP_2015-2019_ACS_csv_files.zip"
    if not os.path.isdir("census"):
        os.makedirs("census")

    if not os.path.isfile(f"census/{CVAPFILE}"):
        subprocess.run(f"aria2c https://www2.census.gov/programs-surveys/decennial/rdo/datasets/2019/2019-cvap/{CVAPFILE} -d census", shell=True)

    if not os.path.isfile("census/BlockGr.csv"):
        subprocess.run(f"cd census && unzip {CVAPFILE}", shell=True) # unzip

    if not os.path.isfile("census/nhgis0001_ds244_20195_2019_blck_grp.csv"):
        # NB: you need to get this file manually
        raise ValueError("You need to manually fetch nhgis0001_ds244_20195_2019_blck_grp.csv from NHGIS")

    state_cvap_shapes = load_state_cvap_shapes(state)
    if not os.path.isfile(f"census/tl_2019_{state.fips}_bg.zip"):
        subprocess.run(f"aria2c https://www2.census.gov/geo/tiger/TIGER2019/BG/tl_2019_{state.fips}_bg.zip -d census", shell=True)

    if not os.path.isfile(f"census/tl_2019_{state.fips}_bg.shp"):
        subprocess.run(f"cd census && unzip tl_2019_{state.fips}_bg.zip", shell=True)

    ## Data merge and process
    block_group_shapes = gpd.read_file(
        f"census/tl_2019_{state.fips}_bg.shp"
    )
    # print(block_group_shapes.columns)
    block_group_with_acs = pd.merge(
        left=block_group_shapes,
        right=state_cvap_shapes,
        left_on="GEOID",
        right_on="GEOID",
    )

    ## Final merge/maupping
    shapefile = gpd.read_file(filename)
    # block_group_with_acs.to_crs(shapefile.crs)
    # shapefile.to_crs(block_group_with_acs.crs)
    # shapefile.to_crs("epsg:4269")
    shapefile.crs = "epsg:4269" # figure out why this works

    bgs_to_blocks_cols = list(set(['HCVAP', 'HCPOP', 'HPOP','NHCVAP', 'NHCPOP', 'NHPOP','2MORECVAP', '2MORECPOP', '2MOREPOP', 'AMINCVAP', 'AMINCPOP', 'AMINPOP', 'ASIANCVAP', 'ASIANCPOP', 'ASIANPOP', 'BCVAP', 'BCPOP', 'BPOP', 'NHPICVAP', 'NHPICPOP', 'NHPIPOP','WCVAP', 'WCPOP', 'WPOP','CVAP', 'CPOP', 'TOTPOP']).intersection(set(block_group_with_acs.columns)))
    if overwrite:
        for col in bgs_to_blocks_cols:
            if col in shapefile:
                del shapefile[col]

    print("64", block_group_with_acs)
    print("65", shapefile)
    with maup.progress():
        pieces = maup.intersections(
            block_group_with_acs, shapefile, area_cutoff=0
        )
        weights = (
            block_group_with_acs["TOTPOP"]
            .groupby(maup.assign(block_group_with_acs, pieces))
            .sum()
        )
        weights = maup.normalize(weights, level=0)
        shapefile[bgs_to_blocks_cols] = maup.prorate(
            pieces,
            block_group_with_acs[bgs_to_blocks_cols],
            weights=weights,
        )

    print("82", shapefile.columns) # debug
    print("83", shapefile) # debug
    shapefile.to_file(output)


def load_state_cvap_shapes(state):
    """
    From JN
    """
    state_name = state.name
    cvap_bgs = pl.scan_csv("census/BlockGr.csv")
    state_cvap_bgs = cvap_bgs.filter(pl.lazy.col("geoname").str_contains(state_name)).collect().to_pandas() # filtering for state
    race_names = {
        "Total": "TOT",
        "Not Hispanic or Latino": "NH",
        "American Indian or Alaska Native Alone": "NH_AMIN", "Asian Alone": "NH_ASIAN",
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
    state_cvap_bgs = state_cvap_bgs.pivot(
        # index="geoid", columns="lntitle", values=["cvap_est", "cit_est", "tot_est"]
        index="geoid", columns="lntitle", values=["cvap_est", "cit_est"]
    )
    # state_cvap_bgs.rename(columns={"cvap_est": "CVAP", "cit_est": "CPOP", "tot_est": "POP"}, inplace=True)
    state_cvap_bgs.rename(columns={"cvap_est": "CVAP", "cit_est": "CPOP"}, inplace=True)

    state_cvap_bgs.columns = [
        "_".join(col).strip() for col in state_cvap_bgs.columns.values
    ]
    state_cvap_bgs = state_cvap_bgs.rename(columns={"GEOID_": "GEOID"})

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

    race_data = pl.read_csv("census/nhgis0001_ds244_20195_2019_blck_grp.csv", use_pyarrow=False, encoding="utf8-lossy").to_pandas()

    ## Clean up and relabel race data
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
    race_data["GEOID"] = race_data["GEOID"].apply(lambda x: x[7:])
    race_data = race_data.rename(columns=race_nhgis_mappings)
    for key in race_data.columns:
        if "ALUC" in key:
            del race_data[key]

    state_all_bgs = pd.merge(left=state_cvap_bgs, right=race_data, left_on="GEOID", right_on="GEOID")
    numeric_cols = list(set(race_nhgis_mappings.values()).union(set(to_rename.values())).intersection(set(state_all_bgs.columns)))
    state_all_bgs[numeric_cols] = state_all_bgs[numeric_cols].apply(pd.to_numeric, errors = 'coerce')

    return state_all_bgs

if __name__ == "__main__":
    typer.run(main)
