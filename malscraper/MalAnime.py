"""
Copyright 2017 Hermann Krumrey

This file is part of mal-scraper.

mal-scraper is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

mal-scraper is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with mal-scraper.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import time
import requests
from bs4 import BeautifulSoup
from typing import Dict


class MalAnime(object):
    """
    Class that models a myanimelist anime
    """

    def __init__(self, url: str):
        """
        Generates a MalAnime object
        :param url: The anime's URL on myanimelist.net
        """
        self.url = url

        response = MalAnime.get_url_data(url)
        self.soup = BeautifulSoup(response, "html.parser")
        self.name = self.__parse_name()
        self.related = self.__parse_related()

    @staticmethod
    def get_url_data(url: str) -> str:
        sleeper = 1
        response = requests.get(url)

        while response.status_code == 429:  # Circumvent rate limiting
            time.sleep(sleeper)
            sleeper += 1
            response = requests.get(url)

        if response.status_code != 200:
            print("HTTP ERROR: " + str(response.status_code) + " " + str(url))
            sys.exit(1)

        return response.text

    def __parse_name(self) -> str:
        """
        Parses the title of the anime
        :return: The title of the name
        """
        return self.soup.select("h1")[0].text

    def __parse_related(self) -> Dict[str, str]:
        """
        Parses the URLs of related anime
        :return: A dictionary consisting of the names and the URLS
                 of the related series
        """
        related = {}
        try:
            table = self.soup.select(".anime_detail_related_anime")[0]
            for entry in table.select("a"):
                related[entry.text] = "https://myanimelist.net" + entry["href"]
        except IndexError:
            pass
        return related


class UserMalAnime(MalAnime):
    """
    Class that extends the myanimelist Anime model
    by integrating user-specific data
    """

    def __init__(self, url: str, username: str, xml_data: BeautifulSoup=None):
        super().__init__(url)
        self.username = username
        if xml_data is not None:
            self.xml_data = xml_data
        else:
            self.xml_data = get_user_xml_data(username)

        url = "https://myanimelist.net/malappinfo.php?" \
              "type=anime&status=all&u=" + self.username
        response = MalAnime.get_url_data(url)

        self.user_series_data = None
        xml_soup = BeautifulSoup(response, features="xml")
        for series in xml_soup.find_all("anime"):
            name = series.find_all("series_title")[0].text
            if name == self.name:
                self.user_series_data = series
                break

        if self.user_series_data is not None:
            self.watch_status = self.__parse_watch_status()

        else:
            self.watch_status = "not in list"

    def __parse_watch_status(self) -> str:
        state = self.user_series_data.find_all("my_status")[0].text
        try:
            return {
                1: "watching",
                2: "completed",
                3: "onhold",
                4: "dropped",
                6: "plantowatch"
            }[int(state)]
        except ValueError:
            return state


def get_user_xml_data(username: str) -> BeautifulSoup:
    """
    Retrieves the XML data for a user's anime series from the MAL API.
    :param username: The user for which to retrieve the XML data
    :return: The XML data in a BeautifulSoup parser
    """
    url = "https://myanimelist.net/malappinfo.php?" \
          "type=anime&status=all&u=" + username
    response = requests.get(url)
    while response.status_code != 200:
        time.sleep(1)
        response = requests.get(url)
    return BeautifulSoup(response.text, features="xml")
