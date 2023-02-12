# Download a series of files for AutoBernese
# Parameters: -d, downloads file (YAML). See example.
# Can evaluate day of year and gpsweek for macro resolution
# Lars Næsbye Christensen, 2023

import argparse
import requests
import os
import yaml

from datetime import date, timedelta, datetime
from ftplib import FTP
from urllib.parse import urlparse

# Constants and globals
version = "0.5"
gps_epoch = date(1980, 1, 6)  # GPS week 0
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
    """Handles HTTP and HTTPS downloads"""
    r = requests.get(url, allow_redirects=True)
    a = urlparse(url)
    open(os.path.basename(a.path), "wb").write(r.content)


def download_ftp_anon(url):
    """Handles anonymous FTP downloads"""
    a = urlparse(url)
    ftp = FTP(url)  # connect to host, default port
    ftp.login()  # user anonymous, password anonymous
    ftp.cwd("debian")  # change into "debian" directory
    with open("README", "wb") as fp:
        ftp.retrbinary("RETR README", fp.write)
    ftp.quit()


def download_ftp_creds(url):
    """Handles FTP downloads with credentials"""
    return 0  # placeholder


def download_ftps_creds(url):
    """Handles FTPS downloads with credentials"""
    return 0  # placeholder


def download_sftp(url):
    """Handles SFTP downloads with credentials"""
    return 0  # placeholder


def load_credentials(credsfile):
    global creds
    with open(credsfile) as c:
        creds = yaml.load(c, Loader=yaml.FullLoader)


def calc_gps_week():
    today = date.today()
    epoch_monday = gps_epoch - timedelta(gps_epoch.weekday())
    today_monday = today - timedelta(today.weekday())
    return (today_monday - epoch_monday).days / 7


def calc_year_yyyy():
    today = datetime.today()
    return today.strftime("%Y")


def calc_year_yy():
    today = datetime.today()
    return today.strftime("%y")


def calc_doy():
    return datetime.now().timetuple().tm_yday


print(
    datetime.fromtimestamp(datetime.now().timestamp()), " Starting remoteget " + version
)
parse_arguments()
print("Day of year: " + str(calc_doy()))
print("Year: " + str(calc_year_yyyy()) + " " + str(calc_year_yy()))
print("GPS week: " + str(calc_gps_week()))

with open(args.downloadpath) as f:
    downloadlist = yaml.load(f, Loader=yaml.FullLoader)
    # print(downloadlist)


load_credentials(downloadlist["credentials"])
print(
    datetime.fromtimestamp(datetime.now().timestamp()), " Ending remoteget " + version
)
