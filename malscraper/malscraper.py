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

from malscraper.MalAnime import MalAnime, UserMalAnime


def main():
    MalAnime("https://myanimelist.net/anime/33486/"
             "Boku_no_Hero_Academia_2nd_Season")
    UserMalAnime("https://myanimelist.net/anime/33486/"
                 "Boku_no_Hero_Academia_2nd_Season", "user_v42-1337")


if __name__ == "__main__":
    main()
