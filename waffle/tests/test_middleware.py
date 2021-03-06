from django.http import HttpResponse

from nose.tools import eq_
from test_utils import RequestFactory

from waffle.middleware import WaffleMiddleware


def test_set_cookies():
    get = RequestFactory().get('/foo')
    get.waffles = {'foo': [True, False], 'bar': [False, False]}
    resp = HttpResponse()
    assert not 'dwf_foo' in resp.cookies
    assert not 'dwf_bar' in resp.cookies

    resp = WaffleMiddleware().process_response(get, resp)
    assert 'dwf_foo' in resp.cookies
    assert 'dwf_bar' in resp.cookies

    eq_('True', resp.cookies['dwf_foo'].value)
    eq_('False', resp.cookies['dwf_bar'].value)


def test_rollout_cookies():
    get = RequestFactory().get('/foo')
    get.waffles = {'foo': [True, True],
                   'bar': [False, True],
                   'baz': [True, False],
                   'qux': [False, False]}
    resp = HttpResponse()
    resp = WaffleMiddleware().process_response(get, resp)
    for k in get.waffles:
        cookie = 'dwf_%s' % k
        assert cookie in resp.cookies
        eq_(str(get.waffles[k][0]), resp.cookies[cookie].value)
        if get.waffles[k][1]:
            assert bool(resp.cookies[cookie]['max-age']) == get.waffles[k][0]
        else:
            assert resp.cookies[cookie]['max-age']
