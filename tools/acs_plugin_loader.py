"""
There are many ways to capture ACS data. We can load each of these different
ways based on preference. 

Examples
--------

settings.py
ACS_PLUGIN = "NHGIS"

race-adder.py
get_race_origin_bgs = acs_plugin_loader.load_plugin(ACS_PLUGIN)
"""
import importlib

def set_race_origin_bgs(plugin_name: str):
    race_origin_function = ""
    if plugin_name is "NHGIS":
        try:
            mymodule = importlib.import_module("nhgis")
        except:
            try:
                mymodule = importlib.import_module("tools.nhgis")
            except:
                print("No NHGIS module!")
                raise
        race_origin_function = mymodule.get_nhgis_race_bgs
    elif plugin_name is "CensusAPI":
        try:
            mymodule = importlib.import_module("census2019")
        except:
            try:
                mymodule = importlib.import_module("tools.census2019")
            except:
                print("No Census2019 API module!")
                raise
        race_origin_function = mymodule.get_censusapi_race_bgs
    else:
        raise NameError("NoModuleSet")

    return race_origin_function