from yourewinner import Forum
from time import sleep

forum = Forum()
forum.login("username", "password")

for post in forum.get_recent(page=1):
    msg = post.get("msg")
    username = post.get("username")
    print "Rating post " + msg + " by " + username
    forum.rate_post(msg, "23")
    sleep(5)

print "Finished rating posts"
