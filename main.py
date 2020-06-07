import requests
import json

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
    categories.extend(pageX.getCategoriesFrom())
    categories.extend(pageY.getCategoriesFrom())
    queue.extend(pageX.getLinksFrom())
    flagged.append(pageX)
    #Use BFS to find the closest path between two pages
    for subPage in queue:
        if subPage in [link.name for link in flagged]: continue
        print("{} -> {}".format(" -> ".join(subPage.path), subPage.name))
        subPageLinks = subPage.getLinksFrom()
        if pageY.name in [link.name for link in subPageLinks]:
            print("=" * 20)
            print("\tConnection found using {}".format(subPage.name))
            alerts.append("Connection between {} and {} is {}".format(pageX.name, pageY.name, subPage.name))
            subPage.printDataAbout()
            connection = subPage
            break
        queue.extend(subPageLinks)
        flagged.append(subPage)
        queue.remove(subPage)
    #Now that we've found the connection, let's clear the queue and try reccomend something
    print("\tLooking for reccomendation")
    queue = connection.getLinksFrom()
    flagged = []
    flagged.append(pageX)
    flagged.append(pageY)
    for subPage in queue:
        if subPage.name in [link.name for link in flagged]: continue
        print("Subpage: {}".format(subPage.name))
        if set(categories).isdisjoint(set(subPage.getCategoriesFrom())) == False:
            print("\tFound recommendation using: {}".format(subPage.name))
            alerts.append("Reccomendation for that is {}".format(subPage.name))
            recommendation = subPage
            break
        flagged.append(subPage)
        queue.remove(subPage)
        queue.extend(subPage.getLinksFrom())

    pages.remove(pageX)
    pages.remove(pageY)
    pages.append(recommendation)
    
    
print("=" * 20)
print("===== RESULTS =====")
for alert in alerts:
    print(alert)
print("=" * 20)
