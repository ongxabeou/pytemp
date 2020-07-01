#!/usr/bin/env python
import unittest
import app


class TestHello(unittest.TestCase):

    def setUp(self):
        self.host = 'http://localhost:5000'
        self.sub_path = '/api/v1.0/bot/'
        app.app.testing = True
        self.app = app.app.test_client()
        self.headers = {'Content-Type': 'application/json',
                        'authorization': 'Basic bliauwbralwiubnawk24114eobn'}

    def test_bot_no_token(self):
        rv = self.app.get(self.host + self.sub_path + 'bot_single_seller_shop_pizza_express')
        self.assertEqual(rv.status, '401 UNAUTHORIZED')
        # self.assertEqual(rv.status, '200 OK')
        # self.assertEqual(rv.data, b'Hello World!\n')

    def test_bot_have_token(self):
        rv = self.app.get(self.host + self.sub_path + 'bot_single_seller_shop_pizza_express', headers=self.headers)
        self.assertEqual(rv.status, '200 OK')

    # de f test_hello_hello(self):
    #     rv = self.app.get('/hello/')
    #     self.assertEqual(rv.status, '200 OK')
    #     self.assertEqual(rv.data, b'Hello World!\n')
    #
    # def test_hello_name(self):
    #     name = 'Simon'
    #     rv = self.app.get(f'/hello/{name}')
    #     self.assertEqual(rv.status, '200 OK')
    #     self.assertIn(bytearray(f"{name}", 'utf-8'), rv.data)


if __name__ == '__main__':
    import xmlrunner

    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)

    unittest.main()
