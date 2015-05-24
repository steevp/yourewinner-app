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

import requests
import re

from bs4 import BeautifulSoup

from lib.yourewinner import Forum

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.carousel import Carousel
from kivy.properties import StringProperty
from kivy.clock import mainthread

import threading

Builder.load_string("""
<RootWidget>:
    gl: gl
    orientation: "vertical"
    ActionBar:
        pos_hint: {'top':1}
        ActionView:
            use_separator: True
            background_image: "catbg.jpg"
            ActionPrevious:
                title: 'Action Bar'
                with_previous: False
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
            id: gl
            cols: 1
            spacing: 2
            size_hint_y: None
            height: self.minimum_height

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

<PostContent>
    direction: "right"
    size_hint_y: None
    height: label1.height + image1.height + 20
    Button:
        size_hint_y: None
        height: root.height
        background_normal: "contentbg.jpg"
        AsyncImage:
            id: image1
            source: root.image_username
            allow_stretch: True
            keep_ratio: False
            width: 200 / 2
            height: 30 / 2
            x: self.parent.x
            y: self.parent.y + self.parent.height - self.height
        Label:
            id: label1
            text: root.post_content
            size: self.texture_size
            text_size: self.parent.width - 10, None
            x: self.parent.x
            y: self.parent.y + self.parent.height - self.height - 20
    BoxLayout:
        orientation: "horizontal"
        height: root.height
        Button:
            text: "test"
            background_normal: "contentbg.jpg"
""")

class RootWidget(BoxLayout):

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        threading.Thread(target=self.get_latest).start()
    
    def get_latest(self, *args):

        print "Getting latest"

        url = "http://www.yourewinner.com/index.php?topic=16399.msg239763;topicseen"
        #url = "http://www.yourewinner.com/index.php?topic=16522.msg239831;topicseen"

        data = requests.get(url).text
        soup = BeautifulSoup(data)

        posts = soup.find(id="forumposts")
        contenthead = posts.find_all(class_="contenthead")
        content = posts.find_all(id=re.compile("^msg_[0-9]+$"))
        posterinfo = posts.find_all(class_="posterinfo")

        for ch, c in zip(contenthead, content): 
            if ch.a.img is None:
                image_username = ch.a.string
            else:
                image_username = "http://yourewinner.com" + ch.a.img["src"][1:]
            post_content = "\n".join(c.strings)
            self.add_post(image_username, post_content)

    @mainthread
    def add_post(self, image_username, post_content):
        pc = PostContent()
        pc.change_content(image_username, post_content)
        self.gl.add_widget(pc)

class PostContent(Carousel):
    image_username = StringProperty()
    post_content = StringProperty()

    def change_content(self, i, p):
        self.image_username = i
        self.post_content = p

class YoureWinner(App):
    def __init__(self, **kwargs):
        super(YoureWinner, self).__init__(**kwargs)
        self.forum = Forum()

    def build(self):
        return RootWidget()

if __name__ == "__main__":
    YoureWinner().run()
