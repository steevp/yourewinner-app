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
import xmlrpclib

#from bs4 import BeautifulSoup
from transport import RequestsTransport

class Forum:
    def __init__(self, **kwargs):
        self.url = "http://yourewinner.com/"
        self.api = xmlrpclib.ServerProxy(self.url + "mobiquo/mobiquo.php", transport=RequestsTransport())
        self.logged_in = False
        self.session_id = None
        self.session_var = None
        self.session = RequestsTransport.session

    def login(self, username, password):
        username = xmlrpclib.Binary(username)
        password = xmlrpclib.Binary(password)
        request = self.api.login(username, password)

        result = request.get("result")
        if result:
            self.logged_in = True

        return result

    def get_recent(self, page=1):

        start = str((page - 1) * 10)

        request = self.session.get(self.url + "index.php?action=recent;start=" + start)
        soup = BeautifulSoup(request.text)
        check_board_id = re.compile(r'board\=(\d+)')
        check_topic = re.compile(r'topic\=(\d+)\.msg(\d+)')

        contenthead = soup.find_all("div", class_="contenthead")
        content = soup.find_all("div", class_="content")

        recent = []

        for ch, c in zip(contenthead, content):
            post = {}
            post["username"] = ch.a.string

            for a in c.find("div", class_="topic_details").find_all("a"):
                href = a.get("href")
                board = check_board_id.search(href)
                topic = check_topic.search(href)
                if board:
                    post["board"] = check_board_id.search(href).group(1)
                    post["board_name"] = a.string
                elif topic:
                    post["topic"] = topic.group(1)
                    post["msg"] = topic.group(2)
                    post["subject"] = a.string

            post["content"] = " ".join(c.find("div", class_="list_posts").strings)
            recent.append(post)

        return recent

    def get_unread(self, page=None):
        pass

    def get_topic(self, topic, message=None, page=1, page_size=10):

        start = page * page_size - page_size
        end = page * page_size - 1

        request = self.api.get_thread(topic, start, end)
        return request

    def get_board(self, board, page=1, page_size=25, children=False):

        start = page * page_size - page_size
        end = page * page_size - 1
        
        request = self.api.get_topic(board, start, end)
        return request.get("topics")

    def get_board_index(self):
        request = self.api.get_forum()
        return request
    
    def reply(self, board, topic, subject, message):

        if not self.logged_in:
            print "You must be logged in to do that!"
            return False

        subject = xmlrpclib.Binary(subject)
        message = xmlrpclib.Binary(message)

        self.api.reply_post(board, topic, subject, message)
        return

        request = self.session.get(self.url + "index.php?action=post;topic=" + topic + ".0;wap2")

        soup = BeautifulSoup(request.text)
        subject = soup.find("input", attrs={"name": "subject"})
        # Random number used to check for double-posting
        seqnum = soup.find("input", attrs={"name": "seqnum", "type": "hidden"})

        payload = {
            "subject": subject.get("value"),
            "message": message,
            "icon": "wireless",
            "goback": "1",
            "seqnum": seqnum.get("value"),
            self.session_var: self.session_id,
            "topic": topic,
            "notify": "0"
        }

        self.session.post(self.url + "index.php?action=post2;start=0;board=" + board + ".0;wap2", data=payload)

        # I'm sure it went fine
        return True
    
    def rate_post(self, post, rating):

        if not self.logged_in:
            print "You must be logged in to do that!"
            return False

        request = self.session.get(self.url + "index.php?action=rateTopic;sesc=" + self.session_id + ";rateId=" + rating + ";postId=" + post + ";xml")
        soup = BeautifulSoup(request.text)
        ratecount = soup.find("ratecount").string
        return ratecount

