contents = open("pub.txt","r")

with open("pubs.html", "w") as e:
    e.write('<html>')
    e.write('<body>')
    e.write('<ul>')
    for lines in contents.readlines():
        e.write('\t<li>'+lines +'</li>')
    e.write('</ul>')
    e.write('</body>')
    e.write('</html>')
