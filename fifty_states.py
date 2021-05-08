"""
This example downloads ASCS and CVAP shapefiles of all United States plus DC
and Puerto Rico. 
"""

import us
from tqdm import tqdm
from tools.census_adder import make_race_cvap_shp

allstates = us.states.STATES + [us.states.DC, us.states.PR]

allstates = allstates[:5]

for state in tqdm(allstates):
    make_race_cvap_shp(state.abbr, download_allowed=True)