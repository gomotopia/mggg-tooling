"""
    Written by @gomotopia, May 2021, with heavy credit due to
    @InnovativeInventor/MGGG-Tooling for the data processing techniques
    and in turn, @jenni-niels.

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
    
    We need only the
    GEOID20 and the geometry.
    
    From the Census website, 2019 Block Groups can be found...

    https://www2.census.gov/geo/tiger/TIGER2019/
        BG/tl_2019_19_bg.zip

    For 2020, there are two parallel ways. 

    https://www2.census.gov/geo/tiger/TIGER2020PL/STATE/15_HAWAII/
        15/tl_2020_15_bg20.zip
    https://www2.census.gov/geo/tiger/TIGER2020/
        BG/tl_2020_15_bg20.zip

    As the Decennial Census, the fields in 2020 are appended with 20,
    "STATEFP20," "COUNTYFP20,"...

"""
import us
import geopandas as gpd
import settings as SET

# def check_tiger_data(state_abbrev: str):
#     if not os.path.isfile(f"census/tl_2020_{state.fips}_bg20.zip"):
#         subprocess.run(
#             f"aria2c https://www2.census.gov/geo/tiger/TIGER2020PL
#                   /STATE/{state.fips}_{state.name.upper()}
#                   /{state.fips}/tl_2020_{state.fips}_bg20.zip -d census",
#             shell=True,
#         )

def get_tiger_bgs(state_abbrev: str):
    """
    Returns the block groups of a given state as a geopandas
    Geo DataFrame.

    Option to check if data is downloaded.

    Parameters
    ----------
    state_abrrev : str
        Relevant state to return block groups geoDataFrame.

    Returns
    -------
    geopandas.geoDataFrame
        DataFrame of state Block Group boundaries. We only 
        include GEOID and the geometry.

    Raises
    ------

    """
    state = us.states.lookup(state_abbrev)
    # check_tiger_data(state)
    tiger_data = gpd.read_file(f"{SET.LOCAL_DATA_FOLDER}/" +
        f"{SET.TIGER_PREFIX}{state.fips}{SET.BG_POSTFIX}/" +
        f"{SET.TIGER_PREFIX}{state.fips}{SET.BG_POSTFIX}.shp")

    # Select only columns we need and rename column. 
    tiger_data = tiger_data[['GEOID','geometry']]

    return tiger_data