"""Tests mapped methods for errors"""
import unittest
import lciafmt
from lciafmt.util import log, read_method

class TestInputFiles(unittest.TestCase):

    def test_duplicate_flows(self):
        """Tests whether a target flow maps to more than one characterization
        factor for a given indicator"""
        method_list = lciafmt.supported_methods()
        total_duplicates = 0
        for m in method_list:
            method = read_method(lciafmt.Method.get_class(m['id']))
            flowables = method[['Method','Indicator','Flow UUID']].drop_duplicates()
            duplicates = len(method)-len(flowables)
            if duplicates > 0:
                log.debug('duplicate factors in method '+ m['name'])
            total_duplicates += duplicates
        self.assertTrue(total_duplicates==0,'Duplicate factors in one or more methods')


if __name__ == "__main__":
    unittest.main()
