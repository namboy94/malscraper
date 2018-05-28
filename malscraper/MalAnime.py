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

from typing import List
from malscraper.Cache import Cache
from malscraper.types.AiringState import AiringState
from malscraper.types.MediaType import MediaType


class MalAnime(object):
    """
    Class that models a myanimelist anime
    """

    def __init__(self, mal_id: int):
        """
        Generates a MalAnime object
        :param mal_id: The anime's ID on myanimelist.net
        """
        self.id = mal_id
        self.soup = Cache().load_mal_page(self.id, MediaType.ANIME)
        self.name = self.__parse_name()
        self.related_anime = self.__parse_related("anime")
        self.related_manga = self.__parse_related("manga")
        self.airing_status = self.__parse_airing_status()
        self.episode_count = self.__parse_episode_count()

    def __parse_name(self) -> str:
        """
        Parses the title of the anime
        :return: The title of the name
        """
        return self.soup.select("h1")[0].text

    def __parse_related(self, media_type: str) -> List[int]:
        """
        Parses the URLs of related anime
        :param media_type: The media type to check for (anime or manga)
        :return: A dictionary consisting of the names and the URLS
                 of the related series
        """
        related = []
        try:
            table = self.soup.select(".anime_detail_related_anime")[0]
            for entry in table.select("a"):
                path = entry["href"]
                mal_id = path.rsplit("/", 2)[1]
                if path.startswith("/" + media_type + "/"):
                    related.append(int(mal_id))

        except IndexError:
            pass
        return related

    def __parse_airing_status(self) -> AiringState:
        """
        Parses the airing status of a series
        :return: The airing status
        """
        state = \
            str(self.soup).split("Status:</span>")[1].split("</div>")[0].strip()

        for airing_type in AiringState:
            if airing_type.value == state:
                return airing_type

    def __parse_episode_count(self) -> int or None:
        """
        Parses the episode count of a series
        :return: The amount of episodes or
                 None if that information is not available
        """
        eps = str(self.soup).split("Episodes:</span>")[1].split("</div>")[0]\
            .strip()
        try:
            return int(eps)
        except ValueError:
            return None
