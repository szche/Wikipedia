import requests
import json
import copy 
import collections
import random

url = "https://pl.wikipedia.org/w/api.php?"
pages = []
alerts = []

class Page:
    path = []
    def __init__(self, name, path = []):
        self.name = name
        self.path = path
        
    #Get all links within this page, return a Page list
    def getLinksFrom(self):
        links = []
        #print("Checking for links in {}".format(self.name))
        response = requests.get(url+"action=parse&prop=links&format=json&page={}".format(self.name))
        #If the page is invalid, return "-1" indicating error
        try: data = response.json()["parse"]["links"]
        except: return links
        #Loop the gathered items and throw away all the Helpers etc.
        for item in data:
            if item["ns"] != 0 or item['*'] in links: continue
            subPage = Page(item["*"], self.path + [self.name])
            links.append(subPage)
        return links
        
    #Get all categories within this page
    def getCategoriesFrom(self):
        categories = []
        #print("Checking for categories in {}".format(self.name))
        response = requests.get(url+"action=parse&prop=categories&format=json&page={}".format(self.name))
        try: data = response.json()["parse"]["categories"][::-1]
        except: return categories
        for item in data:
            if "hidden" in item.keys() or item["*"] in categories: continue
            categories.append(item["*"])
        return categories
        
    #Print information about this Page
    def printDataAbout(self):
        print("="*30)
        print("Page name: {}".format(self.name))
        print("Page path: {} -> {}".format(" -> ".join(self.path), self.name))
        print("="*30)


#Gather user's input
while True:
   print("=" * 20)
   inputName = input("Input the name of your page: ")
   if inputName == "": break
   inputPage = Page(inputName)
   if inputPage.getLinksFrom() == [] or inputPage.getCategoriesFrom() == []:
        print("There's something wrong with the link, try again!")
        continue
   pages.append(inputPage)
   
if len(pages) < 2:
    print("Not enough items to determine connections :(")
    exit()

if len(pages)%2 == 1: pages.append(pages[0])

initPages = copy.deepcopy(pages)

#Main algorythm loop
while len(pages) != 1:
    print("=" * 20)
    print("====== PAGES ======")
    for page in pages:
        print(page.name)
    print("=" * 20)
    pageX = pages[0]
    pageY = pages[1]
    print("\tLooking for the path between {} -> {}".format(pageX.name, pageY.name))
    connection = None
    recommendation = None
    queue = []
    flagged = []
    categories = []
    #categories.extend(pageX.getCategoriesFrom())
    #categories.extend(pageY.getCategoriesFrom())   
    categories = [item for item, count in collections.Counter(pageY.getCategoriesFrom() + pageX.getCategoriesFrom()).items() if count > 1]
    if len(categories) == 0:
        categories.extend(pageX.getCategoriesFrom())
    
    queue.extend(pageX.getLinksFrom())
    #flagged.append(pageX)
    lastLinksFrom = pageX
    #Use BFS to find the closest path between two pages
    for subPage in queue:
        if subPage.name in [link.name for link in flagged] or subPage.name in [link.name for link in pages]: continue
        subPageLinks = subPage.getLinksFrom()
        if pageY.name in [link.name for link in queue]:
            print("=" * 20)
            print("\tConnection found using {}".format(lastLinksFrom.name))
            alerts.append("Connection between {} and {} is {}".format(pageX.name, pageY.name, lastLinksFrom.name))
            connection = lastLinksFrom
            break
        print("{} -> {}".format(" -> ".join(subPage.path), subPage.name))
        flagged.append(lastLinksFrom)
        lastLinksFrom = subPage
        queue.remove(subPage)
        queue.extend(subPageLinks)

    #Now that we've found the connection, let's clear the queue and try reccomend something
    print("\tLooking for reccomendation")
    print(categories)
    queue = connection.getLinksFrom()
    random.shuffle(queue)
    flagged = []
    flagged.append(pageX)
    flagged.append(pageY)
    recommendation = [connection, []]
    for subPage in queue:
        if subPage.name in [link.name for link in flagged] or subPage.name in [link.name for link in pages]: continue
        sameCats = [item for item, count in collections.Counter(categories+subPage.getCategoriesFrom()).items() if count > 1]
        # encounters.append([subPage.name, len(sameCats)])
        if len(sameCats) > len(recommendation[1]):
            recommendation = [subPage, sameCats]
        if len(recommendation[1]) == len(categories):
            break
        print("Subpage: {}\t\t{} categories".format(subPage.name, len(sameCats)))
        flagged.append(subPage)
        queue.remove(subPage)
    print("The best recommendation is {} with {}".format(recommendation[0].name, len(recommendation[1])))
    alerts.append("The best recommendation is {} with {} of the same categories".format(recommendation[0].name, len(recommendation[1])))
    
    pages.remove(pageX)
    pages.remove(pageY)
    pages.append(recommendation[0])
    
    
print("=" * 20)
print("===== RESULTS =====")
for alert in alerts:
    print(alert)
print("=" * 20)
