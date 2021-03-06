#!/usr/bin/env python2 
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
import os
import json
import datetime
from math import ceil

from lib.yourewinner import Forum
from lib.settingsjson import settings_json

os.environ["KIVY_IMAGE"] = "pil"

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.listview import ListView, ListItemButton
from kivy.uix.settings import SettingsWithSidebar
from kivy.uix.actionbar import ActionBar
from kivy.adapters.listadapter import ListAdapter
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.clock import mainthread

import threading

Builder.load_string("""
<RootWidget>:
    canvas.before:
        Color:
            rgba: 0.129, 0.11, 0.271, 1
        Rectangle:
            pos: self.pos
            size: self.size
    boardindex: boardindex
    boardview: boardview
    topicview: topicview
    BoardIndex:
        id: boardindex
        name: "boardindex"
    BoardView:
        id: boardview
        name: "boardview"
    TopicView:
        id: topicview
        name: "topicview"

<TopicView>:
    name: "topicview"
    forum_posts: forum_posts
    BoxLayout:
        orientation: "vertical"
        ActionBar:
            pos_hint: {'top':1}
            ActionView:
                use_separator: True
                ActionPrevious:
                    title: "Social/Off-Topic - " + root.topic_title
                    on_release: app.root.current = "boardview"
                ActionOverflow:
                #ActionButton:
                #    text: 'Btn2'
                #ActionButton:
                #    text: 'Btn3'
                #ActionButton:
                #    text: 'Btn4'
                #ActionGroup:
                #    text: 'Group1'
                #    ActionButton:
                #        text: 'Btn5'
                #    ActionButton:
                #        text: 'Btn6'
                #    ActionButton:
                #        text: 'Btn7'

        ScrollView:
            #on_scroll_y: root.refresh(self.scroll_y)
            GridLayout:
                id: forum_posts
                cols: 1
                size_hint_y: None
                height: self.minimum_height

        BoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: "40dp"
            Button:
                text: "|<"
                on_release: root.get_topic(page=1)
            Button:
                text: "<"
                on_release: root.previous_page()
            Button:
                text: str(root.current_page) + "/" + str(root.last_page)
            Button:
                text: ">"
                on_release: root.next_page()
            Button:
                text: ">|"
                on_release: root.get_topic(page=root.last_page)


<BoardIndex>:
    name: "boardindex"
    boards: boards
    BoxLayout:
        orientation: "vertical"
        ActionBar:
            pos_hint: {'top':1}
            ActionView:
                use_separator: True
                ActionPrevious:
                    title: "Social/Off-Topic - "
                ActionOverflow:
                    ActionButton:
                        text: "Settings"
                        on_release: app.open_settings()
        BoxLayout:
            orientation: "vertical"
            id: boards

<BoardView>:
    name: "boardview"
    topics: topics
    BoxLayout:
        orientation: "vertical"
        ActionBar:
            pos_hint: {'top':1}
            ActionView:
                use_separator: True
                ActionPrevious:
                    title: "Social/Off-Topic"
                    on_release: app.root.current = "boardindex"
                ActionOverflow:
                    ActionButton:
                        text: "Settings"
                        on_release: app.open_settings()

        ScrollView:
            GridLayout:
                id: topics
                cols: 1
                size_hint_y: None
                height: self.minimum_height

<PostContent>:
    canvas.after:
        Color:
            rgba: 0.051, 0.035, 0.141, 1
        Line:
            rectangle: self.x, self.y, self.width, self.height
    #background_color: 0.129, 0.11, 0.271, 1
    #deselected_color: 0.129, 0.11, 0.271, 1
    #selected_color: 0.624, 0.365, 0.094, 1
    background_normal: ""
    background_down: ""
    #on_press: self.select() if not self.is_selected else self.deselect()
    on_press: app.root.topicview.popup()
    #msg_id: ctx.msg_id
    size_hint_y: None
    height: dp(30) + image_username.height + post_content.height
    AsyncImage:
        id: image_username
        source: root.image_username
        #source: ctx.image_username
        allow_stretch: True
        keep_ratio: False
        width: '100dp'
        height: '15dp'
        x: self.parent.x + dp(30) + dp(5)
        y: self.parent.y + self.parent.height - self.height
    AsyncImage:
        canvas:
            Color:
                rgb: (1, 1, 1)
            Ellipse:
                texture: self.texture
                size: dp(30), dp(30)
                pos: self.pos
            Color:
                rgb: (0, 1, 0)
            Ellipse:
                size: (dp(5), dp(5)) if root.is_online else (0, 0)
                pos: self.x + dp(23), self.y + dp(3)
        id: avatar
        source: root.avatar
        #source: ctx.avatar
        allow_stretch: True
        keep_ratio: False
        width: 0
        height: 0
        x: self.parent.x
        y: self.parent.y + self.parent.height - dp(30)
    Label:
        id: post_content
        text: root.post_content
        markup: True
        #text: ctx.post_content
        size: self.texture_size
        text_size: self.parent.width - dp(30) - dp(10), None
        x: self.parent.x + dp(30) + dp(5)
        y: self.parent.y + self.parent.height - self.height - image_username.height - dp(5)
    Label:
        text: root.post_time
        size: self.texture_size
        x: self.parent.x + self.parent.width - self.width
        y: self.parent.y + self.parent.height - self.height

<BoardIndexButton>:
    canvas.after:
        Color:
            rgba: 0.051, 0.035, 0.141, 1
        Line:
            rectangle: self.x, self.y, self.width, self.height
    #background_color: 0.129, 0.11, 0.271, 1
    #deselected_color: 0.129, 0.11, 0.271, 1
    #selected_color: 0.624, 0.365, 0.094, 1
    background_normal: ""
    #background_down: ""
    #board_id: ctx.board_id
    text: root.board_name
    size_hint_y: None
    height: '40dp'

<BoardContent>:
    canvas.after:
        Color:
            rgba: 0.051, 0.035, 0.141, 1
        Line:
            rectangle: self.x, self.y, self.width, self.height
    #background_color: 0.129, 0.11, 0.271, 1
    #deselected_color: 0.129, 0.11, 0.271, 1
    #selected_color: 0.624, 0.365, 0.094, 1
    background_normal: ""
    #background_down: ""
    text: root.title
    topic_id: root.topic_id
    size_hint_y: None
    height: '40dp'

<ReplyPopup>:
    size_hint: (.8, .8)
    BoxLayout:
        orientation: "vertical"
        TextInput:
            id: message
            size_hint_y: .8
            multiline: True
        BoxLayout:
            orientation: "horizontal"
            size_hint_y: .2
            spacing: "5dp"
            Button:
                text: "Reply"
                on_release: app.root.topicview.reply(message.text); root.dismiss()
            Button:
                text: "Close"
                on_release: root.dismiss()

""")

