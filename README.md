# remoteget

__remoteget__ downloads a series of files using different protocols - http, https, ftp, ftps, (sftp not yet).

Developed for @SDFIdk to collect GNSS-related data, but may be useful for others who want to download parameterized file collections from heterogenous sources.

Uses macros for Day of Year, Year and GPS week. System environment variables (such as HOME) can also be used.

Input must be a YAML file ,set via the `-d` parameter, that specifies credentials and paths to files (see 'downloadlist-example.yaml').
It does not need to have a .yaml extension.

Setup is done using `conda` :
```bash
conda env create --file environment.yaml
conda activate remoteget
```
