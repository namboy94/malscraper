import os
import sys
import time
import requests
from bs4 import BeautifulSoup


class Cache:
    """
    Class that handles fetching and caching of myanimelist data
    """

    flush_time = 86400  # Keep data for one day
    """
    Specifies the flush time for the cached data
    """

    def __init__(self):
        """
        Initializes the cache directories
        """

        self.cache_dir = os.path.join(os.path.expanduser("~"), ".malscraper")
        self.anime_cache_dir = os.path.join(self.cache_dir, "anime")
        self.manga_cache_dir = os.path.join(self.cache_dir, "manga")
        self.user_cache_dir = os.path.join(self.cache_dir, "users")

        for directory in [self.anime_cache_dir, self.manga_cache_dir,
                          self.user_cache_dir]:
            if not os.path.isdir(directory):
                os.makedirs(directory)

    def load_anime_page(self, mal_id: int) -> BeautifulSoup:
        """
        Loads an anime's myanimelist page
        :param mal_id: The ID of the anime
        :return: The HTML anime data
        """
        anime_cache_file = os.path.join(self.anime_cache_dir, str(mal_id))
        if self._needs_refresh(anime_cache_file):
            url = "https://myanimelist.net/anime/" + str(mal_id)
            data = self._get_url_data(url)
            with open(anime_cache_file, "w") as f:
                f.write(data)
        else:
            with open(anime_cache_file, "r") as f:
                data = f.read()

        return BeautifulSoup(data, "html.parser")

    def load_manga_page(self, mal_id: int) -> BeautifulSoup:
        """
        Loads an manga's myanimelist page
        :param mal_id: The ID of the manga
        :return: The HTML anime data
        """
        manga_cache_file = os.path.join(self.manga_cache_dir, str(mal_id))
        if self._needs_refresh(manga_cache_file):
            url = "https://myanimelist.net/manga/" + str(mal_id)
            data = self._get_url_data(url)
            with open(manga_cache_file, "w") as f:
                f.write(data)
        else:
            with open(manga_cache_file, "r") as f:
                data = f.read()

        return BeautifulSoup(data, "html.parser")

    def load_user_xml(self, username: str) -> BeautifulSoup:
        """
        Loads a user's XML data
        :param username: The username to fetch the data for
        :return: The XML user data
        """
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

        return BeautifulSoup(data, features="xml")

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
