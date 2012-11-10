# -*- coding: utf-8 -*-

"""
mekk.greader example - reading some feed information
"""

from mekk.greader import GoogleReaderClient, GoogleLoginFailed
from pprint import pprint

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

title("Subscription list (XML)")
print reader_client.get_subscription_list('xml')

title("Subscription list (normal)")
pprint( reader_client.get_subscription_list() )

title("Tags")
pprint( reader_client.get_tag_list() )

title("Preference (JSON)")
pprint( reader_client.get_preference_list('json') )

title("Unread count")
pprint( reader_client.get_unread_count() )

# See also feed_mgmt_sample for reading feed content with get_feed_atom
