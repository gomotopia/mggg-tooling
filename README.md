# MGGG-Tooling for Citizen Voting-Age Population

In February, 2021, the Census Bureau released information on projected
[Citizen Voting Age Population][1] broken down by Race/Origin down to
block groups, based on the [2019 5-Year American Community Survey.][2]
This tool allows for the creation of State Block Group state shapefiles
based on the [2019 TIGER boundaries][3] with merged CVAP and 2019
ACS Race/Origin Census Information. The bulk of this is based on the
original [mggg-tooling][6] by [@InnovativeInventor][5] which in turn
credits [@jenni-niels][4] for techniques in data processing.  

## Our Large Nation

Creating a batch of shapefiles is as easy as the script below! Clone
this repository and run python [FiftyStates.py][7] after downloading 
the correct nhgis and cvap files and checking that you’re happy with
[tools.settings.py][8]. 
```
import us
from tqdm import tqdm # For progress bar
from tools.census_adder import make_race_cvap_shp

allstates = us.states.STATES + [us.states.DC, us.states.PR]

for state in tqdm(allstates):
    make_race_cvap_shp(state.abbr, download_allowed=True)

```
Sample data shapefile output for inspection can be found
[here][9]. 

## Modular Functionality 
The tools package in this repository carries the following modules and
attendant functions.

### [tools.tiger][10]

Tiger has many files depending on state and must account for the many
state folders and shapefiles that could be in use.

```
def check_download_tiger_file(state_abbrev: str,
                                download_allowed: bool = False) -> str:
    """
    Checks if shapefile exists for specified state. If downloading is
    allowed, function will download and unzip shapefile from Census
    website...

def get_tiger_bgs(state_abbrev: str, \
                    download_allowed: bool = False) -> gpd.geodataframe:
    """
    Returns the block groups of a given state or states as a geopandas
    Geo DataFrame...
```
	
### [tools.nhgis][11]

The current implementation of sourcing 2019 5Y ACS Data is through
the [NHGIS][19], which provides easily standardized information but must
be downloaded manually. Fortunately, block groups for the whole country
are included in one file. For this package, we rely on **NHGIS:ALUK**
based on **Census B03002** for Race and Origin for 2019 5Y ACS.
```
def check_nhgis_data():
    """
    Checks if NHGIS csv file exists in the location specified by the
    settings. If none found, an exception is raised....

def get_nhgis_race_bgs(state_abbr: str):
    """
    This returns a pandas DataFrame of NHGIS ACS 2019 Race and Origin
    data filtered by the given state in columns following MGGG naming
    standards...
```

NHGIS is only one of several ways to collect Census data. In
anticipation of future methods, `get_nhgis_race_bgs` is renamed
`get_race_origin_bgs` whenever it is used. 

### [tools.cvap2019][12]:

CVAP information is provided in many geographies for the whole nation in
an unusual file format. I learned a lot by studying the brilliant
technique provided by [JN][4] and [Max][5] that I detail in
[cvap_docs.md][20].

```
def check_download_cvap19_data():
    """
    Checks if the CVAP 2019 csv file exists in the location specified by
    the settings. If none found, an exception is raised...

def get_cvap_bgs(state_abbr: str):
    """
    This returns a pandas DataFrame of the Citizens of Voting Age
    Population in each Block Group of the specified state...
```

*In the future, `check_download_cvap19_data` will download the data
from the census website to the correct directory, but for now, please
download and place this manually per docs.*

### [tools.census-adder][13]
This file, from the original [mggg-tooling][6], served as the original fork
for this environment. It offers three functions...

```
def race_cvap_merge(race_data, cvap_data):
    """
    Conducts inner join of mggg-standardized race and cvap data...


def make_race_cvap_gdf(state_abbr: str, download_allowed: bool = False):
    """
    Returns geoDataFrame of Block Groups in target State with CVAP and
    ACS Race information formatted to mggg-standards...

def make_race_cvap_shp(state_abbr: str, output = "", \
                                        download_allowed: bool = False):
    """
    Creates Shapefile of Block Groups in target State with CVAP and ACS
    Race information formatted to mggg-standards as well...
```
...and is the home for providing CLI compatibility with its parent fork. 
```
def main(filename: str, output: str, \
                    postal_code: str, overwrite: bool = False):
    """
    To ensure some compatibility, we retain the original CLI inputs from
    original MGGG-tooling repository.
```

Each can be used separately and return either pandas DataFrames or
geopandas GeoDataFrames with Block Groups titled by short GEOID and data
columns listed in [MGGG Standardized][14] columns. 

## Settings

Since these functions are designed to check, download and manipulate
files, urls and paths are set in [tool.settings][8]. Currently, the settings
presupposes the following local file structure.

```
mggg-tools/
├── tools/
│   ├── settings.py
│   ├── tiger.py
│   ├── nhgis.py
│   ├── cvap2019.py
│   └── census_adder.py
├── data/
│   ├── CVAP5Y2019/
│   |   ├── CVAP5Y2019/
│   |   |   ├──CVAP_2015-2019_ACS_csv_files
│   |   |   |   ├── BlockGr.csv
│   |   |   |   └── ...
│   ├── nhgis0004_csv/
│   |   ├── nhgis0004_ds244_20195_2019_blck_grp.csv
│   |   └── ...
│   ├── Tiger19_bgs/
│   |   ├── tl_2019_01_bg
│   |   |   ├── tl_2019_01_bg.shp
|   |   |   └── ...
│   |   ├── tl_2019_01_bg.zip
│   |   └── ...
│   ├── cvap_acs-output/
|   |   ├── AL_cvap_acs/
|   |   |   ├── AL_cvap_acs.shp
│   |   |   └── ...
│   |   └── ...
|   └── ...
└── ...
```

