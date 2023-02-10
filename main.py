# Download a series of files for AutoBernese
# Parameters: credentials file, downloads file
# Can evaluate day of year and gpsweek for macro resolution
# LANCH, 2023

import yaml
import requests
import argparse
import os

from datetime import date, timedelta, datetime
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
    parser.add_argument("d", help="path to file containing download locations", type=str)
    args = parser.parse_args()
    return 0 # placeholder


def download_http(url):
    r = requests.get(url, allow_redirects=True)
    a = urlparse(url)
    open(os.path.basename(a.path), 'wb').write(r.content) # 
    return 0  # placeholder


def download_ftp(url):
    return 0  # placeholder


def download_ftps(url):
    return 0  # placeholder


def download_sftp(url):
    return 0  # placeholder


def load_credentials(credsfile):
    global creds
    with open(credsfile) as c:
        creds = yaml.load(c, Loader=yaml.FullLoader)


def calc_gps_week():
    epoch = date(1980, 1, 6)
    today = date.today()
    epochMonday = epoch - timedelta(epoch.weekday())
    todayMonday = today - timedelta(today.weekday())
    return (todayMonday - epochMonday).days / 7


def calc_doy():
    return datetime.now().timetuple().tm_yday


print("--- Starting remoteget version " + version + " ---")
parse_arguments()
print(args)
print("GPS week: " + str(calc_gps_week()))
print("Day of year: " + str(calc_doy()))
load_credentials("credentials.yaml")
print(creds)

with open("downloadlist.yaml") as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
    print(data)
