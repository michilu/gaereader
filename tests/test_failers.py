from cStringIO import StringIO
import urllib2

import pytest

import gaereader


def mock_urlopen_login_fail(url, **_kwargv):
  url = url._Request__original
  code = 403
  msg = "Forbidden"
  hdrs = None
  fp = StringIO("Error=BadAuthentication")
  raise urllib2.HTTPError(url, code, msg, hdrs, fp)

def pytest_funcarg__mock_login_fail(request):

  def setup():
    mock = request.getfuncargvalue("monkeypatch")
    mock.setattr(urllib2, "urlopen", mock_urlopen_login_fail)
    return mock

  def teardown(mock):
    mock.undo()

  return request.cached_setup(setup=setup, teardown=teardown, scope="function")

def test_GoogleLoginFailed(mock_login_fail):
  with pytest.raises(gaereader.GoogleLoginFailed):
    gaereader.GoogleReaderClient("login", "password")


def mock_urlopen_login_fail1(url, **_kwargv):
  url = url._Request__original
  code = 400
  msg = "Forbidden"
  hdrs = None
  fp = StringIO("Error=BadAuthentication")
  raise urllib2.HTTPError(url, code, msg, hdrs, fp)

def pytest_funcarg__mock_login_fail1(request):

  def setup():
    mock = request.getfuncargvalue("monkeypatch")
    mock.setattr(urllib2, "urlopen", mock_urlopen_login_fail1)
    return mock

  def teardown(mock):
    mock.undo()

  return request.cached_setup(setup=setup, teardown=teardown, scope="function")

def test_GoogleLoginFailed1(mock_login_fail1):
  with pytest.raises(urllib2.HTTPError):
    gaereader.GoogleReaderClient("login", "password")


def mock_urlopen_login_fail2(url, **_kwargv):
  url = url._Request__original
  fp = StringIO("Auth=")
  headers = None
  return urllib2.addinfourl(fp, headers, url)

def pytest_funcarg__mock_login_fail2(request):

  def setup():
    mock = request.getfuncargvalue("monkeypatch")
    mock.setattr(urllib2, "urlopen", mock_urlopen_login_fail2)
    return mock

  def teardown(mock):
    mock.undo()

  return request.cached_setup(setup=setup, teardown=teardown, scope="function")

def test_GoogleLoginFailed2(mock_login_fail2):
  with pytest.raises(gaereader.GoogleLoginFailed):
    gaereader.GoogleReaderClient("login", "password")


def mock_urlopen_errors(url, **_kwargv):
  url = url._Request__original
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
  fp = StringIO(result)
  headers = None
  return urllib2.addinfourl(fp, headers, url)

def pytest_funcarg__mock_errors(request):

  def setup():
    mock = request.getfuncargvalue("monkeypatch")
    mock.setattr(urllib2, "urlopen", mock_urlopen_errors)
    return mock

  def teardown(mock):
    mock.undo()

  return request.cached_setup(setup=setup, teardown=teardown, scope="function")

def test_GoogleOperationFailed(mock_errors):
  c = gaereader.GoogleReaderClient("login", "password")
  with pytest.raises(gaereader.GoogleOperationFailed):
    c.disable_tag("tag")
  with pytest.raises(gaereader.GoogleOperationFailed):
    c._change_feed("feed_url", "operation")
  with pytest.raises(gaereader.GoogleOperationFailed):
    c._change_tag("feed_url", "title")
