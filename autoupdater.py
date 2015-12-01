import time, random, datetime
from bs4 import BeautifulSoup
import urllib2
import scholarly
import difflib

publications = []
cleaned = []
authors = []
information = []

print "AUTO UPDATER \n\n"
print "Fetching data...\n\n"

def order(seq): #Groups publications yearwise
   rev = []
   desc = []
   for year in range(2000,2017):
      for line in seq:
         if str(year) in line:
            rev.append(line)
   for item in reversed(rev):
      desc.append(item)
   return desc

def duplicheck(seq):  #checks for duplicates in a list
    noDupes = []
    
    [noDupes.append(i) for i in seq if not noDupes.count(i)]
    return noDupes

def fuzzycheck(seq): #fuzzy algo checks for similar publications
   toremove=[]
   for i in range(0,len(seq)):
      for j in range(i+1,len(seq)):
         match = difflib.SequenceMatcher(None,seq[i],seq[j])
         d = match.ratio()
         if (d > 0.85): #degree of similarity
            toremove.append(seq[j])
            
   for x in toremove:
      if x in seq:
         seq.remove(x)
   return seq


def writetofile(seq,mode): #writes publications to a txt file
    outfile = open('pub.txt', mode)
    for item in seq:
        item = item.encode('utf8', 'replace')
        outfile.write("%s\n" %item)
    outfile.close()

def elim_blank(): #Function to remove blank lines from txt file
    with open("pub.txt","r") as f:
        lines=f.readlines()

    with open("pub.txt","w") as f:  
        [f.write(line) for line in lines if line.strip() ]

def scraper(url): #scrapes any url(weak)
    try:
        test_url = urllib2.urlopen(url)
    except Exception:
        time.sleep(2);
        test_url = urllib2.urlopen(url)
    
    readhtml = test_url.read()
    test_url.close()
    soup = BeautifulSoup(readhtml)
    doc = soup.get_text()
    splitter = doc.splitlines()
    for publi in splitter:
        for year in range(2000,2020):
           if (str(year) in publi
               and publi.strip().isdigit() == False
               and len(publi.strip()) > 20):
               publications.append(publi)
               

def gsc_scraper(gsc_url): #scrapes google scholar page
    authors = []
    information = []
    random.seed();  
    n = random.random()*5;  
    time.sleep(n); #for delay in fetching to avoid detection
    try:
        test_url = urllib2.urlopen(gsc_url)
    except Exception:
        time.sleep(2);
        test_url = urllib2.urlopen(gsc_url)
    readhtml = test_url.read()
    test_url.close()
    soup = BeautifulSoup(readhtml)
    for auth in soup.html.find_all("div", class_="gs_gray")[::2]:
        authors.append(auth.text)
    for info in soup.html.find_all("div", class_="gs_gray")[1::2]:
       information.append(info.text)
    for publi,author,info in zip(soup.html.find_all("a", class_="gsc_a_at"),authors,information):
        publications.append(author+", "+publi.text+","+info.replace('...','')+".")

def remove_spaces():
    for item in publications:
        cleaned.append(item.strip())

names = []
namefile = open('names.txt','r')
f = namefile.read().splitlines()
for name in f:
    names.append(name)
namefile.close()

for name in names:
    info = scholarly.search_author(name).next()
    url = "https://scholar.google.co.in/citations?user=$$$$$$$$$$$$&hl=en&cstart=0&pagesize=100".replace('$$$$$$$$$$$$',info.id)
    next_url = url.replace('start=0','start=101')
    next2_url = url.replace('start=0','start=201')
    gsc_scraper(url)
    gsc_scraper(next_url)
    gsc_scraper(next2_url)
    remove_spaces()
    writetofile(cleaned,"a")
    cleaned = []
    publications = []
    
urls = []
urlfile = open('URLS.txt','r')
f = urlfile.read().splitlines()
for url in f:
   urls.append(url)
urlfile.close()
for url in urls:
   scraper(url)
   remove_spaces()
   writetofile(cleaned,"a")
   cleaned = []
   publications = []
   
pubfile = open('pub.txt','r')
f = pubfile.read().splitlines()
for item in f:
   item = item.decode('utf8','replace')
   cleaned.append(item.strip())
pubfile.close()
print "Checking for duplicates...\n\n"
cleaned = duplicheck(cleaned)
cleaned = fuzzycheck(cleaned)
print "Duplicates removed...\n\n"
print
cleaned = order(cleaned)
writetofile(cleaned,'w')
elim_blank()
print "\nUPDATE COMPLETE"
time.sleep(2)