class RootWidget(ScreenManager):
    pass

class TopicView(Screen):
    loaded_topic = StringProperty()
    topic_title = StringProperty()
    current_page = NumericProperty()
    last_page = NumericProperty()

    def on_pre_enter(self):
        if self.loaded_topic != self.manager.boardview.selected_topic:
            threading.Thread(target=self.get_topic).start()
    
    def get_topic(self, page=1):
        self.current_page = page
        self.loaded_topic = topic = self.manager.boardview.selected_topic
        if topic:
            recent = forum.get_topic(topic, page=page)
            self.add_posts(recent)

    @mainthread
    def add_posts(self, posts):
        self.last_page = int(ceil(posts["total_post_num"] / 10.0))
        self.topic_title = str(posts["topic_title"])
        self.forum_posts.clear_widgets()
        for p in posts["posts"]:
            pc = PostContent()
            pc.image_username = p["image_username"]
            pc.avatar = p["icon_url"]
            pc.post_content = str(p["post_content"])
            pc.is_online = p["is_online"]
            post_time = datetime.datetime.strptime(p["post_time"].value, "%Y%m%dT%H:%M:%S+00:00")
            pc.post_time =  post_time.strftime("%m-%d-%Y, %H:%M:%S")
            self.forum_posts.add_widget(pc)
        #list_item_args_converter = lambda row_index, ctx: {
        #    "image_username": ctx["image_username"],
        #    "avatar": ctx["icon_url"],
        #    "post_content": str(ctx["post_content"])
        #}
        #list_adapter = ListAdapter(data=posts["posts"], args_converter=list_item_args_converter, template="PostContent")
        #list_view = ListView(adapter=list_adapter)
        #self.forum_posts.add_widget(list_view)

    def next_page(self):
        if self.current_page < self.last_page:
            self.forum_posts.clear_widgets()
            page = self.current_page + 1
            self.get_topic(page=page)

    def previous_page(self):
        if self.current_page > 1:
            self.forum_posts.clear_widgets()
            page = self.current_page - 1
            self.get_topic(page=page)

    def popup(self, *args):
        if forum.logged_in:
            popup = ReplyPopup()
            popup.open()

    def reply(self, message):
        if not message:
            return
        board = self.manager.boardview.loaded_board
        topic = self.loaded_topic
        subject = self.topic_title
        forum.reply(board, topic, subject, message)
        self.get_topic(page=self.last_page)


