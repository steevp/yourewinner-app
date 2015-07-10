import json

settings_json = json.dumps([
    {"type": "title",
     "title": "Login"},
    {"type": "string",
     "title": "Username",
     "desc": "Enter your username",
     "section": "login",
     "key": "username"},
    {"type": "string",
     "title": "Password",
     "desc": "Enter your password",
     "section": "login",
     "key": "password"}])

