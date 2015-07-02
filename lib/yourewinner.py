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

        #payload = {
        #    "user": username,
        #    "passwrd": password,
        #    "cookieneverexp": "1"
        #}
    
        #request = self.session.post(self.url + "index.php?action=login2;wap2", data=payload)
        #
        #check_login = re.search(r'action\=logout\;(\w+)\=(\w+)', request.text)

        #if check_login:
        #    self.logged_in = True
        #    self.session_var = check_login.group(1)
        #    self.session_id = check_login.group(2)
        #else:
        #    self.logged_in = False
        #    self.session_var = None
        #    self.session_id = None
        #
        #return self.logged_in

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

    def get_topic(self, topic, message=None, page=1):

        start = page * 10 - 10
        end = page * 10 - 1

        request = self.api.get_thread(topic, start, end)
        return request
        
        if page:
            if self.logged_in:
                topic = topic + "." + str((page - 1) * 50)
            else:
                # Smaller page size for guests
                topic = topic + "." + str((page - 1) * 15)
        elif message:
            topic = topic + "." + message

        request = self.session.get(self.url + "?topic=" + topic + ";topicseen")
        soup = BeautifulSoup(request.text)
        check_msg_id = re.compile(r'msg(\d+)')
        
        title = soup.title.string.split(" - ")[1:]
        forumposts = soup.find(id="forumposts")
        contenthead = forumposts.find_all(class_="contenthead")
        subject = forumposts.find_all(id=re.compile(r'^subject_\d+$'))
        content = forumposts.find_all(id=re.compile(r'^msg_\d+$'))
        posterinfo = forumposts.find_all(class_="posterinfo")
        
        topic = {
            "title": title,
            "id": topic,
            "posts": [],
            "page": page
        }

        for ch, pi, s, c in zip(contenthead, posterinfo, subject, content):
            post = {}

            if ch.a.img is None:
                post["image_username"] = None
                post["username"] = ch.a.string
            else:
                post["image_username"] = self.url + ch.a.img.get("src")[2:]
                post["username"] = ch.a.img.get("alt")
            
            avatar = pi.find("img", class_="avatar")
            if avatar:
                post["avatar"] = avatar.get("src")
            else:
                post["avatar"] = None
            
            href = s.a.get("href")
            msg_id = check_msg_id.search(href)
            if msg_id:
                post["msg_id"] = msg_id.group(1)

            post["content"] = " ".join(c.strings)

            topic["posts"].append(post)

        return topic

    def get_board(self, board, page=1, children=False):
        request = self.api.get_topic(board, 0, 25)
        return request.get("topics")

        #board = "{0}.{1}".format(board, str((page - 1) * 50))
        #request = self.session.get(self.url + "index.php?board=" + board)
        #soup = BeautifulSoup(request.text)
        #check_topic = re.compile(r'topic\=(\d+)')
        #check_profile = re.compile(r'action\=profile\;u\=(\d+)')
        #check_replies = re.compile(r'(\d+) Replies')
        #check_views = re.compile(r'(\d+) Views')
        #posts = []

        #thread_row = soup.find_all("tr", class_="threadrow")
        #for tr in thread_row:
        #    post = {}
        #    thread_icon = tr.find("td", class_="threadicon2").img
        #    thread_info = tr.find("td", class_="threadinfo")
        #    thread_stats = tr.find("td", class_="threadstats")
        #    post["icon"] = thread_icon.get("src")
        #    for a in thread_info.find_all("a"):
        #        class_ = a.get("class")
        #        if class_:
        #            if "navPages" in class_:
        #                continue
        #        href = a.get("href")
        #        topic = check_topic.search(href)
        #        profile = check_profile.search(href)
        #        if topic:
        #            post["topic_id"] = topic.group(1)
        #            post["title"] = a.string
        #        elif profile:
        #            post["username"] = a.string
        #            post["user_id"] = profile.group(1)
        #    for ts in thread_stats.strings:
        #        replies = check_replies.search(ts)
        #        views = check_views.search(ts)
        #        if replies:
        #            post["replies"] = check_replies.search(ts).group(1)
        #        elif views:
        #            post["views"] = check_views.search(ts).group(1)
        #    posts.append(post)

        #return posts

    def get_board_index(self):
        request = self.api.get_forum()
        return request

        #request = self.session.get(self.url + "index.php?wap2")
        #soup = BeautifulSoup(request.text)
        #check_board_id = re.compile(r'board\=(\d+)')
        #boards = {}

        ## Current category
        #cat = "Uncategorized"
        #for a in soup.find_all("a"):
        #    href = a.get("href")
        #    if "?action=collapse" in href:
        #        # Must be a new category
        #        cat = a.string
        #        boards[cat] = []
        #    elif "?board=" in href:
        #        board_id = check_board_id.search(href)
        #        if board_id:
        #            board = {
        #                "name": a.string,
        #                "id": board_id.group(1)
        #            }
        #            boards[cat].append(board)

        #return boards
    
    def reply(self, board, topic, message):

        if not self.logged_in:
            print "You must be logged in to do that!"
            return False

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

