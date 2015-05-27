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
from kivy.properties import StringProperty
from kivy.clock import mainthread
from kivy.graphics.vertex_instructions import Ellipse
from kivy.graphics.context_instructions import Color

import threading

Builder.load_string("""
<RootWidget>:
    canvas.before:
        Color:
            rgba: 0.129, 0.11, 0.271, 1
        Rectangle:
            pos: self.pos
            size: self.size
    forum_posts: forum_posts
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
    orientation: "vertical"

[PostContent@ListItemButton]
    canvas.after:
        Color:
            rgba: 0.051, 0.035, 0.141, 1
        Line:
            rectangle: self.x + 1, self.y + 1, self.width - 1, self.height - 1
    background_color: 0.129, 0.11, 0.271, 1
    deselected_color: 0.129, 0.11, 0.271, 1
    selected_color: 0.624, 0.365, 0.094, 1
    background_normal: ""
    background_down: ""
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
        pos: self.pos
        size: self.size
        x: self.parent.x
        y: self.parent.y + self.parent.height - self.height
    Label:
        #canvas.before:
        #    Color:
        #        rgba: 0.745, 0.455, 0.008, 1
        #    Rectangle:
        #        pos: self.pos
        #        size: self.size
        id: post_content
        text: ctx.post_content
        size: self.texture_size
        text_size: self.parent.width - avatar.width - 10, None
        x: self.parent.x + avatar.width + 5
        y: self.parent.y + self.parent.height - self.height - image_username.height - 5
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

class RootWidget(BoxLayout):

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
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
            "post_content": ctx["content"]
        }
        list_adapter = ListAdapter(data=data, args_converter=args_converter, template="PostContent")
        list_view = ListView(adapter=list_adapter)
        self.forum_posts.add_widget(list_view)

class BoardIndex(BoxLayout):
    
    def __init__(self, **kwargs):
        super(BoardIndex, self).__init__(**kwargs)
        threading.Thread(target=self.get_board_index).start()
    
    def get_board_index(self):
        board_index = forum.get_board_index()
        self.add_boards(board_index)

    @mainthread
    def add_boards(self, boards):
        data = []
        for k in boards.iterkeys():
            data += boards[k]

        args_converter = lambda row_index, rec: {"text": rec["name"], "size_hint_y": None, "height": 40}
        list_adapter = ListAdapter(data=data, args_converter=args_converter, cls=ListItemButton)
        list_view = ListView(adapter=list_adapter)
        self.add_widget(list_view)

class YoureWinner(App):
    def __init__(self, **kwargs):
        super(YoureWinner, self).__init__(**kwargs)

    def build(self):
        return RootWidget()
        #return BoardIndex()

if __name__ == "__main__":
    forum = Forum()
    YoureWinner().run()
