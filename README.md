## Census-adder
A quick script to maup CVAP and ACS data to an arbitrary shapefile.

```
Example: python main.py tests/PA_final.shp output.shp PA
```

```
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
```

## Setup
You need to manually fetch `nhgis0001_ds244_20195_2019_blck_grp.csv` from NHGIS and place it in the `census/` folder before running.
To install the deps, ensure that you have `aria2c` (https://aria2.github.io/) installed and `poetry` (via pip).
Then, do:
```
poetry shell
python main.py [args]
```
