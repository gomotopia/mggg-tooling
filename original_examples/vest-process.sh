fd --search-path ~/Dropbox\ \(Personal\)/mggg/drafts_with_VEST/ ".shp" -x sh -c 'python tools/dedup.py "{}" "{.}.dedup.shp" --column GEOID20'
fd --search-path ~/Dropbox\ \(Personal\)/mggg/drafts_with_VEST/ ".dedup.shp" -x sh -c 'python tools/census_adder.py "{}" "{.}.census.shp" $(echo {/} | head -c2)'
