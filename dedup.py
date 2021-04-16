import typer
import geopandas as gpd

"""
Usage: dedup.py [OPTIONS] FILENAME OUTPUT

  Deduplicates a shapefile by a given column

Arguments:
  FILENAME  [required]
  OUTPUT    [required]

Options:
  --column TEXT                   [default: GEOID]
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.

  --help                          Show this message and exit.
"""


def main(filename: str, output: str, column: str = "GEOID"):
    """
    Deduplicates a shapefile by a given column
    """
    shapefile = gpd.read_file(filename)
    shapefile = shapefile[~shapefile[column].duplicated()]
    shapefile.to_file(output)


if __name__ == "__main__":
    typer.run(main)
