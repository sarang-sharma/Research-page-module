def duplicheck(seq): 
   noDupes = []
   [noDupes.append(i) for i in seq if not noDupes.count(i)]
   return noDupes

def writetofile(seq): #Function to write publications to a txt file
    outfile = open("pub.txt", "a")
    for item in seq:
        item = item.encode('utf8', 'replace')
        outfile.write("%s\n" %item)
    outfile.close()
    
allpublications = []
pubfile = open('pub.txt', 'r')
#print pubfile.read().decode("utf-8-sig").encode("utf-8")
f = pubfile.read().decode("utf-8-sig").encode("ascii","ignore").splitlines()
for x in f:
    allpublications.append(x)
pubfile.close()


allpublications = duplicheck(allpublications)

print allpublications

writetofile(allpublications)


