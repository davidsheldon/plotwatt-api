#!/usr/bin/env python

#############################################################################
########### plotwatt disaggregation access API                    ###########
#############################################################################
import urllib2
import base64
import json
from datetime import datetime
"""
curl -v -u username:password 
'https://plotwatt.com/disags?start_date=2012-01-22&end_date=2012-01-26'

curl -v -u username:password
'https://plotwatt.com/disags?start_date=2012-01-22&end_date=2012-01-26&house_ids=12'
'https://plotwatt.com/disags?start_date=2012-01-22&end_date=2012-01-26&house_ids=1016,1017'

"""
DISAGS_SERVICE='https://plotwatt.com/disags'
def get_disags(username, password, start_date, end_date, house_ids=None):
    """
    @ returns disags from the disags service in the following json format
    A day is divided into 4  timeslots that are 6 hours each
    the occurred_at falls in the middle of each time slot
    { 'house_id1': [ [occured_at time slot, KWhr consumption for the time slot,
                    appliance_group], [ O2, K2, G2 ], ... ],
      'house_id2':[ [occured_at time slot, KWhr consumption for the time slot,
                    appliance_group], [ O3, K3, G3 ], ... ],
        ...
    }

    @param username
    @param password
    @param start_date  YYYY-MM-DD format
    @param end_date  YYYY-MM-DD format
    @param house_ids  optionally scope the result to only house_ids from this list
    """

    # start_date and end_date are required params
    url = "%s?start_date=%s&end_date=%s" %(DISAGS_SERVICE, start_date,
            end_date)
    if house_ids != None:
        url += "&house_ids=%s" %(','.join(house_ids))

    print "fetching data from ", url
    req  = urllib2.Request(url)

    # add auth header
    base64string = base64.encodestring(
                '%s:%s' % (username, password))[:-1]
    authheader =  "Basic %s" % base64string
    req.add_header("Authorization", authheader)

    # data is returned as json
    conn = urllib2.urlopen(req)
    ret = conn.read()
    if 'login' in conn.url:
        print "auth failed"
        data={}
    else:
        data = json.loads(ret)

    return data


def exportToCsv (data, byday=False):
    """
    This is data for a house as a list
    [YYYY-mm-dd HH:MM:SS, 'group', kwhr ]
    """
    from datetime import datetime
    from collections import defaultdict

    ddtotal = defaultdict (lambda: defaultdict(float))
    cats = set()

    for row in data:
        if byday:
            ddtotal[row[0][:10]][row[1]] += row[2]
        else:
            ddtotal[row[0]][row[1]] = row[2]
        cats.add(row[1])

    # now print
    lcat = sorted (cats)
    print "Date,", 
    print ','.join(lcat)
    for ts in sorted(ddtotal):
        tsrow = ddtotal[ts]
        tss = 'T'.join(ts.split(' ',1))
        print "%s," %(tss),
        for cat in lcat:
            print "%.2f," %(tsrow[cat]), 
        print

def main():
    import sys
    if len(sys.argv) < 5:
        print "test_disags_service.py username password start_date end_date house_id"
        exit(-1)
    username = sys.argv[1]
    password = sys.argv[2]
    start_date = sys.argv[3]
    end_date = sys.argv[4]

    if len(sys.argv) > 5:
        house_ids = [ sys.argv[5] ]
    else:
        house_ids = None
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError, e:
        print str(e)
        exit(-1)
    #  all houses that I have access to -- for start_date <= date < end_date
    data=get_disags(username, password, start_date, end_date, house_ids)

    for house in data:
        print "houseID ", house,",BY DAY,"
        exportToCsv (data[house], True)
        print "houseID ", house,",6 hours,"
        exportToCsv (data[house], False)

if __name__ == "__main__":
    main()
