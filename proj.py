import sys, time, random, pickle, datetime
from bs4 import BeautifulSoup
import urllib2
import scholarly

publications = []
cleaned = []
authors = []
information = []

def scraper(url): #scrapes any URL(weak)
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
    #for delay in fetching to avoid detection
    authors = []
    information = []
    random.seed();  
    n = random.random()*5;  
    time.sleep(n);
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

def writetofile(seq): #writes data to txt file
    outfile = open("pub.txt", "a")
    for item in seq:
        item = item.encode('utf8', 'replace')
        outfile.write("%s\n" %item)
    outfile.close()

def elim_blank(): #eliminates blank lines from text files
    with open("pub.txt","r") as f:
        lines=f.readlines()

    with open("pub.txt","w") as f:  
        [f.write(line) for line in lines if line.strip() ]

def remove_spaces(): #strip spaces from start and end of strings
    for item in publications:
        cleaned.append(item.strip())

flag = "y"
while flag == "y":
    choice = raw_input("Choose\n\n1.Google Scholar\n2.Publications page \n\t")
    if choice == "1":
        try:
            name = raw_input("\nEnter your name: ")
            info = scholarly.search_author(name).next() 
        except Exception:
            print "\nProfile not found on Google Scholar !!" 
            name = raw_input("\nEnter your name: ")
            info = scholarly.search_author(name).next()

        names = []
        namefile = open('names.txt','r')
        f = namefile.read().splitlines()
        for x in f:
            names.append(x)
        if name in names:
            print "\nName already added ! \n"
            continue

        print "\n"    
        print info.affiliation
        print "\nInterests: %s" % info.interests
            
        verify = raw_input("\n\nIs this your google scholar profile? ( y OR n ): ")

        while verify == 'n':
            name = raw_input("\nEnter your name again: ")
            info = scholarly.search_author(name).next()
            print info.affiliation
            print "\n"
            print "\nInterests: %s" % info.interests
            verify = raw_input("\nIs this your google scholar profile? ( y OR n ): ")

        if verify == "y":
            namefile = open("names.txt","a")
            namefile.write("%s\n" %name)
            namefile.close()
            url = "https://scholar.google.co.in/citations?user=$$$$$$$$$$$$&hl=en&cstart=0&pagesize=100".replace('$$$$$$$$$$$$',info.id)
            next_url = url.replace('start=0','start=101')
            next2_url = url.replace('start=0','start=201')
            print "\nFetching data..."
            gsc_scraper(url)
            gsc_scraper(next_url)
            gsc_scraper(next2_url)
            remove_spaces()
            writetofile(cleaned)
            print "\nFetching Complete"
            time.sleep(2);
            
            
    elif choice == "2":
        url = raw_input("\nEnter URL: ")
        print "\nFetching data..."
        scraper(url)
        urlfile = open("URLS.txt","a")
        urlfile.write("%s\n" %url)
        urlfile.close()
        remove_spaces()
        writetofile(cleaned)
        print "\nFetching Complete"
        time.sleep(2);

    elim_blank()
    flag = raw_input("\nWould you like to continue(y or n)? :")
