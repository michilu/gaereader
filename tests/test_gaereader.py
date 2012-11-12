from cStringIO import StringIO
import urllib2

import lxml
import pytest

import gaereader

from google.appengine.ext import ndb, testbed
testbed = testbed.Testbed()
testbed.activate()
testbed.init_urlfetch_stub()

class Result(str):
  pass

@ndb.tasklet
def mock_urlfetch(self, url, **_kwargv):
  if url == "https://www.google.com/accounts/ClientLogin":
    result = "Auth=DUMMY"
  elif url == "http://www.google.com/reader/api/0/tag/list?output=json":
    result = '{"tags": [{"id":"user/0/"}]}'
  elif url in [
               "http://www.google.com/reader/atom/feed/feed?n=2",
               "http://www.google.com/reader/atom/feed/url",
               "http://www.google.com/reader/atom/user/0/label/tag",
               "http://www.google.com/reader/atom/user/-/state/com.google/reading-list",
               "http://www.google.com/reader/atom/user/-/state/com.google/read",
               "http://www.google.com/reader/atom/user/-/state/com.google/starred",
               "http://www.google.com/reader/atom/user/-/state/com.google/fresh",
               "http://www.google.com/reader/atom/user/-/state/com.google/broadcast",
               "http://www.google.com/reader/atom/user/-/state/com.google/state",
               "url",
               "url?c=c&r=o",
               "url?output=format",
              ]:
    result = '<?xml version="1.0"?><feed><entry><id>id</id></entry></feed>'
  elif url.startswith("http://www.google.com/reader/api/0/search/items/ids?q=query&output=json&num=20&ck="):
    result = '{"results":[]}'
  elif (url in [
               "http://www.google.com/reader/api/0/token",
               "http://www.google.com/reader/api/0/subscription/list?output=json",
               "http://www.google.com/reader/api/0/preference/list?output=json",
               "http://www.google.com/reader/api/0/unread-count?output=json",
               ]
     or url.startswith("http://www.google.com/reader/api/0/stream/items/contents?ck=")
     or url.startswith("http://www.google.com/reader/api/0/stream/contents/feed/feed_url?ck=")
     or url.startswith("http://www.google.com/reader/api/0/subscription/quickadd?ck=")):
    result = '{}'
  elif url in [
               "http://www.google.com/reader/api/0/subscription/edit?client=mekk.reader_client",
               "http://www.google.com/reader/api/0/disable-tag?client=mekk.reader_client",
              ]:
    result = 'OK'
  else:
    raise ValueError(url)

  result = Result(result)
  result.status_code = 200
  result.url = url
  raise ndb.Return(result)


def pytest_funcarg__mock(request):

  def setup():
    mock = request.getfuncargvalue("monkeypatch")
    mock.setattr(ndb.Context, "urlfetch", mock_urlfetch)
    return mock

  def teardown(mock):
    mock.undo()

  return request.cached_setup(setup=setup, teardown=teardown, scope="function")

def test_GoogleReaderClient(mock):
  c = gaereader.GoogleReaderClient("login", "password")
  assert c.tag_id("tag") == "user/0/label/tag"
  assert c.get_my_id() == "0"
  assert c.feed_item_id("feed") == "id"
  assert isinstance(c.get_feed_atom("url"), lxml.etree._Element)
  assert isinstance(c.get_reading_list_atom(), lxml.etree._Element)
  assert isinstance(c.get_read_atom(), lxml.etree._Element)
  assert isinstance(c.get_tagged_atom("tag"), lxml.etree._Element)
  assert isinstance(c.get_starred_atom(), lxml.etree._Element)
  assert isinstance(c.get_fresh_atom(), lxml.etree._Element)
  assert isinstance(c.get_broadcast_atom(), lxml.etree._Element)
  assert isinstance(c.get_instate_atom("state"), lxml.etree._Element)
  assert c.search_for_articles("query") == []
  assert c.article_contents("ids") == {}
  assert c.feed_contents("feed_url") == {}
  assert c.get_subscription_list() == {}
  assert c.get_tag_list() == {u'tags': [{u'id': u'user/0/'}]}
  assert c.get_preference_list() == {}
  assert c.get_unread_count() == {}
  assert c.subscribe_quickadd("site_url") == {}
  assert c.subscribe_feed("feed_url") is None
  assert c.unsubscribe_feed("feed_url") is None
  assert c.change_feed_title("feed_url", "title") is None
  assert c.add_feed_tag("feed_url", "title", "tag") is None
  assert c.remove_feed_tag("feed_url", "title", "tag") is None
  assert c.disable_tag("tag") is None
  assert isinstance(c._get_atom("url", older_first=True, continue_from="c", format="etree"), lxml.etree._Element)
  assert c._get_atom("url", format="unkown") == '<?xml version="1.0"?><feed><entry><id>id</id></entry></feed>'
  assert c._change_feed("feed_url", "operation", add_tag="tag", remove_tag="tag") is None
  assert c._get_list("url", "format") == '<?xml version="1.0"?><feed><entry><id>id</id></entry></feed>'
