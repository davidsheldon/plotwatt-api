#!/usr/bin/python

import unittest
from datetime import datetime, timedelta

from plotwattapi import Plotwatt, PlotwattError

class TestDisagDayGeneration(unittest.TestCase):
    def setUp(self):
        self.pw = Plotwatt(2517, "3b0f9e9a9d98137c")
        
        # clear any old meters
        for meter_id in self.pw.list_meters() :
            self.pw.delete_meter(meter_id)
    
    def test_list_and_create_meters(self):
        assert self.pw.list_meters() == []
        self.pw.create_meters(1)
        assert len(self.pw.list_meters()) == 1
    
    def test_push_readings(self):
        self.pw.create_meters(1)
        meter_id = self.pw.list_meters()[0]
        
        now = datetime.now()
        second = seconds = timedelta(seconds=1)
        self.pw.push_readings(meter_id, [1, 2, 3], [now, now + 1*second, now + 2*second])

    def test_push_invalid_readings(self):
        self.pw.create_meters(1)
        meter_id = self.pw.list_meters()[0]
        
        now = datetime.now() + timedelta(days = 2)
        second = seconds = timedelta(seconds=1)
        try :
            self.pw.push_readings(meter_id, [1, 2, 3], [now, now + 1*second, now + 2*second])
            assert 'the previous line should have raised an error'
        except PlotwattError, e:
            assert 'future' in str(e)

def main() :
    unittest.main()

if __name__ == '__main__':
    main()