## Philosophy
I’m not naturally a coder or computer scientist and only feel secure in
anything I can teach. Thus, these files are overwhelming in their
documentation and perhaps even loquacious in its design architecture.
Much of these functions could be combined or optimized. 

However, as a teaching tool, this package should hold appeal no matter
whether one has deep or scant curiosity on how it works. It must do
exactly what it says with ease and transparent on what it says, such
that data is streamline, easily verified, holds no surprises and is of
the highest quality.

As such, it is written using **[PEP8][15], [type hinting][16],
[numpy docs][17] and judicious in-line documentation** as best as 
possible.

## Compatibility 
This package is a refactored fork of the original [mggg-tooling][5], a
command line application originally described as... 

```
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
```
... and whose original readme is retained [here][18].

The original function used [maup][19] to compare ACS and CVAP data with
an original filename, where weight-based proration was applied. **This
has yet to be implemented.**

As someone more comfortable with Python, I wanted to transfer system
operations away from the command line, including the use of `os`,
`wget` and `zipfile`.

This fork also ensures the use of 2019 shapefiles for 2019 Census Data
Products. 

Some backwards compatibility is provided, however, but without original
data merging functionality. 

## Requirements
The original repo depended on `poetry` for version requirements.
Versioning using package.json poetry or pip has yet to be implemented
and is next on the to do list, so the python package requirements below
must be included manually. 

- ```us```, American States as objects
- ```pandas```, Dataprocessing
- ```geopandas```, Dataprocessing with maps
- ```polars```, Faster dataprocessing
- ```wget```, Downloading with Python
- ```zipfile```, Unzipping with Python
- ```tqdm```, Progress bars

Original CLI and data processing requirements.
- ```typer``` CLI utility
- ```aria2c``` BASH downloader
- ```unzip``` BASH unzipper
- ```maup``` District assignment, proration and aggregation

## Plugging for the Future

- ### Versioning, out of the box, pypi 

   My hope is for this to be a well-used, extensive, modular and turn-key
pypi candidate that’s easy to use, easy to use and easy to understand.
The first step is providing ease of download by including pip or poetry
requirements files.

- ### Different algorithms for ACS

   One way to collect ACS data is directly through the api or by using a
different python ```census``` package. A plug-in loader, akin to django
apps, should make it easy to include different ways of collecting data
provided that mggg naming conventions are used. 

- ### Different geographic areas, with [MAUP][19]

    Since the [original][6] mggg-tooling considered the disaggregation of
CVAP and ACS data onto different sized geographic units, native
functionality or tutorial on how to use blocks, tracts, etc., should be
included. A test for this should be building compatibility between this
and the [original][6].

- ### Different Years and Data Sets
    A promise of plug-in style modularity points us in a direction towards
the inclusion of different and future years’ collection of data,
particularly with the arrival of Census 2020 data. NHGIS, for instance,
provides a large repository of standardized historical data. 

    MGGG happens to use some census data on housing characteristics and
other demographic data.

    The trick is to account for the variety and peculiarities of the many
Census and derivative file formats. The implementation of a plug-in
loader for different ACS algorithms or the ability to choose different
years’ TIGER files will be great first steps.

- ### Select by Area

   Maybe one day, we can do more with shapefiles than return states.
Geopandas methods like ```envelope``` and ```overlay``` could help us
return only pieces of large shape files. 

## Acknowledgements

Thanks [JN][4] and [Max][5] I was able to learn much more about the census,
pandas and geopandas. 

As someone less comfortable with command line applications, I found Max's
[original][6] repo to be revelatory. I learned...
- That command line applications can be built with `typer`.
- That `os` has many ways for Python to make SH commands. I particularly
learned his way to check for local files and folders and the fetching
of downloads 
- That `polars` is a fast way to process information and is compatible
with `pandas`
- That `subprocess` is a way to manage threads like downloads.
- That `aria2c` and `unzip` are native applications in SH to download
and unzip files. 
- That `poetry` is another way maintain python package dependency
requirements

I also enjoyed upgrading my skills in pandas and dataframes thanks again
to JN's work with Max which I’ve detailed [here][20].

## _Thanks!_

Signed, [@gomotopia][21]
May 2021

🐰🗼🐌

[1]: https://www.census.gov/programs-surveys/decennial-census/about/voting-rights/cvap.2019.html

[2]: https://www.census.gov/data/developers/data-sets/acs-5year.html

[3]: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.2019.html

[4]: https://github.com/jenni-niels

[5]: https://github.com/InnovativeInventor/

[6]: https://github.com/InnovativeInventor/mggg-tooling

[7]: ../main/fifty_states.py

[8]: ../main/tools/settings.py

[9]: ../main/sample_output

[10]: ../main/tools/tiger.py

[11]: ../main/tools/nhgis.py

[12]: ../main/tools/cvap2019.py

[13]: ../blob/main/tools/census-adder.py

[14]: https://github.com/mggg/mggg-states-qa/blob/main/src/naming_convention.json

[15]: https://www.python.org/dev/peps/pep-0008/

[16]: https://www.python.org/dev/peps/pep-0484/

[17]: https://numpydoc.readthedocs.io/en/latest/format.html

[18]: ../main/Original_README.md

[19]: https://github.com/mggg/maup

[20]: ./cvap_docs.md

[21]: https://github.com/gomotopia