class PostContent(ListItemButton):
    image_username = StringProperty()
    avatar = StringProperty()
    post_content = StringProperty()
    is_online = BooleanProperty(False)
    post_time = StringProperty()

    def select(self, *args):
        self.deselect_all()
        super(PostContent, self).select(*args)
        self.is_selected = True

    def deselect(self, *args):
        super(PostContent, self).deselect(*args)
        self.is_selected = False

    def deselect_all(self, *args):
        for c in self.parent.children:
            if c.is_selected:
                c.deselect()

class BoardContent(Button):
    title = StringProperty()
    topic_id = StringProperty()

class BoardIndex(Screen):
    selected_board = StringProperty()

    def on_pre_enter(self):
        if not self.selected_board:
            #self.boards.clear_widgets()
            threading.Thread(target=self.get_board_index).start()
    
    def get_board_index(self):
        board_index = forum.get_board_index()
        self.add_boards(board_index)

    @mainthread
    def add_boards(self, boards):
        ac = Accordion(orientation="vertical")
        for cat in boards:
            if cat["sub_only"]:
                # Category
                item = AccordionItem(background_normal="catbg.jpg", title=str(cat["forum_name"]))
                container = GridLayout(cols=1, size_hint_y=None)
                container.bind(minimum_height=container.setter("height"))

                for b in cat["child"]:
                    bib = BoardIndexButton()
                    bib.board_name = str(b["forum_name"])
                    bib.board_id = b["forum_id"]
                    bib.bind(on_release=self.open_board)
                    container.add_widget(bib)

                scrollview = ScrollView()
                scrollview.add_widget(container)

                item.add_widget(scrollview)
                ac.add_widget(item)

        self.boards.add_widget(ac)

    def open_board(self, widget):
        self.selected_board = widget.board_id
        if self.selected_board:
            self.manager.current = "boardview"

class BoardIndexButton(Button):
    board_name = StringProperty()
    board_id = StringProperty()

class BoardView(Screen):
    selected_topic = StringProperty()
    loaded_board = StringProperty()

    def on_pre_enter(self):
        if self.loaded_board != self.manager.boardindex.selected_board:
            self.topics.clear_widgets()
            threading.Thread(target=self.get_board).start()

    def get_board(self):
        self.loaded_board = board = self.manager.boardindex.selected_board
        if board:
            topics = forum.get_board(board)
            self.add_topics(topics)

    @mainthread
    def add_topics(self, topics):
        for t in topics:
            bc = BoardContent()
            title = str(t.get("topic_title"))
            topic_id = t.get("topic_id")
            if title:
                bc.title = title
            if topic_id:
                bc.topic_id = topic_id
            bc.bind(on_release=self.open_topic)
            self.topics.add_widget(bc)

    def open_topic(self, widget):
        topic_id = widget.topic_id
        if topic_id:
            self.selected_topic = topic_id
            self.manager.current = "topicview"

class ReplyPopup(Popup):
    pass

class YoureWinner(App):
    logged_in = BooleanProperty(False)

    def build(self):
        self.use_kivy_settings = False
        self.load_theme()
        self.do_login()

        return RootWidget()

    def on_pause(self):
        # save data here
        return True

    def on_resume(self):
        pass

    def build_config(self, config):
        config.setdefaults("login", {
            "username": "",
            "password": ""})
        config.setdefaults("appearance", {
            "theme": "default"})

    def build_settings(self, settings):
        settings.add_json_panel("Settings",
                                self.config,
                                data=settings_json)

    def on_config_change(self, config, section, key, value):
        self.do_login()

    def do_login(self):
        if self.logged_in:
            return

        username = str(self.config.get("login", "username"))
        password = str(self.config.get("login", "password"))

        if username and password:
            self.logged_in = forum.login(username, password)
            print self.logged_in

    def load_theme(self):
        theme = self.config.get("appearance", "theme")
        with open(os.path.join("themes", theme, "style.json"), "r") as f:
            style = json.load(f)
        ActionBar.background_image.defaultvalue = style["button_background"]
        Button.background_normal.defaultvalue = style["button_background"]
        Label.color.defaultvalue = style["text_color"]
        PostContent.background_color = style["background_color"]
        PostContent.deselected_color = style["background_color"]
        PostContent.selected_color = style["selected_color"]
        BoardIndexButton.background_color = style["background_color"]
        BoardIndexButton.deselected_color = style["background_color"]
        BoardIndexButton.selected_color = style["selected_color"]
        BoardContent.background_color = style["background_color"]
        BoardContent.deselected_color = style["background_color"]
        BoardContent.selected_color = style["selected_color"]

if __name__ == "__main__":
    forum = Forum()
    YoureWinner().run()
