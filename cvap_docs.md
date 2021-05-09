# Converting the CVAP CSV into a Pandas Dataframe

[Information on Citizen Voting Age Population][1], or CVAP, based on the
[2019 5-Year American Community Survey.][2], was released in Februrary
2021. It is reported in a very unusual format! 

Credit for unlocking this puzzle goes to [@jenni-niels][4]
and coded in the original [mggg-tooling][6] by [@InnovativeInventor][5].
Kudos to both!

## Raw Data

Rather than each geographic unit having many columns representing totals
for each Race/Origin, every unit has many rows to achieve the same.
Thus, one Block Group may have many rows, rather than just one in
regular ACS data. Downloading the data from the source reveals that
information for the entire country is stored in csv's of different
geographic units. The one we use is stored as `BlockGr.csv`.

```
	                                  	    
geoname	            lntitle	            geoid	  lnnumber  cit_est cit_moe cvap_est    cvap_moe
Block Group 1...	Total   	        15000US...1	2	725	222	610	186
Block Group 1...	Not Hisp...	        15000US...1	2	715	221	600	184
Block Group 1...	American Indian...	15000US...1	3	0	12	0	12
Block Group 1...	Asian...	        15000US...1	4	0	12	0	12
```
So unusual! 

Each Block Group is identified by...
-`geoname` e.g...
    "Block Group 1, Census Tract 201, Autauga County,..."
-`geoid`
    "15000US010010201001"

...copied over...
-`lntitle` e.g...
    "Total","Asian Alone"...
-`lnnumber`
        "1","4"

...listing the following data:
- `cit_est`
    The estimates of the number of Citizens
- `cit_moe`
    The margin of error of Citizens
- `cvap_est`
    Estimate of Citzens over 18, the Voting Age
- `cvap_moe`
    Margin of error for Citzens of Voting Age Population.

## Reading the File 

Reading the file is simple. We use `polars` to read this in quickly, 
filter on the `geoname` column for the relevant state and convert the
result into a `pandas.DataFrame`.

```
import polars as pl

state = us.states.lookup(state_abbrev)
cvap_bgs_pl = pl.scan_csv("BlockGr.csv")
state_cvap_bgs = (
    cvap_bgs_pl.filter(pl.lazy.col("geoname").str_contains(state.name))
    .collect()
    .to_pandas()
```

## The First Data Frame

The first `DataFrame` has the following columns, essentailly taking the
data in line by line.
```
state_cvap_bgs.columns = Index(['geoname', 'lntitle', 'geoid', 'lnnumber',
'cit_est', 'cit_moe','cvap_est', 'cvap_moe'])
```
Like above, you'll find entries with duplicate `geoname`s and `geoid`s.
Finally, we replace the long form `lntitle`s with [mggg standardized
codes][14]. At this point, its index is still a simple 
`pandas.RangeIndex`.
```
CVAP_RACE_NAMES = {
        "Total": "TOTPOP",
        "Not Hispanic or Latino": "NH", # unused?
        "American Indian or Alaska Native Alone": "NH_AMIN",
        ...}

state_cvap_bgs.replace(to_replace=CVAP_RACE_NAMES, inplace=True)
```

## Grouping on the duplicate Block Group rows 

Since information by Block Group is split over several rows, we must
group them all together. When we replaced the `lnvalues` above, you'll
notice that races of two or more are applied the same code. They will
aggregate together in this step. We tell `Pandas` to group by the
geographic columns which results in a `DataFrameGroupBy` object. We then
apply `.agg` instructing the object to sum data found in the numeric
columns.

```
state_cvap_bgs = (
    state_cvap_bgs.groupby(["geoname", "lntitle", "geoid"])
    .agg({"cit_est": "sum","cvap_est": "sum"})
    .reset_index()
)
```

Since this removes rows from our `DataFrame`, we `reset_index` to ensure
that the dataframe's index is still a `RangeIndex` of sequential
numbers. The final result is once again a `DataFrame`.

