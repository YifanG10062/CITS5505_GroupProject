import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

loader = unittest.TestLoader()
suite = loader.discover('tests/unitTests')  

runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)
