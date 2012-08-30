from __future__ import with_statement

import threading

from django.template import RequestContext, TemplateDoesNotExist
from django.template.loaders import app_directories, filesystem
from django.test import Client, TestCase

from mock import Mock, patch

from mobileme.utils import get_flavour, set_flavour
from mobileme.middleware import DetectMobileMiddleware


def _reset():
    '''
    Reset the thread local.
    '''
    from mobileme import utils
    del utils._local
    utils._local = threading.local()


class BaseTestCase(TestCase):
    def setUp(self):
        _reset()

    def tearDown(self):
        _reset()


class BasicFunctionTests(BaseTestCase):
    def test_set_flavour(self):
        set_flavour('full')
        self.assertEqual(get_flavour(), 'full')
        set_flavour('mobile')
        self.assertEqual(get_flavour(), 'mobile')
        self.assertRaises(ValueError, set_flavour, 'spam')


class TemplateLoaderTests(BaseTestCase):
    @patch.object(app_directories.Loader, 'load_template')
    @patch.object(filesystem.Loader, 'load_template')
    def test_load_template(self, filesystem_loader, app_directories_loader):
        filesystem_loader.side_effect = TemplateDoesNotExist()
        app_directories_loader.side_effect = TemplateDoesNotExist()

        from mobileme.loaders.mobile import Loader
        loader = Loader([])
        loader._cached_loaders = [filesystem_loader, app_directories_loader]

        set_flavour('mobile')
        with self.assertRaises(TemplateDoesNotExist):
            loader.load_template('base.html', template_dirs=None)
        self.assertEqual(filesystem_loader.call_args_list[0][0], ('mobile/base.html', None))
        self.assertEqual(filesystem_loader.call_args_list[1][0], ('base.html', None))
        self.assertEqual(app_directories_loader.call_args_list[0][0], ('mobile/base.html', None))
        self.assertEqual(app_directories_loader.call_args_list[1][0], ('base.html', None))

        set_flavour('full')
        with self.assertRaises(TemplateDoesNotExist):
            loader.load_template('base.html', template_dirs=None)
        self.assertEqual(filesystem_loader.call_args_list[2][0], ('full/base.html', None))
        self.assertEqual(filesystem_loader.call_args_list[3][0], ('base.html', None))
        self.assertEqual(app_directories_loader.call_args_list[2][0], ('full/base.html', None))
        self.assertEqual(app_directories_loader.call_args_list[3][0], ('base.html', None))

    @patch.object(app_directories.Loader, 'load_template_source')
    @patch.object(filesystem.Loader, 'load_template_source')
    def test_load_template_source(self, filesystem_loader, app_directories_loader):
        filesystem_loader.side_effect = TemplateDoesNotExist()
        app_directories_loader.side_effect = TemplateDoesNotExist()

        from mobileme.loaders.mobile import Loader
        loader = Loader([])
        loader._cached_loaders = [filesystem_loader, app_directories_loader]

        set_flavour('mobile')
        with self.assertRaises(NotImplementedError):
            loader.load_template_source('base.html', template_dirs=None)

        set_flavour('full')
        with self.assertRaises(NotImplementedError):
            loader.load_template_source('base.html', template_dirs=None)

    def test_functional(self):
        from django.template.loader import render_to_string
        set_flavour('full')
        result = render_to_string('index.html')
        result = result.strip()
        self.assertEqual(result, 'Hello .')
        # simulate RequestContext
        result = render_to_string('index.html', context_instance=RequestContext(Mock()))
        result = result.strip()
        self.assertEqual(result, 'Hello full.')
        set_flavour('mobile')
        result = render_to_string('index.html')
        result = result.strip()
        self.assertEqual(result, 'Mobile!')


class NonRealAgentNameTests(BaseTestCase):
    @patch('mobileme.middleware.set_flavour')
    def test_mobile_browser_agent(self, set_flavour):
        request = Mock()
        request.META = {
            'HTTP_USER_AGENT': 'My Mobile Browser',
        }
        middleware = DetectMobileMiddleware()
        middleware.process_request(request)
        self.assertEqual(set_flavour.call_args, (('full', request), {}))

    @patch('mobileme.middleware.set_flavour')
    def test_desktop_browser_agent(self, set_flavour):
        request = Mock()
        request.META = {
            'HTTP_USER_AGENT': 'My Desktop Browser',
        }
        middleware = DetectMobileMiddleware()
        middleware.process_request(request)
        self.assertEqual(set_flavour.call_args, (('full', request), {}))


class RealAgentNameTests(BaseTestCase):
    def assertFullFlavour(self, agent):
        client = Client(HTTP_USER_AGENT=agent)
        response = client.get('/')
        if response.content.strip() != 'Hello full.':
            self.fail(u'Agent is matched as mobile: %s' % agent)

    def assertMobileFlavour(self, agent):
        client = Client(HTTP_USER_AGENT=agent)
        response = client.get('/')
        if response.content.strip() != 'Mobile!':
            self.fail(u'Agent is not matched as mobile: %s' % agent)

    def test_ipad(self):
        self.assertFullFlavour(u'Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10')

    def test_iphone(self):
        self.assertMobileFlavour(u'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543a Safari/419.3')

    def test_motorola_xoom(self):
        self.assertFullFlavour(u'Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13')

    def test_opera_mobile_on_android(self):
        '''
        Regression test of issue #9
        '''
        self.assertMobileFlavour(u'Opera/9.80 (Android 2.3.3; Linux; Opera Mobi/ADR-1111101157; U; en) Presto/2.9.201 Version/11.50')


class RegressionTests(BaseTestCase):
    def setUp(self):
        self.desktop = Client()
        # wap triggers mobile behaviour
        self.mobile = Client(HTTP_USER_AGENT='wap')

    def test_multiple_browser_access(self):
        '''
        Regression test of issue #2
        '''
        response = self.desktop.get('/')
        self.assertEqual(response.content.strip(), 'Hello full.')

        response = self.mobile.get('/')
        self.assertEqual(response.content.strip(), 'Mobile!')

        response = self.desktop.get('/')
        self.assertEqual(response.content.strip(), 'Hello full.')

        response = self.mobile.get('/')
        self.assertEqual(response.content.strip(), 'Mobile!')

    def test_cache_page_decorator(self):
        response = self.mobile.get('/cached/')
        self.assertEqual(response.content.strip(), 'Mobile!')

        response = self.desktop.get('/cached/')
        self.assertEqual(response.content.strip(), 'Hello full.')

        response = self.mobile.get('/cached/')
        self.assertEqual(response.content.strip(), 'Mobile!')

        response = self.desktop.get('/cached/')
        self.assertEqual(response.content.strip(), 'Hello full.')
