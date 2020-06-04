import requests
import json

url = "https://en.wikipedia.org/w/api.php?"
pages = []
queue = []
flagged = []

#Find all the external wiki links inside the specified wiki article
def getLinks(pageName):
    links = []
    print("Page: {}".format(pageName))
    response = requests.get(url+"action=parse&prop=links&format=json&page={}".format(pageName))
    #If the page doesn't exist return empty array
    try:
        data = response.json()["parse"]["links"]
    except:
        return []
    for item in data:
        if item["ns"] != 0: continue
        if item['*'] not in links: links.append(item['*'])
    return links


while True:
    inputPage = input("Input the name of the page: ")
    if inputPage == "": break
    pages.append(inputPage)
    
#Make the number of pages even by adding the first page to the end
if len(pages)%2 == 1:
    pages.append(pages[0])

while len(pages) != 1:
    print("Pages: {}".format(pages))
    page1 = pages[0]
    page2 = pages[1]
    queue.extend(getLinks(page1))
    for subPage in queue:
        #We don't want to visit the same page more than once for one pair
        if subPage in flagged:
            queue.remove(subPage)
            continue
        subPageLinks = getLinks(subPage)
        if page2 in subPageLinks:
            print("-"*20)
            print("{} found in {}".format(pages, subPage))
            print("https://en.wikipedia.org/wiki/{}".format(subPage))
            pages.remove(page1)
            pages.remove(page2)
            pages.append(subPage)
            print("-"*20)
            break
        flagged.append(subPage)
        queue.remove(subPage)
        queue.extend(subPageLinks)
    #Once we found a match for the pair, clear the queue and flagged pages
    flagged.clear()
    queue.clear()

print("The best match is: {}".format(pages[0]))
print("https://en.wikipedia.org/wiki/{}".format(pages[0]))

