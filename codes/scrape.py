import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient 

# this function gets the link for each page and returns it
def get_page_link(link, pages):
    page_link = link + str(pages)
    return page_link

# this function gets the link for each property
def listing_page_link(href):
    property_page = 'https://tonaton.com' + str(href)
    return property_page


# this function makes a request to get the page parses it through beautiful soup and returns the content
def get_soup(link):
    req = requests.get(link)
    src = req.content
    soup = BeautifulSoup(src, "lxml")
    return soup


# This main function extracts the data and posts it into mongodb 
def main():
    # Import MongoClient from pymongo so we can connect to the database
    db_client = MongoClient()
    
    page = 1 # initializing the page
    # This url is the base url for the apartment for rent page of tonaton
    url = 'https://tonaton.com/en/ads/ghana/apartments?by_paying_member=0&sort=date&buy_now=0&urgent=0&type=for_rent&page='
    
    end  = None
    while  True:
        start_link = get_page_link(url,page) # This gets the page_url and puts it in start_link variable
        soup = get_soup(start_link) # parses the link through beautiful soup and stores it in a soup variable
        listings = soup.find_all("ul", class_="list--3NxGO") # this by inspection, this code gets the all the apartment listings and saves the object in a listings variable 
        end = soup.find("div", class_="no-result-text--16bWr")
        

        if end != None: 
            break 

        for links in listings:            
            for href in links.find_all("a"):
                if href['href'] != '/en/promotions':
                    list_url = listing_page_link(href['href'])
                    soup = get_soup(list_url)
                    extracted = {}
                    if soup.find("div", class_="title-container--1PPnS") == None: # This skips apartments which have been rented out
                        continue    
                    Property = soup.find("div", class_="title-container--1PPnS")
                    extracted['Property'] = Property.text
                    
                    extracted["Price"] = soup.find("div", class_="price-section--3xCm3").text

                    features = soup.find("div", class_="ad-meta--17Bqm justify-content-flex-start--1Xozy align-items-normal--vaTgD flex-wrap-wrap--2PCx8 flex-direction-row--27fh1 flex--3fKk1")
                    for div in features:
                        extracted[div.find("div", class_="word-break--2nyVq label--3oVZK").text[:-2]] = div.find("div", class_="word-break--2nyVq value--1lKHt").text
                    db_client.apartment_database.rented_apartment.insert_one(extracted) # This inserts the dictionary into mongodb
                    print("item posted")
        
        print("\n page {0} completed \n".format(page)) # prints to track the number of pages completed
        page +=1

    print("There is no more data")
if __name__ == "__main__":
    main()
   
    
    
