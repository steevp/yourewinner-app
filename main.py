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

from lib.yourewinner import Forum

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListView, SelectableView, ListItemButton
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivy.clock import mainthread
from kivy.graphics.vertex_instructions import Ellipse

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
    forum_posts: forum_posts
    BoxLayout:
        orientation: "vertical"
        ActionBar:
            pos_hint: {'top':1}
            ActionView:
                use_separator: True
                background_image: "catbg.jpg"
                ActionPrevious:
                    title: 'Social/Off-Topic'
                    on_release: app.root.current = "boardindex"
                ActionOverflow:
                ActionButton:
                    text: 'Btn0'
                    icon: 'atlas://data/images/defaulttheme/audio-volume-high'
                ActionButton:
                    text: 'Btn1'
                ActionButton:
                    text: 'Btn2'
                ActionButton:
                    text: 'Btn3'
                ActionButton:
                    text: 'Btn4'
                ActionGroup:
                    text: 'Group1'
                    ActionButton:
                        text: 'Btn5'
                    ActionButton:
                        text: 'Btn6'
                    ActionButton:
                        text: 'Btn7'

        ScrollView:
            GridLayout:
                id: forum_posts
                cols: 1
                size_hint_y: None
                height: self.minimum_height

        #BoxLayout:
        #    orientation: "horizontal"
        #    size_hint_y: None
        #    height: 32
        #    TextInput:
        #        multiline: False
        #        hint_text: "Quick Reply"
        #    Button:
        #        text: "Post"
        #        size_hint_x: None
        #        width: self.texture_size[0] + 15
        #        background_normal: "catbg.jpg"

<BoardIndex>:
    boards: boards
    BoxLayout:
        pos_hint: {'top': 1}
        id: boards
        canvas.before:
            Color:
                rgba: 0.129, 0.11, 0.271, 1
            Rectangle:
                pos: self.pos
                size: self.size

<BoardView>:
    topics: topics
    ScrollView:
        GridLayout:
            id: topics
            cols: 1
            size_hint_y: None
            height: self.minimum_height

<ListItemButton>:
    canvas.after:
        Color:
            rgba: 0.051, 0.035, 0.141, 1
        Line:
            rectangle: self.x, self.y, self.width, self.height
    background_color: 0.129, 0.11, 0.271, 1
    deselected_color: 0.129, 0.11, 0.271, 1
    selected_color: 0.624, 0.365, 0.094, 1
    background_normal: ""
    background_down: ""
    size_hint_y: None
    height: '40dp'

<PostContent>:
    canvas.after:
        Color:
            rgba: 0.051, 0.035, 0.141, 1
        Line:
            rectangle: self.x, self.y, self.width, self.height
    background_color: 0.129, 0.11, 0.271, 1
    deselected_color: 0.129, 0.11, 0.271, 1
    selected_color: 0.624, 0.365, 0.094, 1
    background_normal: ""
    background_down: ""
    #msg_id: ctx.msg_id
    size_hint_y: None
    height: avatar.height + image_username.height + post_content.height
    AsyncImage:
        id: image_username
        source: root.image_username
        allow_stretch: True
        keep_ratio: False
        width: '100dp'
        height: '15dp'
        x: self.parent.x + avatar.width + 5
        y: self.parent.y + self.parent.height - self.height
    CircleAvatar:
        id: avatar
        source: root.avatar
        allow_stretch: True
        keep_ratio: False
        width: '25dp'
        height: '25dp'
        x: self.parent.x
        y: self.parent.y + self.parent.height - self.height
    Label:
        id: post_content
        text: root.post_content
        size: self.texture_size
        text_size: self.parent.width - avatar.width - 10, None
        x: self.parent.x + avatar.width + 5
        y: self.parent.y + self.parent.height - self.height - image_username.height - 5

<BoardIndexButton>:
    canvas.after:
        Color:
            rgba: 0.051, 0.035, 0.141, 1
        Line:
            rectangle: self.x, self.y, self.width, self.height
    background_color: 0.129, 0.11, 0.271, 1
    deselected_color: 0.129, 0.11, 0.271, 1
    selected_color: 0.624, 0.365, 0.094, 1
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
    background_color: 0.129, 0.11, 0.271, 1
    deselected_color: 0.129, 0.11, 0.271, 1
    selected_color: 0.624, 0.365, 0.094, 1
    background_normal: ""
    #background_down: ""
    text: root.title
    topic_id: root.topic_id
    size_hint_y: None
    height: '40dp'
