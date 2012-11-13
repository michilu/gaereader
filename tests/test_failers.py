from cStringIO import StringIO
import urllib2

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
def mock_urlfetch_login_fail(self, url, **_kwargv):
  result = Result("Error=BadAuthentication")
  result.status_code = 403
  result.url = url
  raise ndb.Return(result)

def pytest_funcarg__mock_login_fail(request):

  def setup():
    mock = request.getfuncargvalue("monkeypatch")
    mock.setattr(ndb.Context, "urlfetch", mock_urlfetch_login_fail)
    return mock

  def teardown(mock):
    mock.undo()

  return request.cached_setup(setup=setup, teardown=teardown, scope="function")

def test_GoogleLoginFailed(mock_login_fail):
  with pytest.raises(gaereader.GoogleLoginFailed):
    gaereader.GoogleReaderClient("login", "password")


@ndb.tasklet
def mock_urlfetch_login_fail1(self, url, **_kwargv):
  result = Result("Error=BadAuthentication")
  result.status_code = 400
  result.url = url
  result.final_url = url
  result.headers = {}
  raise ndb.Return(result)

def pytest_funcarg__mock_login_fail1(request):

  def setup():
    mock = request.getfuncargvalue("monkeypatch")
    mock.setattr(ndb.Context, "urlfetch", mock_urlfetch_login_fail1)
    return mock

  def teardown(mock):
    mock.undo()

  return request.cached_setup(setup=setup, teardown=teardown, scope="function")

def test_GoogleLoginFailed1(mock_login_fail1):
  with pytest.raises(urllib2.HTTPError):
    gaereader.GoogleReaderClient("login", "password")


@ndb.tasklet
def mock_urlfetch_login_fail2(self, url, **_kwargv):
  result = Result("Auth=")
  result.status_code = 200
  result.url = url
  raise ndb.Return(result)

def pytest_funcarg__mock_login_fail2(request):

  def setup():
    mock = request.getfuncargvalue("monkeypatch")
    mock.setattr(ndb.Context, "urlfetch", mock_urlfetch_login_fail2)
    return mock

  def teardown(mock):
    mock.undo()

  return request.cached_setup(setup=setup, teardown=teardown, scope="function")

def test_GoogleLoginFailed2(mock_login_fail2):
  with pytest.raises(gaereader.GoogleLoginFailed):
    gaereader.GoogleReaderClient("login", "password")


@ndb.tasklet
def mock_urlfetch_errors(self, url, **_kwargv):
  if url == "https://www.google.com/accounts/ClientLogin":
    result = "Auth=DUMMY"
  elif url == "http://www.google.com/reader/api/0/tag/list?output=json":
    result = '{"tags": []}'
  elif url in [
                "http://www.google.com/reader/api/0/disable-tag?client=mekk.reader_client",
                "http://www.google.com/reader/api/0/token",
                "http://www.google.com/reader/api/0/subscription/edit?client=mekk.reader_client",
              ]:
    result = ""
  else:
    raise ValueError(url)

  result = Result(result)
  result.status_code = 200
  result.url = url
  raise ndb.Return(result)

def pytest_funcarg__mock_errors(request):

  def setup():
    mock = request.getfuncargvalue("monkeypatch")
    mock.setattr(ndb.Context, "urlfetch", mock_urlfetch_errors)
    return mock

  def teardown(mock):
    mock.undo()

  return request.cached_setup(setup=setup, teardown=teardown, scope="function")

def test_GoogleOperationFailed(mock_errors):
  c = gaereader.GoogleReaderClient("login", "password")
  future = c.disable_tag("tag")
  assert isinstance(future.get_exception(), gaereader.GoogleOperationFailed)
  future = c._change_feed("feed_url", "operation")
  assert isinstance(future.get_exception(), gaereader.GoogleOperationFailed)
  future = c._change_tag("feed_url", "title")
  assert isinstance(future.get_exception(), gaereader.GoogleOperationFailed)
