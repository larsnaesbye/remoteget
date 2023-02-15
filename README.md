# remoteget

__remoteget__ downloads a series of files using different protocols - http, https, ftp, ftps, sftp.

Developed for the AutoBernese system at SDFI to collect GNSS-related data, but may be useful for others who want to download parameterized file collections from heterogenous sources.

Uses macros for Day of Year, Year and GPS week. System environment variables (such as HOME) can also be used.

Input must be a YAML file (see 'downloadlist-example.yaml') that specifies credentials and paths to files.
