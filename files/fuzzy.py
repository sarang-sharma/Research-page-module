import sys, time, random, pickle, datetime
from bs4 import BeautifulSoup
import urllib2
import scholarly

publications = []
pubfile = open('pub.txt','r')
f = pubfile.read().splitlines()
for item in f:
   item = item.decode('utf8','replace')
   publications.append(item)
pubfile.close()

print publications
