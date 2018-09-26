
import unittest
from tensordash.main import Tensordash
import os

class TensordashTestCase(unittest.TestCase):
    def setUp(self):
        self.tensordash = Tensordash()
# Test config
class ConfigurationTestCase(TensordashTestCase):
    def runTest(self):
        self.tensordash.reconfigure()

# Test login
class LoginTestCase(TensordashTestCase):
    def runTest(self):
       pw = os.getenv('TEST_PASSWORD', 'wrongpass')
       self.tensordash.login('test1', pw)

# Test push
# Test logout
class LogoutTestCase(TensordashTestCase):
    def runTest(self):
       self.tensordash.logout()

if __name__ == '__main__':
    unittest.main()
