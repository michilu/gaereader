# -*- coding: utf-8 -*-

from cStringIO import StringIO
import traceback
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
def mock_urlfetch(self, url, payload=None, **_kwargv):
  if url == "https://www.google.com/accounts/ClientLogin":
    result = "Auth=DUMMY"
  elif url == "http://www.google.com/reader/api/0/tag/list?output=json":
    result = '{"tags": [{"id":"user/0/"}]}'
  elif url.startswith("http://www.google.com/reader/api/0/search/items/ids?q="):
    result = '{"results":[]}'
  elif url == "http://www.google.com/reader/api/0/token":
    result = '{}'
  elif url == "http://www.google.com/reader/api/0/subscription/edit?client=mekk.reader_client":
    assert urlparse.parse_qsl(payload) == [('a', 'user/0/label/\xe8\xbf\xbd\xe5\x8a\xa0'), ('ac', 'edit'),
                                           ('s', 'feed/\xe3\x82\xbf\xe3\x82\xb0'), ('r', 'user/0/label/\xe5\x89\x8a\xe9\x99\xa4'),
                                           ('T', '{}'), ('t', '\xe3\x82\xbf\xe3\x82\xa4\xe3\x83\x88\xe3\x83\xab')]
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

def test_UnicodeEncodeError(mock):
  c = gaereader.GoogleReaderClient("login", "password")

  future = c.tag_id(u"タグ")
  traceback.print_tb(future.get_traceback())
  assert future.get_exception() is None
  assert future.get_result() == u"user/0/label/\u30bf\u30b0"

  future = c.search_for_articles(u"検索")
  traceback.print_tb(future.get_traceback())
  assert future.get_exception() is None
  assert future.get_result() == []

  future = c._change_tag(u"タグ", u"タイトル", u"追加", u"削除")
  traceback.print_tb(future.get_traceback())
  assert future.get_exception() is None
  assert future.get_result() is None
