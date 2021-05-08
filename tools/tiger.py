"""
This module downloads state block group shapefiles from the 2019 Census
for use in that year's ACS.

Examples
--------
This module has two functions that can be used separately.

    We can check if a proper 2019 Tiger Shapefile exists and download it
    if desired. If we wanted to check simply if a correct file exists,
    we could catch an error thrown by check_download_tiger_file.

    try:
        check_download_tiger_file("HI").
    except:
        print("No proper file!")

    To create a proper shapefile, we can turn on download_allowed. The
    output file is contingent upon the settings.

    filename = ""
    try:
        filename = check_download_tiger_file("HI")
    except:
        print("Proper file still can't be made!")

    The generation of shapefiles is easy, and uses
    check_download_tiger_file. The generated shapefile is stripped of
    extra formatting to conform with MGGG_naming standards.

    HI_blocks = ""
    try:
        HI_blocks = get_tiger_bgs("HI")
    except:
        print("No Hawaii shapefile could be made")

Notes
-----
Refactored by @gomotopia, May 2021, in debt to the original MGGG-Tooling 
by @InnovativeInventor's with heavy credit due to @jenni-niels for the
data processing techniques. 

Tiger Data for each state is easy to get and follows an easy file
pattern. The 2020 files, carry the following columns.

STATEFP
    State FIPS code, e.g. "15"
COUNTYFP
    County FIPS code, "007"
TRACTCE
    Tract Census Code, "040301"
BLKGRPCE
    Block Group Census Code, "1"
GEOID
    Geo ID, Concat. of previous codes, "150070403011"
NAMELSAD
    Name, Legal Area Statistical Area Def., "Block Group 1"
MTFCC
    MAF/Tiger Feature Class Code, "G5030"
FUNCSTAT
    Functional Status, "S"
ALAND
    Land Area in sq. meters from epsg:4269, "544238"
AWATER
    Water Area in sq. meters from epsg:4269, "0"
INTPTLAT
    Latitude of an internal point, "+22.0910243"
INTPTLON
    Longitude of an internal point, "-159.3210492"

We need only the GEOID and the geometry.

From the Census website, 2019 Block Groups can be found...

https://www2.census.gov/geo/tiger/TIGER2019/
    BG/tl_2019_19_bg.zip

For 2020, there are two parallel ways.

https://www2.census.gov/geo/tiger/TIGER2020PL/STATE/15_HAWAII/
    15/tl_2020_15_bg20.zip
https://www2.census.gov/geo/tiger/TIGER2020/
    BG/tl_2020_15_bg20.zip

As the Decennial Census, the fields in 2020 are appended with 20,
"STATEFP20," "COUNTYFP20,"... Thus in the future, we could expand this
function to handle different year's worth of TIGER data.

"""


import os
import errno
import sys
import us
import geopandas as gpd

# To make work in project or editor namespace
try: import settings as SET
except: import tools.settings as SET

import wget
from zipfile import ZipFile

