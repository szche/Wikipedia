import requests
import json

url = "https://en.wikipedia.org/w/api.php?"
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
    print("Pages: {}".format(pages))
    page1 = pages[0]
    page2 = pages[1]
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
            alert = "{} found in:  {}".format(pages[1], " -> ".join(subPage))
            print(alert)
            msgs.append(alert)
            print("https://en.wikipedia.org/wiki/{}".format(subPage[-1]))
            pages.remove(page1)
            pages.remove(page2)
            pages.append(subPage[-1])
            print("-"*20)
            break
        flagged.append(subPage[-1])
        queue.remove(subPage)
        queue.extend(subPageLinks)
    #Once we found a match for the pair, clear the queue and flagged pages
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

