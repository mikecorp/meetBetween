import shlex, subprocess
import os
import sys
import time
import networkx as nx
import xml.dom.minidom
import heapq


def findCheapest():
  results = xml.dom.minidom.parse("ksearchresults.xml")

  trip = results.documentElement.getElementsByTagName('trip')
  flightData = {}
  simple = {}
  orig = ""
  dest = ""
  #id=0
  for t in trip:
    #id +=1  #FIXME t.attributes( 'id' )
    id= t.attributes['id'].value
    price = t.getElementsByTagName( 'price' )[0].childNodes[0].nodeValue
    url = t.getElementsByTagName('price')[0].attributes['url'].value
    print "the currentPrice is",price
    for lg in t.getElementsByTagName( 'legs'):
      departs = []
      arrives = []
      for l in lg.getElementsByTagName( 'leg'):
        dest = l.getElementsByTagName( 'dest')[0].childNodes[0].nodeValue
        orig = l.getElementsByTagName( 'orig')[0].childNodes[0].nodeValue
        departs.append(l.getElementsByTagName( 'depart')[0].childNodes[0].nodeValue) 
        arrives.append(l.getElementsByTagName( 'arrive')[0].childNodes[0].nodeValue)
        #dict[orig] = price
        flightTime = 0
        for s in l.getElementsByTagName('segment'):
          flightTime+=int(s.getElementsByTagName('duration_minutes')[0].childNodes[0].nodeValue)
    if id in flightData.keys() : exit(3)
    flightData[id]= price,orig,dest,flightTime,arrives,departs,id,url
    simple[id] = price
  #for o,d,id in dict.keys():
   #print o,d,id,dict[o,d,id]
  simpleB = dict(map(lambda item: (item[1],item[0]),simple.items()))
  minID = simpleB[min(simpleB.keys())]
  print "THIS IS THE MIN price",simple[minID]
  return flightData[minID] #return firstKey


#returns false if just flying from source to source is cheaper
def compareWithSource2Source(cheapestMeetPrice,source):
  cmd = ['ruby','kayak.rb','f',source[0],source[1],outDate,returnDate]
  retCode = subprocess.call(cmd)
  if (retCode != 0):
    print "[Error] did not work as expected!"
    sys.exit(2) #unknown error
  price1,orig,dest,flightTime,arrive,depart,id,url = findCheapest()
  #now check s1 to s
  cmd = ['ruby','kayak.rb','f',source[1],source[0],outDate,returnDate]
  retCode = subprocess.call(cmd)
  if (retCode != 0):
    print "[Error] did not work as expected!"
    sys.exit(2) #unknown error
  price2,orig,dest,flightTime,arrive,depart,id,url = findCheapest()
  if min(price1,price2) < cheapestMeetPrice:
    print "min cost of flying to each other",min(price1,price2),"compared to min meet",cheapestMeetPrice
    return False
  else: return True 


#start main

G=nx.DiGraph()

#make all of these options

outDate = '02/11/2011'
returnDate = '02/14/2011'

checkSourcetoSource = True

cmd = ['ruby','kayak.rb','h']

source = ['sfo','pit']

#port = ['den','phx']
port = ['den','phx','las','chi','bos','jfk','lax']

outer=-1

flightAttributes = {}

for s in source:
  outer+=1 #outer kludge will only work with 2 sources
  S = s #saveSource for kludge
  for p in port:
    if outer == 1: #kludge1
      s=p
      p=S
    cmd = ['ruby','kayak.rb','f',s,p,outDate,returnDate]
    print cmd
    retCode = subprocess.call(cmd)
    if (retCode != 0):
      print "[Error] did not work as expected!"
      sys.exit(2) #unknown error
    price,orig,dest,flightTime,arrive,depart,id,url = findCheapest()
    print price,"THIS IS CHEAPEST PRICE"
    if outer == 1:  #to ensure proper key
      flightAttributes[(S,s)] = price,orig,dest,flightTime,arrive,depart,id,url
    else:
      flightAttributes[(s,p)] = price,orig,dest,flightTime,arrive,depart,id,url
    #uses xml created by previous call
    print price
    G.add_edge(str(s),str(p),weight=int(price))

print "Findcheap has finished searching" 
shortestPath= nx.shortest_path(G,'sfo','pit',weighted=True)
cheapestMeetCost = nx.shortest_path_length(G,'sfo','pit',weighted=True)

print "combined cost",cheapestMeetCost
print "shortestPath",shortestPath
print "for depart and return date",outDate,returnDate

if checkSourcetoSource is True:
  if compareWithSource2Source(cheapestMeetCost,source) is False:
    print "just fly source2source"
    sys.exit()


sourceOneFlight = shortestPath[0],shortestPath[1]
sourceTwoFlight = shortestPath[2],shortestPath[1] #reversed due to kludge1


print "SourceOne\n"
print flightAttributes[sourceOneFlight]
print sourceOneFlight

print "SourceTwo\n"
print flightAttributes[sourceTwoFlight]
print sourceTwoFlight
print "sources"
print source
#print nx.shortest_path(G,'pit',target=None,weighted=True)
