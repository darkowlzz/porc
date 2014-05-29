import vcr
import porc
import unittest
import time
from credentials import API_KEY

class PageTest(unittest.TestCase):

    @vcr.use_cassette('fixtures/page/setup.yaml')
    def setUp(self):
        self.client = porc.Client(API_KEY)
        self.collection = self.client.collection('test')
        self.key_names = ['omg', 'wut', 'bbq']
        for name in self.key_names:
            response = self.collection.key(name).put(dict(hello='world')).result()
            response.raise_for_status()

    @vcr.use_cassette('fixtures/page/teardown.yaml')
    def tearDown(self):
        self.collection.delete(dict(force=True)).result().raise_for_status()

    @vcr.use_cassette('fixtures/page/next.yaml')
    def testNext(self):
        pages = self.collection.list(limit=len(self.key_names))
        response = pages.next()
        try: 
            pages.next()
        except StopIteration:
            # good. this is expected
            pass
        else:
            raise AssertionError("Should have thrown StopIteration")

    @vcr.use_cassette('fixtures/page/prev.yaml')
    def testPrev(self):
        page = self.collection.search(query="*", limit=1)
        # proceed two pages
        page.next()
        page.next()
        # go back one
        page.prev()
        # going back one more should raise StopIteration
        try: 
            page.prev()
        except StopIteration:
            # good. this is expected
            pass
        else:
            raise AssertionError("Should have thrown StopIteration")

    @vcr.use_cassette('fixtures/page/reset.yaml')
    def testReset(self):
        page = self.collection.list(limit=len(self.key_names))
        response = page.next().result()
        response.raise_for_status()
        page.reset()
        # now, nexting should work
        response = page.next().result()
        response.raise_for_status()

    @vcr.use_cassette('fixtures/page/iter.yaml')
    def testIter(self):
        pages = self.collection.list(limit=1)
        pages_responses = [page for page in pages]
        assert len(pages_responses) == 3