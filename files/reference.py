import sys, time, random, pickle, datetime
import pprint
import re
import requests
import csv
from collections import defaultdict
from bs4 import BeautifulSoup as bs

agents = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
    "Mozilla/5.0 (compatible; MSIE 10.0; Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)",
    "Opera/9.25 (Windows NT 6.0; U; en)"
]
    
random.seed()
rint = random.randint(0, len(agents)-1)

base_url = "http://scholar.google.es"
user_url = base_url + "/citations?user=M1FQwSUAAAAJ&hl=en"
header = {'User-agent' : agents[rint]}
num_results = 20
nap_time = 360

def fetchPage(url, delay=nap_time):
    time.sleep(delay + (delay * random.random()))
    #header = {'User-agent': agents[random.randint(0, len(agents)-1)]}
    header = {'User-agent': agents[0], 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Referer': 'https://scholar.google.es/citations?view_op=view_citation&hl=en&user=M1FQwSUAAAAJ&citation_for_view=M1FQwSUAAAAJ:zYLM7Y9cAGgC'}
    r = requests.get(url + "&num=" + str(num_results), headers=header, allow_redirects=False, verify=False)
    print r.request.headers
    html = r.text
    return bs(html, "lxml")
    
# Recursively iterates over pagination to collect all citations for the given link
# Each page is returned as an individual BS object
def fetchPages(url, pages):
    # Get first page
    print "Fetching", url
    p = fetchPage(url)
    pages.append(p)
    
    # Check if another page exists in paginated results
    next_link = p.find("b", text="Next")
    if next_link and next_link.parent.name == 'a':
        print "Fetching another page"
        fetchPages(base_url + next_link.parent['href'], pages)    
    
def toInt(s):
    try:
        return int(s)
    except ValueError:
        return 0
    
# Returns a list of articles from single page
def parseArticles(page):
    articles = []
    
    # Get all citation rows as list
    rows = page.find_all(class_="gsc_a_tr")  
    for row in rows:
        name = unicode(row.td.a.string).strip()
        link = base_url + row.td.a['href'].strip()
        details = row.find_all(class_="gs_gray")
        authors = details[0].text.strip()
        rest = details[1].stripped_strings
        journal = rest.next()
        year = toInt(unicode(row.find(class_="gsc_a_h").string).strip())
        cites = row.find(class_="gsc_a_c")
        num_citations = toInt(unicode(cites.a.string).strip())
        citations_link = cites.a['href']
        article = {"name":name, "link":link, "authors":authors, "journal":journal, "year":year, 
            "num_citations":num_citations, "citations_link":citations_link};
        articles.append(article)

    return articles
    
# Collects citations for a list of pages
def parseArticlePages(pages):
    articles = []
    for page in pages:
        page_articles = parseArticles(page)
        articles.extend(page_articles)
    
    return articles
    

# Returns list of citations from single page
def parseCitations(page):
    citations = []
    
    rows = page.find_all(class_="gs_r")  
    for row in rows:
        name = unicode(row.find("h3").string).strip()
        
        # Not all citations have links
        link = ""
        link_elem = row.find("h3").a
        if (link_elem):
            link = unicode(link_elem['href']).strip()
            
        details = row.find(class_="gs_a").text.strip()
        
        # Use regex to extract publication year
        year = -1
        #pattern = re.compile("(\d+)(?!.*\d)") # last number in string
        pattern = re.compile("(^|\s)(\d{4})(\s|$)")
        match = pattern.search(details)
        if match is not None:
            year = toInt(match.group().strip())
        
        # Use regex to extract number of citations
        num_citations = 0
        footer_filter = lambda x: x.has_attr('class') and 'gs_fl' in x['class'] and not 'gs_ggs' in x['class']
        footer = row.find(footer_filter)        
        if footer:
            cite_filter = lambda x: x.name == 'a' and x.text.startswith("Cited by")
            cite_link = footer.find(cite_filter)
            if cite_link:
                cite_link = unicode(cite_link.string).strip()
                num_cit_match = pattern.search(cite_link)
                if num_cit_match is not None:
                    num_citations = toInt(num_cit_match.group())
    
        citation = {"name":name, "link":link, "details":details, "year":year, "num_citations":num_citations};
        citations.append(citation)

    return citations

# Collects citations for a list of pages
def parseCitationPages(pages):
    citations = []
    for page in pages:
        page_citations = parseCitations(page)
        citations.extend(page_citations)
        
    return citations
    
# Stores a dictionary in each article recording how many citations it received in each year
def addCounts(articles):
    thisyear = datetime.datetime.now().year + 1
    for a in articles:
        counts = defaultdict(int)
        for c in a['citations']:
            year = c['year']
            # Filter out those without year
            if year > 2000 and year < thisyear:
                counts[year] += 1
        a['citations_count'] = counts    

# Collects all citations for a given user
def fetchAll(url):
    
    if (url == None):
        url = user_url
        
    user_pages = []
    fetchPages(url, user_pages)
    
    print "Parsing user pages to extract articles."
    articles = parseArticlePages(user_pages)
    
    print "Fetching citations."
    for article in articles:
        citations = []
        if (not article['citations_link'] == ''):
            citation_pages = []
            print "Fetching citation pages for article", article['name']
            fetchPages(article['citations_link'], citation_pages)
            print "Parsing citations for article", article['name']
            citations = parseCitationPages(citation_pages)
        article['citations'] = citations
    
    addCounts(articles)
    
    return articles
    
# Returns a short label for the given article    
def label(a):
    return a['name'].replace(" ", "")[0:10] + "_" + str(a['year'])
    
# Prints a csv table of citation counts    
def countsToCsv(articles, fnm):
    # Only those with citations
    arts = [a for a in articles if a['citations_count']]
    
    f = open(fnm, 'w+')
    w = csv.writer(f, delimiter="\t")
    minYear = min([min(a['citations_count'].keys()) for a in arts])
    maxYear = max([max(a['citations_count'].keys()) for a in arts])

    # Header
    header = ["year"]
    for a in arts:
        l = label(a)
        header.append(l)
    w.writerow(header)
    
    for year in range(minYear, maxYear + 1):
        row = [year]
        row.extend([a['citations_count'][year] for a in arts])
        w.writerow(row)
    
# Without citations (exported individually)        
def articlesToCsv(articles, fnm):
    f = open(fnm, 'w+')
    w = csv.writer(f, delimiter="\t")
    fields = [k for k in articles[0].keys() if not (k == "citations" or k == "citations_count")]
    header = ["label"]
    header.extend(fields)
    w.writerow(header)
    
    for a in articles:
        row = [label(a).encode('utf-8')]
        row.extend(unicode(a[k]).encode('utf-8') for k in fields)
        print row
        w.writerow(row)
      
    
def save(artsDat):
    outfile = open('articles.pkl', 'wb')
    pickle.dump(artsDat, outfile)
    outfile.close()
    
def load():
    pkl_file = open('articles.pkl', 'rb')
    articles = pickle.load(pkl_file)
    pkl_file.close()
    
    pprint.pprint(articles)
    return articles
    
if __name__ == "__main__":
    articles = fetchAll(None)
    save(articles)
    articlesToCsv(articles, "js/articles.tsv")
    countsToCsv(articles, "js/counts.tsv")
    
    sys.exit(0)
