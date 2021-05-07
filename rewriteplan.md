|-census LOCAL_DATA_FILE  
|-examples  
|-tools  

# Level 0
typer.run Command Line Client
must be set to main, with docstring

- State FP?
- Zip Code?
- Original Filename?
- Output Filename?
- Year?
- Kind? Race-Pop, CVAP, Shp??
- Kind? NHGIS, etc.
- Unit?
- Check for downloads?

# Level 1
_main(filename: str, output: str, postal_code: str, overwrite: bool = False)_  
make_race_cvap_shp(state_abbrev: str):

- Load Settings
- `cvap2019.get_cvap_bgs(state_abbrev)(...)`
- `nhgis.get_nhgis_race_bgs(...) as get_race_bgs(...)`
- `race_cvap_merge(...)`
- `tiger.get_tiger_bgs(...)`
- Data Merge and Process???
- `geoDataFrame.to_file(...)`

# Level 2 

**cvap2019.get_cvap_bgs(state_abbrev)(...)**
- Check data. Use Python libs.
- Write detailed docs on CVAP format
- Different years of data?

**nhgis.get_nhgis_race_bgs as get_race_bgs(...)**
- Check data (easy to do)
- Could plug-in direct or census package in Settings.py

**race_cvap_merge(...)**

**tiger.get_tiger_bgs(...)**
- Check donwnload. Use Python.
- Different years? 

**Data Merge and Process???**
- Read Filename if relevant
- Ensure epsg:4269
- Collect list of similar columns
- If overwrite, delete cols
- Take intersected pieces
- Prorate on total within CVAP, pop
- - Use weights to prorate

**geoDataFrame.to_file(...)**
