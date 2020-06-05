import requests
import json

#https://en.wikipedia.org/w/api.php?action=query&cmlimit=max&list=categorymembers&cmnamespace=0&format=json&cmtitle=Category:Physics

url = "https://pl.wikipedia.org/w/api.php?"
pages = []
queue = []
flagged = []
msgs = []

#Find all the external wiki links inside the specified wiki article
def getLinks(pageName):
    links = []
    print("Page: {}".format(pageName[-1]))
    response = requests.get(url+"action=parse&prop=links&format=json&page={}".format(pageName[-1]))
    #If the page doesn't exist return empty array
    try:
        data = response.json()["parse"]["links"]
    except:
        return []
    for item in data:
        if item["ns"] != 0: continue
        if item['*'] not in links: 
            temp = [item for item in pageName]
            temp.append(item['*'])
            links.append(temp)
    return links

def getCategories(pageName):
    categories = []
    #Get all categories from the pages
    print("Page: {}".format(pageName))
    response = requests.get(url+"action=parse&prop=categories&format=json&page={}".format(pageName))
    #If the page doesn't exist return empty array
    try:
        data = response.json()["parse"]["categories"][::-1]
    except:
        return categories
    for item in data:
        if "hidden" in item.keys(): continue
        categories.append(item["*"])
    return categories
    
        

def getCurrentLinks(linkHistory):
    links = [item[-1].lower() for item in linkHistory]
    return links

while True:
    inputPage = input("Input the name of the page: ")
    if inputPage == "": break
    pages.append(inputPage)    
#Make the number of pages even by adding the first page to the end
if len(pages)%2 == 1:
    pages.append(pages[0])


while len(pages) != 1:
    print("-"*50)
    print("Pages: {}".format(pages))
    page1 = pages[0]
    page2 = pages[1]
    print("Looking for connection between {} and {}".format(page1, page2))
    print("-"*50)
    middleItem = None
    reccomended = None
    #Collect categories to propose an object later
    categories = []
    categories.extend(getCategories(page1))
    categories.extend(getCategories(page2))
    queue.extend(getLinks([page1]))
    for subPage in queue:
        currentPage = subPage[-1]
        #We don't want to visit the same page more than once for one pair
        if currentPage in flagged:
            queue.remove(subPage)
            continue
        
        subPageLinks = getLinks(subPage)
        if page2.lower() in getCurrentLinks(subPageLinks):
            print("-"*20)
            alert = "{} found in:  {} -> {}".format(pages[1], " -> ".join(subPage), pages[1])
            print(alert)
            subPage.append(pages[1])
            middleItem = subPage[len(subPage)//2]
            msgs.append(alert)
            print("https://en.wikipedia.org/wiki/{}".format(subPage[-2]))
            pages.remove(page1)
            pages.remove(page2)
            print("-"*20)
            break
        flagged.append(currentPage)
        queue.remove(subPage)
        queue.extend(subPageLinks)
    #Once we found a match for the pair, clear the queue and flagged pages
    flagged.clear()
    queue.clear()
    #Now that we've found the relatable item, let's suggest a new one using the categories
    #We have our page and want to find the page within it that contains the category
    flagged.append(page1)
    flagged.append(page2)
    queue.extend(getLinks([middleItem]))
    for subPage in queue:
        currentPage = subPage[-1]
        #We don't want to visit the same page more than once for one pair
        if currentPage in flagged:
            queue.remove(subPage)
            continue
        
        subPageCategories = getCategories(currentPage)
        if set(categories).isdisjoint(set(subPageCategories)) == False:
            print("-"*20)
            alert = "{} found in:  {}".format(categories, currentPage)
            reccomended = currentPage
            print(alert)
            print("-"*20)
            break
    #If found a reccomended page, use it to determine the next pages in queue
    #Otherwise use the middleItem
    if reccomended == None:
        print("Could not recommend a page :(")
        reccomended = middleItem
        pages.append(reccomended)
    else:
        print("I reccomend {}!".format(reccomended))
        pages.append(reccomended)
    msgs.append("Recomendation for that is {}".format(reccomended))
    print(pages)
    flagged.clear()
    queue.clear()
        
    
print("-"*50)
print("\t\tRESULTS")
print("-"*50)
for message in msgs:
    print(message)

print("-" * 20)
print("The best match is: {}".format(pages[0]))
print("https://en.wikipedia.org/wiki/{}".format(pages[0]))

