import requests
import json
import copy 
import collections
import random
import math

url = "https://pl.wikipedia.org/w/api.php?"
pages = []
alerts = []
apiCalls = 0

class Page:
    path = []
    def __init__(self, name, path = []):
        self.name = name
        self.path = path
    #Get all links within this page, return a Page list
    def getLinksFrom(self):
        global apiCalls
        links = []
        response = requests.get(url+"action=parse&prop=links&format=json&page={}".format(self.name))
        apiCalls += 1
        #If the page is invalid, return an empty array indicating error
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
        global apiCalls
        categories = []
        response = requests.get(url+"action=parse&prop=categories&format=json&page={}".format(self.name))
        apiCalls += 1
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


# ==== Gather user's input ====
while True:
   inputName = input("\tInput the name of your page: ")
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

# ==== Main algorythm loop ====
while len(pages) != 1:
    print("====== REMAINING PAGES ======")
    print(", ".join(page.name for page in pages))
    print("=" * 30)
    pageX = pages[0]
    pageY = pages[1]
    print("\tLooking for the path between {} -> {}".format(pageX.name, pageY.name))
    connection = None
    
    queue = []
    flagged = []
    
    queue.extend(pageX.getLinksFrom())
    lastLinksFrom = pageX
    # ==== Use BFS to find the closest path between two pages ====
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

    # ==== Suggest recommendation ====
    queue = connection.getLinksFrom()
    random.shuffle(queue)
    recommendation = None
    #Collect categories to find a recommendation later
    categories = [item for item, count in collections.Counter(pageY.getCategoriesFrom() + pageX.getCategoriesFrom()).items() if count > 1]
    if len(categories) == 0: categories.extend(pageY.getCategoriesFrom())
    flagged.clear()
    flagged.append(pageX)
    flagged.append(pageY)
    print("\tLooking for recommendation")
    print("Intrested {} in categories: {}".format(len(categories), categories))
    print("=== Looking for page with more than {} the same categories ===".format(int(2*math.log(len(categories)))))
    #Store a page with the highest amout of relatable categories
    recommendation = [connection, []]
    for subPage in queue:
        #Skip the duplicates
        if subPage.name in [link.name for link in flagged] or subPage.name in [link.name for link in initPages]: continue
        sameCategories = [item for item, count in collections.Counter(categories+subPage.getCategoriesFrom()).items() if count > 1]
        if len(sameCategories) > len(recommendation[1]): recommendation = [subPage, sameCategories]
        if len(recommendation[1]) > int(2*math.log(len(categories))): break
        print("Subpage: {} -> {} categories".format(subPage.name, len(sameCategories)))
        flagged.append(subPage)
        queue.remove(subPage)
    print("The best recommendation is {} with {}".format(recommendation[0].name, len(recommendation[1])))
    alerts.append("\tThe best recommendation is {} with {} of the same categories".format(recommendation[0].name, len(recommendation[1])))
    pages.remove(pageX)
    pages.remove(pageY)
    pages.append(recommendation[0])
    
print("=" * 20)
print("===== RESULTS =====")
for alert in alerts:
    print(alert)
print("Made {} API calls in total".format(apiCalls))
print("=" * 20)
