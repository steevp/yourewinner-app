#    yourewinner.com forum app
#    Copyright (C) 2015 steev
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import requests
from bs4 import BeautifulSoup

class Forum:
    def __init__(self, **kwargs):
        self.url = "http://yourewinner.com/"
        self.logged_in = False
        self.session_id = None
        self.session_var = None
        self.session = requests.Session()

    def login(self, username, password):

        payload = {
            "user": username,
            "passwrd": password,
            "cookieneverexp": "1"
        }
    
        request = self.session.post(self.url + "index.php?action=login2;wap2", data=payload)
        
        check_login = re.search(r'action\=logout\;(\w+)\=(\w+)', request.text)

        if check_login:
            self.logged_in = True
            self.session_var = check_login.group(1)
            self.session_id = check_login.group(2)
        else:
            self.logged_in = False
            self.session_var = None
            self.session_id = None
        
        return self.logged_in

    def get_recent(self, page=None):
        pass

    def get_unread(self, page=None):
        pass

    def get_topic(self, topic, message=None, page=None):
        request = self.session.get(self.url + "?topic=" + topic + ";topicseen")
        soup = BeautifulSoup(request.text)
        
        posts = soup.find(id="forumposts")
        contenthead = posts.find_all(class_="contenthead")
        content = posts.find_all(id=re.compile(r'^msg_\d+$'))
        posterinfo = posts.find_all(class_="posterinfo")
        
        topic = {
            "title": "",
            "id": topic,
            "posts": [],
            "page": page
        }

        for ch, c in zip(contenthead, content):
            post = {}

            if ch.a.img is None:
                post["image_username"] = None
                post["username"] = ch.a.string
            else:
                post["image_username"] = self.url + ch.a.img.get("src")[1:]
                post["username"] = ch.a.img.get("alt")
            
            post["content"] = " ".join(c.strings)

            topic["posts"].append(post)

        return topic

    def get_board(self, board, page=None):
        pass

    def get_board_index(self):
        request = self.session.get(self.url + "index.php?wap2")
        soup = BeautifulSoup(request.text)
        check_board_id = re.compile(r'board\=(\d+)')
        boards = {}

        # Current category
        cat = "Uncategorized"
        for a in soup.find_all("a"):
            href = a.get("href")
            if "?action=collapse" in href:
                # Must be a new category
                cat = a.string
                boards[cat] = []
            elif "?board=" in href:
                board_id = check_board_id.search(href)
                if board_id:
                    board = {
                        "name": a.string,
                        "id": board_id.group(1)
                    }
                    boards[cat].append(board)

        return boards
    
    def reply(self, topic, message):
        pass
