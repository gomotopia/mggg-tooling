## Census-adder
A quick script to add CVAP and ACS data to an arbitrary shapefile.

```
Example: python main.py tests/PA_final.shp output.shp PA
```

```
Usage: main.py [OPTIONS] FILENAME OUTPUT POSTAL_CODE

  Adds CVAP and ACS data to an arbitrary state-level shapefile

Arguments:
  FILENAME     [required]
  OUTPUT       [required]
  POSTAL_CODE  [required]

Options:
  --overwrite / --no-overwrite    [default: False]
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.

  --help                          Show this message and exit.
```
