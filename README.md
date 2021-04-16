## MGGG-tooling
This repository contains short and self-contained tools and scripts to process, clean, and create MGGG shapefiles.
The structure of this repository is inspired by the Unix philosophy of minimalist, modular software development.

Tools:
- census_adder.py: A quick script to maup CVAP and ACS data to an arbitrary shapefile.
- dedup.py: Deduplicate rows in a shapefile

Tools in the works
- vestment.py: A tool to add VEST data onto Census VTDs.
- checker.py: Run automated QA checks on shapefiles

## Usage
To see how to use the tool, read the comments at the top of the file or pass `--help` as an argument. Eg: `python dedup.py --help`.

## Setup
For most of the scripts, you can do (make sure to install Poetry via `pip` first):
```
poetry shell
python main.py [args]
```

However, for `census_adder.py` need to manually fetch `nhgis0001_ds244_20195_2019_blck_grp.csv` from NHGIS and place it in the `census/` folder before running.
You also need to ensure that you have `aria2c` (https://aria2.github.io/) installed.