def check_download_tiger_file(state_abbrev: str,
                                download_allowed: bool = False) -> str:
    """
    Checks if shapefile exists for specified state. If downloading is
    allowed, function will download and unzip shapefile from Census
    website.

    Working within the local Tiger folder in settings, this function
    looks to see if a 2019 State Block Group file is found in the proper
    local state folders. If one is found, great! The filepath is
    returned.

    If none is found, we can try create one. If the zip file is found,
    then it is extracted in a folder given its name. If no zip file is
    found, then one is downloaded from the Census website and extracted.
    We presume that the shapefile is found in these files and the
    filepath is returned.

    Parameters
    ----------
    state_abbrev: str
        Two digit state abbreviation of subject State or Territory

    download_allowed: bool
        Flag as to whether to download missing data or raise error.
        Set to avoid downloading by default.

    Notes
    -----
    Does not check if shapefile is valid! It could have wrong geography,
    data, missing support files, etc... Beware!

    Returns
    -------
    str
        Filename of found state shapefile or Null if none found or
        created.

    Raises
    ------
    Exception
        From wget in case downloading doesn't work.
    FileNotFoundError
        In case shapefile isn't found and downloading is not permitted.

    """

    # e.g. 15 for Hawaii
    state = us.states.lookup(state_abbrev)

    # e.g. shp tl_2019_15_bg.
    state_tiger_name = f"{SET.TIGER_PREFIX}{state.fips}{SET.BG_POSTFIX}"

    ## Local Filepaths

    # Hard coded to be same as above. Make more flexible in settings?
    local_state_folder = state_tiger_name
    # e.g. data/tiger/shp tl_2019_15_bg/
    local_tiger_state_folder = (
        f"{SET.LOCAL_TIGER_FOLDER}{local_state_folder}/")

    # e.g. data/shp tl_2019_15_bg.zip
    local_state_zip_filename = (
            f"{SET.LOCAL_TIGER_FOLDER}/{state_tiger_name}.zip")

    # e.g. data/tiger/shp tl_2019_15_bg/shp tl_2019_15_bg.shp
    local_state_shp_filename = (
            f"{local_tiger_state_folder}{state_tiger_name}.shp")


    ## URL for Tiger Website
    #   e.g. https://www2.census.gov/geo/tiger/TIGER2019/BG/tl_2019_19_bg.zip
    state_zip_url = f"{SET.TIGER_BG_URL}{state_tiger_name}.zip"

    # Is there no local_tiger_state folder? Get one.
    if not os.path.isdir(SET.LOCAL_TIGER_FOLDER):
        os.makedirs("SET.LOCAL_TIGER_FOLDER")

    # The Big Question
    state_shp_exists = False

    # If state shapefile, great! A shapefile can exist within
    if os.path.isfile(local_state_shp_filename):
        state_shp_exists = True
    else:
        # If not, try to unzip. First check if zip is here.
        if not os.path.isfile(local_state_zip_filename):
            # If download allowed, try to download. If not, raise exception.
            if download_allowed:
                try:
                    wget.download(
                        state_zip_url,
                        local_state_zip_filename,
                        bar=None)
                except Exception as err:
                    print (f"Unable to download {state.name} zip file " + \
                        f"from: {state_zip_url}")
                    raise err
            else:
                raise FileNotFoundError(
                    errno.ENOENT,
                    (f"Shapefile for {state.name} not found, " +
                        "downloading disabled."),
                    state_tiger_name
                    )
        # State shp zip file had or does now exists. Unzip!
        # Clean up downloaded zipfile. 
        with ZipFile(local_state_zip_filename, 'r') as state_zip:
            state_zip.extractall(local_tiger_state_folder)
        os.remove(local_state_zip_filename)
        state_shp_exists = True

    # Return filename or empty string
    return f"{local_tiger_state_folder}{state_tiger_name}.shp" \
                if state_shp_exists else ""

def get_tiger_bgs(state_abbr: str, \
                    download_allowed: bool = False) -> gpd.geodataframe:
    """
    Returns the block groups of a given state or states as a geopandas
    Geo DataFrame.

    Option to check if data is downloaded.

    Parameters
    ----------
    state_abrrev : str
        Relevant state for collecting TIGER block group shapefiles.

    download_allowed : bool
        Flag as to whether to download missing data or raise error.
        Set to avoid downloading by default.

    Returns
    -------
    geopandas.geoDataFrame or null
        Returns geoDataFrame with only GEOID and geometry or null if 
        none found.

    Raises
    ------
    Exception
        Valid state shapefile filename cannot be found or generated.
    Exception
        The shapefile is corrupted and cannot be read by GeoPandas
    Exception
        The GeoDataFrame does not contain GEOID or geometry.
    """
    state = us.states.lookup(state_abbr)
    tiger_data = ""

    try:
        valid_tiger_file = check_download_tiger_file(state_abbr, \
                                                    download_allowed)
    except Exception as check_error:
        print (f"No valid shapefile found or generated for {state.name}")
        raise
    else:
        try:
            tiger_data = gpd.read_file(valid_tiger_file)
        except Exception as read_error:
            print(f"Shapefile could not be read properly for {state.name}.")
            raise
        else:
            # Select only columns we need and rename column.
            try:
                tiger_data = tiger_data[['GEOID','geometry']]
            except Exception as cols_error:
                print("Columns could not be selected properly in " + \
                        f"{state.name} shapefile")
                raise
    return tiger_data
