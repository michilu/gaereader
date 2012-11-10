# -*- coding: utf-8 -*-

"""
mekk.greader example - sample for search and some other methods
"""

from mekk.greader import GoogleReaderClient, GoogleLoginFailed
from pprint import pprint

import logging
logging.basicConfig(level = logging.INFO)

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

############################################################
# Example calls - info reading
############################################################

def title(txt):
    print "*" * 60
    print "*", txt
    print "*" * 60

title("search")
ids = reader_client.search_for_articles(u"humor graphics", count = 4)
pprint(ids)

title("article_contents")
reply = reader_client.article_contents(ids)
#pprint(reply)
for item in reply['items']:
    print u"item %s" % item['id']
    print u"    categories: %s" % u", ".join(item['categories'])
    print u"    title: %s" % item['title']
    for link in item['alternate']:
        print u"    link: %s" % link['href']
    print u"    content: %s" % item['content']['content'][:240]
    print

title("feed_contents")
reply = reader_client.feed_contents(
    "http://rss.gazeta.pl/pub/rss/sport.xml", count=4)
for item in reply['items']:
    print u"item %s" % item['id']
    print u"    categories: %s" % u", ".join(item['categories'])
    print u"    title: %s" % item['title']
    for link in item['alternate']:
        print u"    link: %s" % link['href']
    #print u"    content: %s" % item['content']['content'][:240]
    print

