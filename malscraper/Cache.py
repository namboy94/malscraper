"""LICENSE
Copyright 2017 Hermann Krumrey <hermann@krumreyh.com>

This file is part of malscraper.

malscraper is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

malscraper is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with malscraper.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from malscraper.types.MediaType import MediaType


class Cache:
    """
    Class that handles fetching and caching of myanimelist data
    """

    initialized = False
    """
    Global initialized variable set to true the first time the
    constructor is called
    """

    in_memory = {
        MediaType.ANIME.value: {},
        MediaType.MANGA.value: {},
        "users": {}
    }
    """
    In-Memory cache
    """

    flush_time = 86400  # Keep data for one day
    """
    Specifies the flush time for the cached data
    """

    def __init__(self, preload: bool = False):
        """
        Initializes the cache directories
        :param preload: Preloads the current cache into memory
        """

        self.cache_dir = os.path.join(os.path.expanduser("~"), ".malscraper")
        self.anime_cache_dir = os.path.join(self.cache_dir, "anime")
        self.manga_cache_dir = os.path.join(self.cache_dir, "manga")
        self.user_cache_dir = os.path.join(self.cache_dir, "users")

        for directory in [self.anime_cache_dir, self.manga_cache_dir,
                          self.user_cache_dir]:
            if not os.path.isdir(directory):
                os.makedirs(directory)

            if preload and not Cache.initialized:

                for element in os.listdir(directory):  # Load cached files

                    if directory == self.anime_cache_dir:
                        media_type = MediaType.ANIME
                    elif directory == self.manga_cache_dir:
                        media_type = MediaType.MANGA
                    else:
                        media_type = None

                    if media_type is not None:
                        element_id = int(element)
                        self.load_mal_page(element_id, media_type)

                    else:
                        self.load_user_xml(element)

                Cache.initialized = True

    def load_mal_page(self, mal_id: int, media_type: MediaType):
        """
        Loads a myanimelist page
        :param mal_id: The ID of the anime/manga
        :param media_type: The type of media to load
        :return: The HTML data
        """

        if mal_id in Cache.in_memory[media_type.value]:
            return Cache.in_memory[media_type.value][mal_id]

        else:
            if media_type == MediaType.ANIME:
                cache_dir = self.anime_cache_dir
            elif media_type == MediaType.MANGA:
                cache_dir = self.manga_cache_dir
            else:
                print("Invalid Media Type")
                sys.exit(1)

            cache_file = os.path.join(cache_dir, str(mal_id))

            if self._needs_refresh(cache_file):
                url = "https://myanimelist.net/" + media_type.value + "/"
                url += str(mal_id)
                data = self._get_url_data(url)
                with open(cache_file, "w") as f:
                    f.write(data)
            else:
                with open(cache_file, "r") as f:
                    data = f.read()

            generated = BeautifulSoup(data, "html.parser")
            Cache.in_memory[media_type.value][mal_id] = generated
            return generated

    def load_user_xml(self, username: str) -> BeautifulSoup:
        """
        Loads a user's XML data
        :param username: The username to fetch the data for
        :return: The XML user data
        """

        if username in Cache.in_memory["users"]:
            return Cache.in_memory["users"][username]

        else:

            user_cache_file = os.path.join(self.user_cache_dir, username)
            if self._needs_refresh(user_cache_file):
                url = "https://myanimelist.net/malappinfo.php?" \
                      "type=anime&status=all&u=" + username
                data = self._get_url_data(url)
                with open(user_cache_file, "w") as f:
                    f.write(data)

            else:
                with open(user_cache_file, "r") as f:
                    data = f.read()

            generated = BeautifulSoup(data, features="xml")
            Cache.in_memory["users"][username] = generated
            return generated

    @staticmethod
    def _needs_refresh(file_path: str) -> float:
        """
        Checks if a cache file needs to be updated
        :param file_path: The path to the file to check
        :return: The timestamp at which the file was last modified
        """
        if os.path.isfile(file_path):
            age = os.stat(file_path).st_mtime
            return time.time() - age > Cache.flush_time
        else:
            return True

    @staticmethod
    def _get_url_data(url: str) -> str:
        """
        Retrieves the data from the URL while circumventing rate limiting
        :param url: The URL from which to fetch data
        :return: The retrieved HTML text
        """
        sleeper = 1
        response = requests.get(url)

        while response.status_code != 200:  # Circumvent rate limiting

            print(response.status_code)

            time.sleep(sleeper)
            sleeper += 1
            response = requests.get(url)

            if sleeper > 30:
                print("Timeout: " + url)
                sys.exit(1)

        return response.text