## The Magic Pivot

We continue to have the original problem, that data for a single Block
Group is contained in multiple rows. Using `.pivot` we ensure that each
all information for a single block group is colected together. 

Our new structure is designed to have `geoid` as its index. Multiple
rows with the same geoid must now be combined. Remember, each `lntitle`
race/origin category in each `geoid` had two values (that we're
interested in): `cvap_est` and `cit_est`. Thus, we functionally have a
`MultiIndex` where each of the values has a set of the columns. 

```
Pivot table such that new index is geoid
state_cvap_bgs = state_cvap_bgs.pivot(
      index="geoid",
      columns="lntitle",
      values=["cvap_est", "cit_est"],
  )
```

Each row is now structured as follows with two levels of column index.
```
geoid
cvap_est
    HISP
    NH
    NH_2More
    ...
cit_est
    HISP
    NH
    NH_2More
    ...
```

This object's index is no longer a simple `RangeIndex` but a
`MultiIndex` where each column, represented as a pair, is part of the 
index.

```
state_cvap_bgs.index = 
MultiIndex([('cvap_est',     'HISP'),
            ('cvap_est',       'NH'),
            ('cvap_est', 'NH_2MORE'),
            ('cvap_est',  'NH_AMIN'),
            ('cvap_est', 'NH_ASIAN'),
            ...
            names=[None, 'lntitle'])
```

This makes the DataFrame difficult to use, so we `.reset_index` again to
make sure the index is a simple `RangeIndex` once again, satisfied that
each `geoid` is given one and only one row. 

## Combining the multi-level columns

The columns are now described in two levels, one for the type of data,
CVAP estimate, Citizen Estimate, etc, and another for each Race/Origin.
Thus, we must rename the columns with a single string combination of the
two levels of names (while renaming some of the codes.)
```
state_cvap_bgs.rename(columns={"cvap_est": "CVAP", "cit_est": "CPOP"},
                                inplace=True)
state_cvap_bgs.columns = [
     "_".join(col).strip() for col in state_cvap_bgs.columns.values]                               
```
A columns of name (`'cvap_est','HISP')` and 
`('cvap_est','NH')` are now simply named `CVAP_HISP` and `CVAP_NH`.

## The Clean Up

The data frame is now a straight forward `DataFrame` where each `geoid`
has a set of columns with certain data. The only thing left to do is to
clean up the data. First, we start with removing the _ we added in
`GEOID` and clipping the `050000US` prefix found in all U.S. Block
Group ids. 

```
state_cvap_bgs = state_cvap_bgs.rename(columns={"GEOID_": "GEOID"})
state_cvap_bgs["GEOID"] = state_cvap_bgs["GEOID"].apply(lambda x: x[7:])
```
Each column must now be renamed once more to apply to
[MGGG standards][14]. If we wanted to rename only once, we could
inconveniently keep the full "Not Hispanic or Latino" names rather than
shortening them and only rename once at the end. 
```
state_cvap_bgs = state_cvap_bgs.rename(columns=RENAME_AGAIN)
state_cvap_bgs.reset_index(inplace=True)
```
We also reset the index once more for good measure.

```
state_cvap_bgs.columns = Index(['GEOID', 'CVAP', 'HCVAP', 'WCVAP'...,])
```
## Return! 
```
return state_cvap_bgs
```
# Thanks Again...
...to my friends [JN][4] and [Max][5] for their work in cracking this
puzzle. 

Signed, [@gomotopia][21]
May 2021

🛁☀️🕶️

[1]: https://www.census.gov/programs-surveys/decennial-census/about/voting-rights/cvap.2019.html

[2]: https://www.census.gov/data/developers/data-sets/acs-5year.html

[4]: https://github.com/jenni-niels

[5]: https://github.com//InnovativeInventor/

[6]: https://github.com/InnovativeInventor/mggg-tooling

[14]: https://github.com/mggg/mggg-states-qa/blob/main/src/naming_convention.json

[21]: https://github.com/gomotopia
