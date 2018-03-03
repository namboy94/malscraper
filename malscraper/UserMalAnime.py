"""
Copyright 2017-2018 Hermann Krumrey

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

from typing import List
from datetime import datetime
from malscraper.Cache import Cache
from malscraper.MalAnime import MalAnime
from malscraper.types.WatchState import WatchState


class UserMalAnime(MalAnime):
    """
    Class that extends the myanimelist Anime model
    by integrating user-specific data
    """

    def __init__(self, mal_id: int, username: str):
        """
        Initializes a user-enabled MAL Anime object
        :param mal_id: The ID of the series on MAL
        :param username: The username of the user on MAL
        """
        super().__init__(mal_id)
        self.username = username
        self.xml_data = Cache().load_user_xml(username)

        self.user_series_data = None
        for series in self.xml_data.find_all("anime"):
            name = series.find_all("series_title")[0].text
            if name == self.name:
                self.user_series_data = series
                break

        if self.user_series_data is not None:
            self.watch_status = self.__parse_watch_status()
            self.tags = self.__parse_tags()
            self.start_watching_date = self.__parse_start_watching_date()
            self.finish_watching_date = self.__parse_finish_watching_date()
            self.episodes_watched_count = self.__parse_episodes_watched_count()
        else:
            self.watch_status = WatchState.NOT_IN_LIST
            self.tags = []
            self.start_watching_date = None
            self.finish_watching_date = None
            self.episodes_watched_count = 0

    def __parse_watch_status(self) -> WatchState:
        """
        Parses the watch status of a series
        :return: The watch status
        """
        state = int(self.user_series_data.find_all("my_status")[0].text)
        for enum_state in WatchState:
            if enum_state.value == state:
                return enum_state
        raise ValueError("No valid state: " + str(state))

    def __parse_tags(self) -> List[str]:
        """
        Parses the user-specified tags of an anime
        :return: A list of tags
        """
        tags = self.user_series_data.find_all("my_tags")[0].text.split(",")
        return list(filter(lambda x: x != "", tags))

    def __parse_start_watching_date(self) -> datetime:
        """
        Parses the start date of an anime watched by the user
        :return: The start date of watching this anime
        """
        date = self.user_series_data.find_all("my_start_date")[0].text
        return self.__parse_date(date)

    def __parse_finish_watching_date(self) -> datetime:
        """
        Parses the finish date of an anime watched by the user
        :return: The finish date of watching this anime
        """
        date = self.user_series_data.find_all("my_finish_date")[0].text
        return self.__parse_date(date)

    def __parse_episodes_watched_count(self) -> int:
        """
        Parses the amount of watched episodes for this series
        :return: The amount of watched episodes
        """
        return \
            int(self.user_series_data.find_all("my_watched_episodes")[0].text)

    @staticmethod
    def __parse_date(datestring: str) -> datetime or None:
        """
        Parses a date string into a datetime object
        :param datestring: The date string to parse
        :return: The datetime object
        """
        try:
            return datetime.strptime(datestring, "%Y-%m-%d")
        except ValueError:
            try:
                return datetime.strptime(datestring, "%Y-%m-00")
            except ValueError:
                try:
                    return datetime.strptime(datestring, "%Y-00-00")
                except ValueError:
                    return None
