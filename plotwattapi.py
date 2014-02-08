#!/usr/bin/python
"""
Author: Kyle Konrad and Zach Dwiel

This is a basic interface to the plotwatt api.

Please email comments and questions to zdwiel@plotwatt.com
"""

import urllib2, base64
from datetime import datetime
import time
import json

class PlotwattError(Exception) :
    def __init__(self, message) :
        self.message = message
    
    def __str__(self) :
        return "Plotwatt Error: %s " % (self.message)

class Plotwatt(object) :
    def __init__(self, house_id, secret, baseurl="http://plotwatt.com") :
        self.house_id = house_id
        self.secret   = secret
        
        self.baseurl = baseurl
        self.base64string = base64.encodestring('%s:%s' % (secret, ''))[:-1]
        self.authheader =  "Basic %s" % self.base64string

        self.mysql_datetime_format = "'%Y-%m-%d %H:%M:%S'"

        # api actions
        self.list_meters_url = '/api/v2/list_meters'
        self.push_readings_url = '/api/v2/push_readings'
        self.new_meters_url = '/api/v2/new_meters'
        self.delete_meter_url = '/api/v2/delete_meter'

    def _request(self, url, data=None):
        """ make a request to plotwatt.com """
        req = urllib2.Request(self.baseurl + url)
        req.add_header("Authorization", self.authheader)
        try :
            return urllib2.urlopen(req, data, 5)
        except urllib2.HTTPError, e :
            if e.code == 422 :
                raise PlotwattError(e.read())
            raise e

    def create_meters(self, num_meters):
        """ create meters on your plotwatt.com account """
        res = self._request(self.new_meters_url, "number_of_new_meters=%s" % num_meters)
        return json.loads(res.read())

    def delete_meter(self, meter_id):
        """ delete a meter from your plotwatt.com account """
        return self._request(self.delete_meter_url, "meter_id=%s" % meter_id)

    def list_meters(self):
        """ list the meters connected to your plotwatt.com account """
        res = self._request(self.list_meters_url, '')
        return eval(res.read())

    def push_readings(self, meter, readings, times):
        """call push_readings endpoint. times should be in POSIX format in UTC"""
        
        meters = [meter] * len(readings)
        
        def sanitize_times(t) :
            """ if the input is a datetime, turn it into a timestamp,
            otherwise, make sure that it is an intiger"""
            if isinstance(t, datetime) :
                return str(int(time.mktime(t.timetuple())))
            else :
                return str(int(t))
          
        times = map(sanitize_times, times)
        data = ','.join(map(lambda tup: "%s,%s,%s" % tup, zip(meters, readings, times)))
        print data
        res = self._request(self.push_readings_url, data)
        assert res.getcode() == 200
        return res
