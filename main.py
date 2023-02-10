# Download a series of files for AutoBernese
# Parameters: credentials file, downloads file
# Can evaluate day of year and gpsweek for macro resolution
# LANCH, 2023

import argparse
import requests
import os
import yaml

from datetime import date, timedelta, datetime
from ftplib import FTP
from urllib.parse import urlparse

# Constants
version = "0.5"

credsfile = "credentials.yaml"
args = []
creds = []


def parse_arguments():
    global args
    parser = argparse.ArgumentParser("remoteget")
    parser.add_argument("c", help="path to file containing credentials", type=str)
    parser.add_argument(
        "d", help="path to file containing download locations", type=str
    )
    args = parser.parse_args()
    return 0  # placeholder


def download_http(url):
    """Handles HTTP and HTTPS downloads"""
    r = requests.get(url, allow_redirects=True)
    a = urlparse(url)
    open(os.path.basename(a.path), "wb").write(r.content)


def download_ftp_anon(url):
    """Handles anonymous FTP downloads"""
    ftp = FTP(url)  # connect to host, default port
    ftp.login()  # user anonymous, passwd anonymous@
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
    epoch = date(1980, 1, 6)
    today = date.today()
    epoch_monday = epoch - timedelta(epoch.weekday())
    today_monday = today - timedelta(today.weekday())
    return (today_monday - epoch_monday).days / 7


def calc_doy():
    return datetime.now().timetuple().tm_yday


print("--- Starting remoteget version " + version + " ---")
parse_arguments()

print("GPS week: " + str(calc_gps_week()))
print("Day of year: " + str(calc_doy()))
load_credentials(credsfile)

with open("downloadlist.yaml") as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
    print(data)
