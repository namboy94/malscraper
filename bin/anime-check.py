#!/usr/bin/env python

import os
import sys
from copy import copy
from typing import List

from toktokkie.utils.metadata.media_types.AnimeSeries import AnimeSeries
from toktokkie.utils.metadata.MetaDataManager import MetaDataManager
from malscraper.MalAnime import UserMalAnime, get_user_xml_data


def check_watch_status(maldata: UserMalAnime) -> bool:
    if maldata.watch_status == "onhold":
        print("\033[33m" + maldata.name + " is on hold\033[0m")
        return False
    elif maldata.watch_status != "completed":
        print("\033[31m" + maldata.name + " is not completed (" +
              str(maldata.watch_status) + ")\033[0m")
    return True


def check_for_url(url: str, series: AnimeSeries):
    urls = get_urls_from_series(series)
    id_url = "https://myanimelist.net/anime.php?id=" + \
             url.split("/anime/")[1].split("/")[0]

    if url in urls or id_url in urls:
        pass  # OK
    else:
        print("\033[36mMAL URL missing: " + url + "\033[0m")


def get_urls_from_series(series: AnimeSeries) -> List[str]:
    urls = []
    metadata = copy(series)
    for season in series.seasons:
        metadata.set_child_extender("seasons", season)
        urls.append(metadata.myanimelist_url)
    return urls


def check_directory(directory: str, username: str):

    series = AnimeSeries(directory)
    xmldata = get_user_xml_data(username)
    maldata = UserMalAnime(series.myanimelist_url, username, xmldata)

    check_watch_status(maldata)

    for title, url in maldata.related.items():

        if "/manga/" in url:  # Skip manga
            continue

        related_maldata = UserMalAnime(url, username, xmldata)

        if not check_watch_status(related_maldata):
            continue

        check_for_url(url, series)


def main():
    username = "user_v42-1337"
    path = sys.argv[1]
    series = MetaDataManager.find_recursive_media_directories(path, "anime_series")
    for s in series:
        print(s)
        check_directory(s, username)


if __name__ == "__main__":
    main()
