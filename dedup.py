import typer
import geopandas as gpd
def main(filename: str, output: str, column: str = "GEOID"):
    """
    Deduplicates a shapefile by a certain column
    """
    shapefile = gpd.read_file(filename)
    shapefile = shapefile[~shapefile[column].duplicated()]
    shapefile.to_file(output)

if __name__ == "__main__":
    typer.run(main)
