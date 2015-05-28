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
    BoardIndex:
        id: boardindex
        name: "boardindex"
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

        BoxLayout:
            id: forum_posts
            orientation: "vertical"

        BoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: 32
            TextInput:
                multiline: False
                hint_text: "Quick Reply"
            Button:
                text: "Post"
                size_hint_x: None
                width: self.texture_size[0] + 15
                background_normal: "catbg.jpg"

<BoardIndex>:
    boards: boards
    BoxLayout:
        id: boards
        canvas.before:
            Color:
                rgba: 0.129, 0.11, 0.271, 1
            Rectangle:
                pos: self.pos
                size: self.size
        orientation: "vertical"

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

[PostContent@ListItemButton]:
    msg_id: ctx.msg_id
    size_hint_y: None
    height: image_username.height+avatar.height+10 if image_username.height+avatar.height > image_username.height+post_content.height else image_username.height+post_content.height+10
    AsyncImage:
        id: image_username
        source: ctx.image_username
        allow_stretch: True
        keep_ratio: False
        width: 100
        height: 15
        x: self.parent.x + avatar.width + 5
        y: self.parent.y + self.parent.height - self.height
    CircleAvatar:
        id: avatar
        source: ctx.avatar
        allow_stretch: True
        keep_ratio: False
        width: 25
        height: 25
        x: self.parent.x
        y: self.parent.y + self.parent.height - self.height
    Label:
        id: post_content
        text: ctx.post_content
        size: self.texture_size
        text_size: self.parent.width - avatar.width - 10, None
        x: self.parent.x + avatar.width + 5
        y: self.parent.y + self.parent.height - self.height - image_username.height - 5

[BoardIndexButton@ListItemButton]:
    board_id: ctx.board_id
    text: ctx.text
    size_hint_y: None
    height: 40
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
    def on_pre_enter(self):
        threading.Thread(target=self.get_recent).start()
    
    def get_recent(self, page=None):
        recent = forum.get_topic("16503", page=page)
        self.add_posts(recent)

    @mainthread
    def add_posts(self, posts):
        data = posts["posts"]
        args_converter = lambda row_index, ctx: {
            "image_username": ctx["image_username"],
            "avatar": ctx["avatar"],
            "post_content": ctx["content"],
            "msg_id": ctx["msg_id"]
        }
        list_adapter = ListAdapter(data=data, args_converter=args_converter, template="PostContent")
        list_adapter.bind(on_selection_change=self.callback)
        list_view = ListView(adapter=list_adapter)
        self.forum_posts.add_widget(list_view)

    def callback(self, adapter):
        if adapter.selection:
            print adapter.selection[0].msg_id

class BoardIndex(Screen):
    def on_pre_enter(self):
        threading.Thread(target=self.get_board_index).start()
    
    def get_board_index(self):
        board_index = forum.get_board_index()
        self.add_boards(board_index)

    @mainthread
    def add_boards(self, boards):
        ac = Accordion(orientation="vertical")
        for cat in boards.iterkeys():
            item = AccordionItem(title=cat)
            data = boards[cat]
            args_converter = lambda row_index, ctx: {
                "text": ctx["name"],
                "board_id": ctx["id"]
            }
            list_adapter = ListAdapter(data=data, args_converter=args_converter, template="BoardIndexButton")
            list_adapter.bind(on_selection_change=self.open_board)
            list_view = ListView(adapter=list_adapter)
            item.add_widget(list_view)
            ac.add_widget(item)
        self.boards.add_widget(ac)

    def open_board(self, adapter):
        if adapter.selection:
            print adapter.selection[0].board_id
            self.manager.current = "topicview"

class YoureWinner(App):
    def build(self):
        return RootWidget()

if __name__ == "__main__":
    forum = Forum()
    YoureWinner().run()
