# encoding: utf8
from __future__ import with_statement


import re

mobilestrings = ['sony', 'symbian', 'nokia', 'samsung', 'mobile', 'windows ce',
                 'epoc', 'opera mini', 'nitro', 'j2me', 'midp-', 'cldc-',
                 'netfront', 'mot', 'up.browser', 'up.link', 'audiovox',
                 'blackberry', 'ericsson,', 'panasonic', 'philips', 'sanyo',
                 'sharp', 'sie-', 'portalmmm', 'blazer', 'avantgo', 'danger',
                 'palm', 'series60', 'palmsource', 'pocketpc', 'smartphone',
                 'rover', 'ipaq', 'au-mic,', 'alcatel', 'ericy', 'up.link',
                 'docomo', 'vodafone/', 'wap1.', 'wap2.']

def strategy1(ua):
    """The Russell Beattie Strategy
        See: http://www.russellbeattie.com/blog/mobile-browser-detection-in-php
    """
    u = ua.lower()
    for s in mobilestrings:
        if u.find(s) >= 0:
            return True
    return False

def strategy2(ua):
    """Pythonic version of the Russell Beattie Strategy"""
    u = ua.lower()
    for s in mobilestrings:
        if s in u:
            return True
    return False

mobileregexs = [re.compile(s, re.IGNORECASE) for s in mobilestrings]

def strategy3(ua):
    """Naive Regex routine"""
    for r in mobileregexs:
        if r.search(ua):
            return True
    return False

bigmobileregex = re.compile('|'.join(mobilestrings), re.IGNORECASE)

def strategy4(ua):
    """One Big Regex"""
    return bool(bigmobileregex.search(ua))

strategies = ['strategy1', 'strategy2', 'strategy3', 'strategy4']

try:
    from django.conf import settings
    settings.configure()
    import django.core.cache
    
    localcache = "locmem:///"
    simple = "simple:///"
    memcache = "memcached://127.0.0.1:11211/"
    
    def cached_strategy(strategy, backend_uri):
        cache = django.core.cache.get_cache(backend_uri)
        def cached(ua):
            cachestr = ua.replace(' ','_')
            x = cache.get("MobileUA-%s" % cachestr)
            if x is None:
                x = strategy(ua)
                cache.set("MobileUA-%s" % cachestr, x)
            return x
        cached.__doc__ = "Cached version (%s) of %s" % (backend_uri.split(':')[0],
                                                        strategy.__doc__)
        return cached
    
    strategy2a = cached_strategy(strategy2, simple)
    strategy2b = cached_strategy(strategy2, localcache)
    strategy2c = cached_strategy(strategy2, memcache)
    
    strategies += ['strategy2a', 'strategy2b', 'strategy2c']
                
except ImportError:
    pass
                
        


#Actual stuff

try:
    from django.utils import simplejson
except ImportError:
    import simplejson

def get_uas():
    with open('useragents.json', 'rb') as f:
        uas = simplejson.load(f)
    return uas

uas = get_uas()
best_ua = "Mozilla/4.0 (PDA; PalmOS/sony/model crdb/Revision:1.1.36(de)) NetFront/3.0"
worst_ua = "Mozilla/5.0 (X11; U; Linux x86_64; en; rv:1.8.1.4) Gecko/20061201 Epiphany/2.18 Firefox/2.0.0.4 (Ubuntu-feisty)"

import timeit

passes = 10000
multiplier =  1000000.0 / passes

import time

def ttimeit(fun, passes, *args, **kw):
    starttime = time.time()
    for x in xrange(passes):
        fun(*args, **kw)
    endtime = time.time()
    return endtime - starttime

#strategies = ["strategy2", "strategy12"]

def run_tests():
    print "Number of UAs in spread: %s" % len(uas)
    print "Numbet of passes: %s" % passes
    print "----------------------------------------------------------------"

    for fname in strategies:
        strategy = globals()[fname]
        print "Trying Strategy: %s" % strategy.__doc__.splitlines()[0]


        best_time = ttimeit(strategy, passes, best_ua)
        print "    Best Case: %.02f usec/pass" % (multiplier * best_time)
        

        worst_time = ttimeit(strategy, passes, worst_ua)
        print "    Worst Case: %.02f usec/pass" % (multiplier * worst_time)
        

        average_time = ttimeit(list, passes, (strategy(ua["User-agent"]) for ua in uas))
        print "    Normal spread: %.02f usec/pass (%.02f usec/ua)" % (multiplier * average_time, multiplier * average_time/len(uas))


        hits = {"Correct": [], "False Positives": [], "False Negatives": []}
        for ua in uas:
            result = strategy(ua["User-agent"])
            if result == ua["mobile"]:
                hits["Correct"].append(ua["User-agent"])
            elif ua["mobile"]:
                hits["False Negatives"].append(ua["User-agent"])
            else:
                hits["False Positives"].append(ua["User-agent"])

        for key, value in hits.items():
            print "        %s: %s (%.02f%%)" % (key, len(value), float(len(value))*100/len(uas))


        print "----------------------------------------------------------------"
    print "False Negatives:"
    for ua in hits["False Negatives"]:
        print ua
    print
    print "False Positives:"
    for ua in hits["False Positives"]:
        print ua




def run_tests_timeit():
    print "Number of UAs in spread: %s" % len(uas)
    print "Numbet of passes: %s" % passes
    print "----------------------------------------------------------------"
    
    for fname in strategies:
        strategy = globals()[fname]
        print "Trying Strategy: %s" % strategy.__doc__.splitlines()[0]
        
        
        best_timer = timeit.Timer("%s(best_ua)" % fname, "from %s import %s, best_ua" % (__name__, fname))
        worst_timer = timeit.Timer("%s(worst_ua)" % fname, "from %s import %s, worst_ua" % (__name__, fname))
        average_timer = timeit.Timer("for ua in uas: %s(ua['User-agent'])" % fname, "from %s import %s, uas" % (__name__, fname))
        
        best_time = best_timer.timeit(number=passes)
        print "    Best Case: %.02f usec/pass" % (multiplier * best_time)
        clear_cache()

        worst_time = worst_timer.timeit(number=passes)
        print "    Worst Case: %.02f usec/pass" % (multiplier * worst_time)
        clear_cache()
    
        average_time = average_timer.timeit(number=passes)
        print "    Normal spread: %.02f usec/pass (%.02f usec/ua)" % (multiplier * average_time, multiplier * average_time/len(uas))
        
    
        hits = {"Correct": 0, "False Positives": 0, "False Negatives": 0}
        for ua in uas:
            result = strategy(ua["User-agent"])
            if result == ua["mobile"]:
                hits["Correct"] += 1
            elif ua["mobile"]:
                hits["False Negatives"] += 1
            else:
                hits["False Positives"] += 1

        for key, value in hits.items():
            print "        %s: %s (%.02f%%)" % (key, value, float(value)*100/len(uas))
            
        clear_cache()
        print "----------------------------------------------------------------"
        
if __name__ == "__main__":
    run_tests()
        
        
    
