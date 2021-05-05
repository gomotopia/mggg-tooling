# Level 0
typer.run Command Line Client
must be set to main, with docstring

# Level 1
Rename main(filename: str, output: str, postal_code: str, overwrite: bool = False)
to write_full_data_shapefile

- collect_list_of_cvap_bgs
- get_nhgis_acs_data
- get_bg_tiger_file
- get_state_cvap_shapes
- merge_shapes
- merge_and_maup_data
- shapefile.to_file(final_merged_data)

# Level 2 

**collect_list_of_cvap_bgs**
With zipcode, look for `CVAP_2015-2019_ACS_csv_files.zip`
which results in `BlockGr.csv` then filter for those in state. 

**get_nhgis_acs_data**
Check for manually downloaded nhgis file, return acs_race data with cleaned up and relabel NHGIS columns

**get_bg_tiger_file**
Download and extract state bg shapes
return block_group_shapes

**get_state_cvap_shapes**
Essentially load_state_cvap_shapes

**merge_and_maup_data**
If overwite, delete original data
maup stuff, with weights.

**shapefile.to_file(final_merged_data)**

# Constants:

    bgs_to_blocks_cols = list(
        set(
            [
                "HCVAP",
                "HCPOP",
                "HPOP",
                "NHCVAP",
                "NHCPOP

    race_names = {
        "Total": "TOT",
        "Not Hispanic or Latino": "NH",
        "American Indian or Alaska Native Alone": "NH_AMIN",
        "Asian Alone": "NH_ASIAN",

    ["cvap_est", "cit_est"],

    to_rename = {
        "CVAP_HISP": "HCVAP",
        "CPOP_HISP": "HCPOP",
        "POP_HISP": "HPOP",
        "CVAP_NH": "NHCVAP",

    race_nhgis_mappings = {
        "ALUCE001": "TOTPOP",
        "ALUCE002": "WPOP",
        "ALUCE003": "BPOP",
        "ALUCE004": "AMINPOP",

    for unit, suffix in [("CVAP", "CVAP"), ("CPOP", "CPOP"), ("TOTPOP", "POP")]:


NHGIS uses 

    ALUKE001	ALUKE002	ALUKE003	ALUKE004	ALUKE005	ALUKE006

CVAP uses 

    geoname	lntitle	geoid	lnnumber	cit_est	cit_moe	cvap_est	cvap_moe
    Block Group 1, Census Tract 201, Autauga County, Alabama	Total	15000US010010201001	1	725	222	610	186
    Block Group 1, Census Tract 201, Autauga County, Alabama	Not Hispanic or Latino	15000US010010201001	2	715	221	600	184
    Block Group 1, Census Tract 201, Autauga County, Alabama	American Indian or Alaska Native Alone	15000US010010201001	3	0	12	0	12

TIGER (EPSG:4269 - NAD 83) uses

    STATEFP20
    COUNTYFP20
    TRACTCE20
    BLKGRPCE20
    GEOID20
    NAMELSAD20
    MTFCC20
    FUNCSTAT20
    ALAND20
    AWATER20
    INTPTLAT20
    INTPTLON20