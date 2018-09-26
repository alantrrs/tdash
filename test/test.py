
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
        self.tensordash.login('test', os.getenv('TEST_PASSWORD', 'wrongpass'))

# Test push
# Test logout
if __name__ == '__main__':
    unittest.main()
