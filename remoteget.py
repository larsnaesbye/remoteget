# Download a series of files
# One parameter: -d, downloads file (YAML). See example.
# Can evaluate day of year and gpsweek for macro resolution
# Lars Næsbye Christensen, 2023

import argparse
import os
from datetime import date, timedelta, datetime
from ftplib import FTP, FTP_TLS
from urllib.parse import urlparse

import requests
import yaml
from fabric import Connection

# Constants and globals
version = "0.9"
args = None
creds = None
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


def download_http(url, localpath) -> None:
    """Handles HTTP and HTTPS downloads without credentials.
    Allow following redirects for simplicity."""
    r = requests.get(url, allow_redirects=True)
    a = urlparse(url)
    print(localpath + os.path.basename(a.path))
    # TODO: use open with for closing connection
    open(localpath + os.path.basename(a.path), "wb").write(r.content)


def download_ftp(url, usr, pword, localpath) -> None:
    """Handles FTP (insecure) and FTPS downloads with user/password.
    FTP should NOT be used except with 'anonymous' as username and password."""
    a = urlparse(url)
    if a.scheme == 'ftps':
        ftp = FTP_TLS(a.netloc)  # connect to host, default port
    else:
        ftp = FTP(a.netloc)  # connect to host, default port
    ftp.login(user=usr, passwd=pword)
    ftp.cwd(os.path.dirname(a.path))  # change into the specified directory
    with open(localpath + os.path.basename(a.path), "wb") as fp:
        ftp.retrbinary("RETR %s" % os.path.basename(a.path), fp.write)
    ftp.quit()


def download_sftp(url, usr, pword, localpath) -> None:
    """Handles SFTP downloads with credentials. Uses fabric."""
    a = urlparse(url)
    print(a)
    c = Connection(
        a.netloc, port=22, user=usr, connect_kwargs={"password": pword}
    )
    print(c)
    c.get(os.path.basename(a.path))
    # TODO: set local path for getting


def calc_gps_week() -> int:
    gps_epoch = date(1980, 1, 6)  # GPS week 0
    today = date.today()
    epoch_monday = gps_epoch - timedelta(gps_epoch.weekday())
    today_monday = today - timedelta(today.weekday())
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
    "$GPSWEEK$": str(calc_gps_week()),
}
# Add the system environment variables to our macro collection
for name, value in os.environ.items():
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

# This should probably move into a separate function to avoid variable shadowing
for location in downloadlist["downloads"]:
    method = downloadlist["downloads"][location]["method"]
    url = downloadlist["downloads"][location]["url"]
    path = downloadlist["downloads"][location]["path"]
    user = downloadlist["downloads"][location]["user"]
    password = downloadlist["downloads"][location]["pass"]
    dest = downloadlist["downloads"][location]["dest"]

    match method:
        case 'http' | 'https':
            download_http(method + "://" + url + path, localpath=dest)
        case 'ftp' | 'ftps':
            download_ftp(method + "://" + url + path, usr=user, pword=password, localpath=dest)
        case 'sftp':
            download_sftp(method + "://" + url + path, usr=user, pword=password, localpath=dest)

print(
    datetime.fromtimestamp(datetime.now().timestamp()), " Ending remoteget " + version
)
