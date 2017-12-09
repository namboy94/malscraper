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
        self.soup = BeautifulSoup(requests.get(url).text, "html.parser")

        self.name = self.__parse_name()
        self.related = self.__parse_related()

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
        table = self.soup.select(".anime_detail_related_anime")[0]
        for entry in table.select("a"):
            related[entry.text] = "https://myanimelist.net" + entry["href"]
        return related


class UserMalAnime(MalAnime):
    """
    Class that extends the myanimelist Anime model
    by integrating user-specific data
    """

    def __init__(self, url: str, username: str):
        super().__init__(url)
        self.username = username
        self.user_series = {}

        xmldata = requests.get("https://myanimelist.net/malappinfo.php?"
                               "type=anime&status=all&u=" + self.username).text
        with open("/tmp/maldata.xml", 'w') as f:
            f.write(xmldata)

        self.userdata = None
        xml_soup = BeautifulSoup(xmldata, features="xml")
        for series in xml_soup.find_all("anime"):
            name = series.find_all("series_title")[0].text
            if name == self.name:
                self.userdata = series
                break

        if self.userdata is not None:
            self.watch_status = self.__parse_watch_status()
            print(self.watch_status)

        else:
            self.watch_status = None

    def __parse_watch_status(self) -> str:
        state = self.userdata.find_all("my_status")[0].text
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
