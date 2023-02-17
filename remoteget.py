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


def parse_arguments():
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


def download_http(url, localpath):
    """Handles HTTP and HTTPS downloads.
    Allow following redirects for simplicity."""
    r = requests.get(url, allow_redirects=True)
    a = urlparse(url)
    #    open(os.path.basename(a.path), "wb").write(r.content)
    print(localpath + os.path.basename(a.path))
    # TODO: use open with for closing connection
    open(localpath + os.path.basename(a.path), "wb").write(r.content)


def download_ftp_creds(url, usr, pword, localpath):
    """Handles FTP (insecure) downloads with user/password.
    Should NOT be used except with 'anonymous' as username and password."""
    a = urlparse(url)
    ftp = FTP(a.netloc)  # connect to host, default port
    ftp.login(user=usr, passwd=pword)
    ftp.cwd(os.path.dirname(a.path))  # change into the specified directory
    with open(localpath + os.path.basename(a.path), "wb") as fp:
        ftp.retrbinary("RETR %s" % os.path.basename(a.path), fp.write)
    ftp.quit()


def download_ftps_creds(url, usr, pword, localpath):
    """Handles FTPS downloads with user/password credentials."""
    a = urlparse(url)
    ftps = FTP_TLS(a.netloc)  # connect to host, default port
    ftps.login(user=usr, passwd=pword)
    ftps.cwd(os.path.dirname(a.path))  # change into the specified directory
    with open(localpath + os.path.basename(a.path), "wb") as fp:
        ftps.retrbinary("RETR %s" % os.path.basename(a.path), fp.write)
    ftps.quit()


def download_sftp(url, usr, pword, localpath):
    """Handles SFTP downloads with credentials. Uses fabric."""
    a = urlparse(url)
    print(a)
    c = Connection(
        a.netloc, port=22, user=usr, connect_kwargs={"password": pword}
    )
    print(c)
    c.get(os.path.basename(a.path))
    # TODO: set local path for getting

def calc_gps_week():
    gps_epoch = date(1980, 1, 6)  # GPS week 0
    today = date.today()
    epoch_monday = gps_epoch - timedelta(gps_epoch.weekday())
    today_monday = today - timedelta(today.weekday())
    return int((today_monday - epoch_monday).days / 7)


def calc_year_yyyy():
    today = datetime.today()
    return today.strftime("%Y")


def calc_year_yy():
    today = datetime.today()
    return today.strftime("%y")


def calc_doy():
    return datetime.now().timetuple().tm_yday


# Some useful macros
macros = {
    "$DOY$": str(calc_doy()),
    "$YYYY$": str(calc_year_yyyy()),
    "$YY$": str(calc_year_yy()),
    "$GPSWEEK$": str(calc_gps_week()),
}
# Add the system environment variables to our macro collection
for name, value in os.environ.items():
    macros["$" + name + "$"] = value


def resolve_macros(macrostring):
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

# This should probably move into a function to avoid shadowing
for location in downloadlist["downloads"]:
    method = downloadlist["downloads"][location]["method"]
    url = downloadlist["downloads"][location]["url"]
    path = downloadlist["downloads"][location]["path"]
    user = downloadlist["downloads"][location]["user"]
    password = downloadlist["downloads"][location]["pass"]
    dest = downloadlist["downloads"][location]["dest"]
    print(downloadlist["downloads"][location])
    # TODO: should be replaced with Python 3.10+ match statement instead
    if method == "http" or method == "https":
        download_http(method + "://" + url + path, localpath=dest)
    elif method == "ftp":
        download_ftp_creds(method + "://" + url + path, usr=user, pword=password, localpath=dest)
    elif method == "ftps":
        download_ftps_creds(method + "://" + url + path, usr=user, pword=password, localpath=dest)
    elif method == "sftp":
        download_sftp(method + "://" + url + path, usr=user, pword=password, localpath=dest)

print(
    datetime.fromtimestamp(datetime.now().timestamp()), " Ending remoteget " + version
)
