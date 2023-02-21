# Download a series of files
# One parameter: -d, downloads file (YAML). See example.
# Can evaluate day of year and gpsweek for macro resolution
# Lars Næsbye Christensen, 2023

import argparse
from pathlib import Path
from datetime import date, timedelta, datetime
from ftplib import FTP, FTP_TLS
from urllib.parse import urlparse
from os import environ
import requests
import yaml

# Constants and globals
version = "0.9"
args = None
downloadlist = None


def parse_arguments() -> None:
    global args
    parser = argparse.ArgumentParser("remoteget")
    parser.add_argument(
        "-d",
        "--downloadpath",
        help="path to file containing download locations",
        action="store",
        type=str,
    )
    args = parser.parse_args()


def download_http(domain: str, remotepath: Path, localpath: Path) -> None:
    """Handles HTTP and HTTPS downloads without credentials.
    Allow following redirects for simplicity."""
    r = requests.get(domain + remotepath.as_uri(), allow_redirects=True)
    with open(localpath / remotepath.name, "wb") as file:
        file.write(r.content)


def download_ftp(scheme: str, domain: str, remotepath: Path, localpath: Path) -> None:
    """Handles FTP (insecure) and FTPS downloads using anonymous user."""
    if scheme == "ftps":
        ftp = FTP_TLS(domain)  # connect to host, default port
    else:
        ftp = FTP(domain)
    ftp.login()  # user and pass is anonymous
    ftp.cwd(str(remotepath.parent))  # change into the path's parent
    with open(localpath, "wb") as fp:
        ftp.retrbinary("RETR %s" % remotepath.name, fp.write)
    ftp.quit()


def calc_gps_week(tocalc: date) -> int:
    gps_epoch = date(1980, 1, 6)  # GPS week 0
    epoch_monday = gps_epoch - timedelta(gps_epoch.weekday())
    today_monday = tocalc - timedelta(tocalc.weekday())
    return int((today_monday - epoch_monday).days / 7)


def calc_year_yyyy() -> str:
    today = datetime.today()
    return today.strftime("%Y")


def calc_year_yy() -> str:
    today = datetime.today()
    return today.strftime("%y")


def calc_doy() -> int:
    return datetime.now().timetuple().tm_yday


# Some useful macros
macros = {
    "$DOY$": str(calc_doy()),
    "$YYYY$": calc_year_yyyy(),
    "$YY$": calc_year_yy(),
    "$GPSWEEK$": str(calc_gps_week(date.today())),
}
# Add the system environment variables to our macro collection
for name, value in environ.items():
    macros["$" + name + "$"] = value


def resolve_macros(macrostring: str) -> str:
    """Replaces macros with their calculated values."""
    resultstring = macrostring
    for key in macros.keys():
        resultstring = resultstring.replace(key, macros[key])
    return resultstring


# --- MAIN PROGRAM  ---------------------------------
print(
    datetime.fromtimestamp(datetime.now().timestamp()), " Starting remoteget " + version
)
parse_arguments()  # parse arguments. Only one for now: d for download list

# Using the download list argument, we load the YAML file specifying files to download and how
with open(args.downloadpath) as f:
    downloadlist = yaml.load(f, Loader=yaml.FullLoader)

for location in downloadlist["downloads"]:
    parsedurl = urlparse(resolve_macros(downloadlist["downloads"][location]["url"]))
    dest = Path(resolve_macros(downloadlist["downloads"][location]["dest"]))
    match parsedurl.scheme:
        case 'http' | 'https':
            download_http(parsedurl.netloc, Path(parsedurl.path), localpath=dest)
        case 'ftp' | 'ftps':
            download_ftp(parsedurl.scheme, parsedurl.netloc, Path(parsedurl.path), localpath=dest)

print(
    datetime.fromtimestamp(datetime.now().timestamp()), " Ending remoteget " + version
)
