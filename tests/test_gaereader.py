from cStringIO import StringIO
import urllib2
import urlparse

import lxml
import pytest

import gaereader

from google.appengine.ext import ndb, testbed
testbed = testbed.Testbed()
testbed.activate()
testbed.init_urlfetch_stub()

class Result(str):
  def __init__(self, value):
    super(Result, self).__init__(value)
    self.content = value

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
  elif url.startswith("http://www.google.com/reader/api/0/search/items/ids?"):
    query = dict(urlparse.parse_qsl(urlparse.urlparse(url).query))
    if "s" in query:
      assert query["s"] == "user/0/label/tag"
    result = '{"results":[]}'
  elif (url in [
               "http://www.google.com/reader/api/0/token",
               "http://www.google.com/reader/api/0/subscription/list?output=json",
               "http://www.google.com/reader/api/0/preference/list?output=json",
               "http://www.google.com/reader/api/0/unread-count?output=json",
               ]
     or url.startswith("http://www.google.com/reader/api/0/stream/items/contents?ck=")
     or url.startswith("http://www.google.com/reader/api/0/stream/contents/user%2F0%2Flabel%2Ftag?ck=")
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

  future = c.tag_id("tag")
  assert future.get_exception() is None
  assert future.get_result() == "user/0/label/tag"

  future = c.get_my_id()
  assert future.get_exception() is None
  assert future.get_result() == "0"

  future = c.feed_item_id("feed")
  assert future.get_exception() is None
  assert future.get_result() == "id"

  future = c.get_feed_atom("url")
  assert future.get_exception() is None
  assert isinstance(future.get_result(), lxml.etree._Element)

  future = c.get_reading_list_atom()
  assert future.get_exception() is None
  assert isinstance(future.get_result(), lxml.etree._Element)

  future = c.get_read_atom()
  assert future.get_exception() is None
  assert isinstance(future.get_result(), lxml.etree._Element)

  future = c.get_tagged_atom("tag")
  assert future.get_exception() is None
  assert isinstance(future.get_result(), lxml.etree._Element)

  future = c.get_starred_atom()
  assert future.get_exception() is None
  assert isinstance(future.get_result(), lxml.etree._Element)

  future = c.get_fresh_atom()
  assert future.get_exception() is None
  assert isinstance(future.get_result(), lxml.etree._Element)

  future = c.get_broadcast_atom()
  assert future.get_exception() is None
  assert isinstance(future.get_result(), lxml.etree._Element)

  future = c.get_instate_atom("state")
  assert future.get_exception() is None
  assert isinstance(future.get_result(), lxml.etree._Element)

  future = c.search_for_articles("query")
  assert future.get_exception() is None
  assert future.get_result() == []

  future = c.search_for_articles("query", tag="tag")
  assert future.get_exception() is None
  assert future.get_result() == []

  future = c.article_contents("ids")
  assert future.get_exception() is None
  assert future.get_result() == {}

  future = c.contents("tag")
  assert future.get_exception() is None
  assert future.get_result() == {}

  future = c.feed_contents("feed_url")
  assert future.get_exception() is None
  assert future.get_result() == {}

  future = c.get_subscription_list()
  assert future.get_exception() is None
  assert future.get_result() == {}

  future = c.get_tag_list()
  assert future.get_exception() is None
  assert future.get_result() == {u'tags': [{u'id': u'user/0/'}]}

  future = c.get_preference_list()
  assert future.get_exception() is None
  assert future.get_result() == {}

  future = c.get_unread_count()
  assert future.get_exception() is None
  assert future.get_result() == {}

  future = c.subscribe_quickadd("site_url")
  assert future.get_exception() is None
  assert future.get_result() == {}

  future = c.subscribe_feed("feed_url")
  assert future.get_exception() is None
  assert future.get_result() is None

  future = c.unsubscribe_feed("feed_url")
  assert future.get_exception() is None
  assert future.get_result() is None

  future = c.change_feed_title("feed_url", "title")
  assert future.get_exception() is None
  assert future.get_result() is None

  future = c.add_feed_tag("feed_url", "title", "tag")
  assert future.get_exception() is None
  assert future.get_result() is None

  future = c.remove_feed_tag("feed_url", "title", "tag")
  assert future.get_exception() is None
  assert future.get_result() is None

  future = c.disable_tag("tag")
  assert future.get_exception() is None
  assert future.get_result() is None

  future = c._get_atom("url", older_first=True, continue_from="c", format="etree")
  assert future.get_exception() is None
  assert isinstance(future.get_result(), lxml.etree._Element)

  future = c._get_atom("url", format="unkown")
  assert future.get_exception() is None
  assert future.get_result() == '<?xml version="1.0"?><feed><entry><id>id</id></entry></feed>'

  future = c._change_feed("feed_url", "operation", add_tag="tag", remove_tag="tag")
  assert future.get_exception() is None
  assert future.get_result() is None

  future = c._get_list("url", "format")
  assert future.get_exception() is None
  assert future.get_result() == '<?xml version="1.0"?><feed><entry><id>id</id></entry></feed>'
