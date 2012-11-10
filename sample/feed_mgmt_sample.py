# -*- coding: utf-8 -*-

"""
mekk.greader sample - subscribe, unsubscribe, rename feed...
"""

from mekk.greader import GoogleReaderClient, GoogleLoginFailed
from lxml import objectify

############################################################
# Login & Password
############################################################

# Some oversimplistict password management example.
# Feel free to drop it and get username and password
# any way you like.

def get_username_and_password(force_fresh_input = False):
    """
    Reads username and password from keyring or prompts user for them
    and saves them to the keyring. force_fresh_input enforces
    the prompt (to be used after bad login for example).
    """
    import keyring, getpass

    username = keyring.get_password("mekk.greader", "default-login")
    if (not username) or force_fresh_input:
        while True:
            username = raw_input("Your Google account name: ")
            if username:
                break
        keyring.set_password("mekk.greader", "default-login", username)

    password = keyring.get_password("mekk.greader", username)
    if (not password) or force_fresh_input:
        while True:
            password = getpass.getpass("Password for %s: " % username)
            if password:
                break
        keyring.set_password("mekk.greader", username, password)

    return username, password

############################################################
# Client construction
############################################################

try:
    username, password = get_username_and_password()
    reader_client = GoogleReaderClient(username, password)
except GoogleLoginFailed as e:
    print "Google login failed:", e
    username, password = get_username_and_password(True)
    reader_client = GoogleReaderClient(username, password)

def title(txt):
    print "*" * 60
    print "*", txt
    print "*" * 60

############################################################
# Example calls - info updating, feed detail
############################################################

def title(txt):
    print "*" * 60
    print "*", txt
    print "*" * 60

test_feed = 'http://rss.gazeta.pl/pub/rss/sport.xml'
test_tag = "Just a test tag"

title("Subscribing")

reader_client.subscribe_feed(test_feed, u"Sport Gazetą Zażółć")
reader_client.add_feed_tag(test_feed, u"Sport Bis", test_tag)

title("Reading feed information")
feed_detail = reader_client.get_feed_atom(test_feed, count = 5)
# Debug whole structure
#print objectify.dump(feed_detail)
print u"feed.title: %s" % feed_detail.title
for link in feed_detail.link:
    print u"feed.link(%s): %s" % (
        link.get('rel'), link.get('href'))
for entry in feed_detail.entry:
    print u"* entry %s" % entry.id
    print u"    title: %s" % entry.title
    for link in entry.link:
        print u"    link(%s): %s" % (
            link.get('rel'), link.get('href'))

# Getting raw XML
#feed_detail = reader_client.get_feed_atom(test_feed, format='xml')
#print feed_detail


title("Updating")
reader_client.remove_feed_tag(test_feed, u"Sport Tris", test_tag)
reader_client.change_feed_title(test_feed, u"Zmieniony tytuł Sport")

title("Unsubscribing")
reader_client.unsubscribe_feed(test_feed)

title("Subscribing via site url")
feeds_to_clean = []
for attempt in ['http://sport.pl', 'http://sport.interia.pl']:
    reply= reader_client.subscribe_quickadd("http://sport.pl")
    if reply['numResults']:
        print "Subscribe succesfull"
        print "Feed id:", reply['streamId']
        feeds_to_clean.append(reply['streamId'].replace("feed/", "", 1))
    else:
        print "Subscribe failed to find a feed"

if feeds_to_clean:
    title("Unsubscribing just subscribed")
    for feed in feeds_to_clean:
        print "  ", feed
        reader_client.unsubscribe_feed(feed)