""")

# Draws the avatars in an circle
class CircleAvatar(AsyncImage):
    def __init__(self, **kwargs):
        self.circle = None
        super(CircleAvatar, self).__init__(**kwargs)

    def _on_source_load(self, value):
        image = self._coreimage.image
        if image:
            with self.canvas.after:
                self.circle = Ellipse(texture=image.texture, pos=self.pos, size=self.size)
    
    def _on_tex_change(self, *largs):
        if self._coreimage and self.circle:
            self.circle.texture = self._coreimage.texture

    def on_pos(self, obj, new_pos):
        if self.circle:
            self.circle.pos = new_pos

    def on_size(self, obj, new_size):
        if self.circle:
            self.circle.size = new_size

class RootWidget(ScreenManager):
    pass

class TopicView(Screen):
    loaded_topic = StringProperty(None)

    def on_pre_enter(self):
        if self.loaded_topic != self.manager.boardview.selected_topic:
            self.forum_posts.clear_widgets()
            threading.Thread(target=self.get_recent).start()
    
    def get_recent(self, page=1):
        self.loaded_topic = topic = self.manager.boardview.selected_topic
        if topic:
            recent = forum.get_topic(topic, page=page)
            self.add_posts(recent)

    @mainthread
    def add_posts(self, posts):
        for p in posts["posts"][:10]:
            pc = PostContent()
            image_username = p.get("image_username")
            avatar = p.get("icon_url")
            post_content = str(p.get("post_content"))
            if image_username:
                pc.image_username = image_username
            if avatar:
                pc.avatar = avatar
            if post_content:
                pc.post_content = post_content
            self.forum_posts.add_widget(pc)
        #data = posts["posts"]
        #args_converter = lambda row_index, ctx: {
        #    "image_username": ctx["image_username"],
        #    "avatar": ctx["avatar"],
        #    "post_content": ctx["content"],
        #    "msg_id": ctx["msg_id"]
        #}
        #list_adapter = ListAdapter(data=data, args_converter=args_converter, template="PostContent")
        #list_adapter.bind(on_selection_change=self.callback)
        #list_view = ListView(adapter=list_adapter)
        #self.forum_posts.add_widget(list_view)

    #def callback(self, adapter):
    #    if adapter.selection:
    #        print adapter.selection[0].msg_id

class PostContent(Button):
    image_username = StringProperty()
    avatar = StringProperty()
    post_content = StringProperty()

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
                item = AccordionItem(title=str(cat["forum_name"]))
                bl = BoxLayout(orientation="vertical")

                for b in cat["child"]:
                    bib = BoardIndexButton()
                    bib.board_name = str(b["forum_name"])
                    bib.board_id = b["forum_id"]
                    bib.bind(on_release=self.open_board)
                    bl.add_widget(bib)

                item.add_widget(bl)
                ac.add_widget(item)

        self.boards.add_widget(ac)
            

        #for cat in boards.iterkeys():
        #    item = AccordionItem(title=cat)
        #    bl = BoxLayout(orientation="vertical")
        #    for b in boards[cat]:
        #        bib = BoardIndexButton()
        #        board_name = b.get("name")
        #        board_id = b.get("id")
        #        if board_name:
        #            bib.board_name = board_name
        #        if board_id:
        #            bib.board_id = board_id
        #        bib.bind(on_release=self.open_board)
        #        bl.add_widget(bib)
        #    item.add_widget(bl)
        #    ac.add_widget(item)
        #    item = AccordionItem(title=cat)
        #    data = boards[cat]
        #    args_converter = lambda row_index, ctx: {
        #        "text": ctx["name"],
        #        "board_id": ctx["id"]
        #    }
        #    list_adapter = ListAdapter(data=data, args_converter=args_converter, template="BoardIndexButton")
        #    list_adapter.bind(on_selection_change=self.open_board)
        #    list_view = ListView(adapter=list_adapter)
        #    item.add_widget(list_view)
        #    ac.add_widget(item)
        #self.boards.add_widget(ac)

    def open_board(self, widget):
        self.selected_board = widget.board_id
        if self.selected_board:
            self.manager.current = "boardview"

class BoardIndexButton(Button):
    board_name = StringProperty()
    board_id = StringProperty()

class BoardView(Screen):
    selected_topic = StringProperty(None)
    loaded_board = StringProperty(None)

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
        #data = topics
        #args_converter = lambda row_index, ctx: {
        #    "text": ctx["title"],
        #    "topic_id": ctx["topic_id"]
        #}
        #list_adapter = ListAdapter(data=data, args_converter=args_converter, template="BoardContent")
        #list_adapter.bind(on_selection_change=self.open_topic)
        #list_view = ListView(adapter=list_adapter)
        #self.topics.add_widget(list_view)

    def open_topic(self, widget):
        topic_id = widget.topic_id
        if topic_id:
            self.selected_topic = topic_id
            self.manager.current = "topicview"

class YoureWinner(App):
    def build(self):
        return RootWidget()

if __name__ == "__main__":
    forum = Forum()
    YoureWinner().run()
