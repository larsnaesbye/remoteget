# Download a series of files for AutoBernese
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


def download_http(url):
    """Handles HTTP and HTTPS downloads."""
    r = requests.get(url, allow_redirects=True)
    a = urlparse(url)
    open(os.path.basename(a.path), "wb").write(r.content)


def download_ftp_anon(url):
    """Handles anonymous FTP downloads."""
    a = urlparse(url)
    ftp = FTP(a.netloc)  # connect to host, default port
    ftp.login()  # user anonymous, password anonymous
    ftp.cwd(os.path.dirname(a.path))  # change into the specified directory
    with open(os.path.basename(a.path), "wb") as fp:
        ftp.retrbinary("RETR %s" % os.path.basename(a.path), fp.write)
    ftp.quit()


def download_ftp_creds(url, usr, pword):
    """Handles FTP (insecure) downloads with user/password. Should actually NOT be used."""
    a = urlparse(url)
    ftp = FTP(a.netloc)  # connect to host, default port
    ftp.login(user=usr, passwd=pword)
    ftp.cwd(os.path.dirname(a.path))  # change into the specified directory
    with open(os.path.basename(a.path), "wb") as fp:
        ftp.retrbinary("RETR %s" % os.path.basename(a.path), fp.write)
    ftp.quit()


def download_ftps_creds(url, usr, pword):
    """Handles FTPS downloads with user/password credentials."""
    a = urlparse(url)
    ftps = FTP_TLS(a.netloc)  # connect to host, default port
    ftps.login(user=usr, passwd=pword)
    ftps.cwd(os.path.dirname(a.path))  # change into the specified directory
    with open(os.path.basename(a.path), "wb") as fp:
        ftps.retrbinary("RETR %s" % os.path.basename(a.path), fp.write)
    ftps.quit()


def download_sftp(url):
    """Handles SFTP downloads with credentials. Uses fabric."""
    with Connection(url) as c:
        c.get('file')


def load_credentials(credsfile):
    global creds
    with open(credsfile) as c:
        creds = yaml.load(c, Loader=yaml.FullLoader)


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

parse_arguments()  # parse arguments. Only one for now, d for download list

# Using the download list argument, we load the YAML file specifying files to download and how
with open(args.downloadpath) as f:
    downloadlist = yaml.load(f, Loader=yaml.FullLoader)

for location in downloadlist["downloads"]:
    method = downloadlist["downloads"][location]["method"]
    url = downloadlist["downloads"][location]["url"]
    path = downloadlist["downloads"][location]["path"]
    creds = downloadlist["downloads"][location]["creds"]
    dest = downloadlist["downloads"][location]["dest"]
    # should be replaced with Python 3.10 match statement instead
    if method == "http":
        download_http(url)
    elif method == "ftp":
        download_ftp_anon(url)
    elif method == "ftps":
        download_ftps_creds(url, usr=creds, pword=creds)
    elif method == "sftp":
        download_sftp(url)


load_credentials(downloadlist["credentials"])

# download_ftp_anon("ftp://ftp.cs.brown.edu/u/ag/giotto3d/btree-print.ps.gz") # this works in ordinary FTP clients
# download_ftp_creds(
#   "ftp://ftp.cs.brown.edu/u/ag/giotto3d/btree-print.ps.gz", "anonymous", "anonymous"
# )

print(
    datetime.fromtimestamp(datetime.now().timestamp()), " Ending remoteget " + version
)
