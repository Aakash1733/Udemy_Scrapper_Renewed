from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import warnings
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.core.utils import ChromeType
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import sys
import datetime
from pathlib import Path
import chromedriver_binary
#import chromedriver_autoinstaller
#chromedriver_autoinstaller.install()
warnings.filterwarnings('ignore')
chrome_options = Options()
chrome_options.add_experimental_option('detach', True)
chrome_options.add_argument('--headless')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
#webdriver = webdriver.Chrome(executable_path='chromedriver.exe',)
#fpath = Path(r"chromedriver.exe").absolute()
def second_site(mydate=0,record_count=50,retry_limit=1):
    print("The final output file can be downloaded using Download button once the process is finished")
    print("|**SEVERAL PAGES WILL OPEN AND CLOSE AUTOMATICALLY FOR BEST SCRAPPING EXPERIENCE **|")
    driver = webdriver.Chrome(options=chrome_options)
    driver2=webdriver.Chrome(options=chrome_options)
    url = 'https://www.real.discount/udemy-coupon-code/'
    # Navigate to the webpage
    print("Starting the browser for ",url)
    driver.get(url)
    driver.implicitly_wait(30)
    # Find the element by its ID
    wait=WebDriverWait(driver,30)
    #limit_of_links=50
    links = [] #links of second page
    useful_links=[] #udemy links
    load_more_button_selector = "input.btn.btn-primary[type='button'][onclick^='load_all']" # replace with the CSS selector for the button

    # wait for the button to appear
    wait = WebDriverWait(driver, 10) # wait up to 10 seconds
    print("Searching the Load More button of the page")
    load_more_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, load_more_button_selector)))
    links = []
    pinks=[]
    zz=0
    while True:
        
            pinks=links+pinks
            links=[]
            try:
                load_more_button.click()
                time.sleep(10)
            except:
                 break
            list_element = driver.find_element(By.ID,"myList")
            list_items = list_element.find_elements(By.TAG_NAME,"li")
            for item in list_items:
                link_element = item.find_element(By.TAG_NAME,"a")
                link = link_element.get_attribute("href")
                if "real.discount/offer" in link and link not in pinks:
                    links.append(link)
                    print("Adding ",link," in the queue")

            # do something with the links, e.g. print them
            for i in links:
                print("Opening the browser for the link page")
                driver2.get(i)
                time.sleep(5)
                retry_count=0
                max_retry=retry_limit
                while retry_count<max_retry:
                    if zz==22:
                        return
                    try:
                        oururl=driver2.find_element(By.LINK_TEXT,'Get Coupon').get_attribute('href')
                        #print(oururl)
                        print("Adding the udemy course link to the list")
                        useful_links.append(oururl)
                        print("Sending the Udemy links for validation")
                        try:
                            zz=check_course_on_udemy(oururl,mydate,record_count,retry_limit)
                            break
                        except:
                            zz=5
                    except:
                        retry_count +=1
                        time.sleep(5)
                        print("Retrying")

            # wait for the page to load
            

    # get the links from the list items
    # close the driver
    print("Exiting the search process for site ",url)
    driver.quit()

def check_course_on_udemy(url,mydate,record_count,retry_limit):
    data = []
    # Start a new browser session
    driver3 = webdriver.Chrome(executable_path='chromedriver.exe',options=Options().add_experimental_option('excludeSwitches', ['enable-logging']))
    print("Starting Browser for Udemy Scanner")
    # Navigate to the webpage
    driver3.get(url)
    driver3.implicitly_wait(20)
    # Find the element by its ID
    try:
        print("Trying to locate the Price of course on Udemy")
        elements = driver3.find_elements(By.CSS_SELECTOR, 'div[class*="price-text--price-part"]')
    except:
        print("Not a valid page")
        return 5
    print("Getting the Title of Course")
    Title=driver3.find_elements(By.TAG_NAME, 'h1')
    print("Getting the Date when this course was last modified on Udemy")
    Expdate=driver3.find_elements(By.CSS_SELECTOR,'div[class="last-update-date"]')
    for dat in Expdate:
        faaltu=dat.text
        first_half=int(faaltu[faaltu.index("/")+1:])*100
        second_half=int(faaltu[faaltu.index("/")-2:faaltu.index("/")])
        final_faaltu=first_half+second_half
        print(final_faaltu)
    a=[]
    print("Extracting the course current price and original price")
    for element in elements:
        try:
            if element.text!="":
                CurrentP=element.find_elements(By.TAG_NAME, 'span')
                a.append(element.text.strip("\n"))
        except:
            break
    print("Checking the course for matching the input parameters")
    if 2<=len(a) and "Free" in a[0] and mydate<=final_faaltu:
        print("Found a Free Course")
        for title in Title:
            print(title.text)
        urli=driver3.current_url
        coupon_code=urli[urli.index("=")+1:]
        edited_url=urli[:urli.index("?")]
        print(coupon_code)
        print(edited_url)
        try:
            Coupexp=driver3.find_elements(By.CSS_SELECTOR,'div[class*="discount-expiration--discount-expiration"]')
            for coupdate in Coupexp:
                dategap=coupdate.text[0:2]
            if dategap != "NA" or dategap!="":
                current_date = datetime.date.today()
                future_date = current_date + datetime.timedelta(days=int(dategap))
                print(future_date)
        except:
            future_date= "NA"
        data.append((title.text, edited_url,coupon_code,future_date))
        if len(global_var)==record_count:
            print(len(global_var))
            print("Task Successfully Completed")
            return 22
        for row in data:
            print("Writing the data in the csv file")
            global_var.loc[len(global_var)] = row
        #results = pd.read_csv('Data.csv')
        #if len(results)==count_records:
            #return 22
        print('Record Saved Successfully!')
    elif len(a)<2:
        print("The course is already Free")
        return 9
    elif mydate>final_faaltu:
        print("The course is older than the provided date")
        print("Checking the next record..")
        return 6
    else:
        print("OOPS !! either course is already free or the coupon expired ..")
        print("Moving on to the next link")
        return 7

# Start a new browser session
def third_site(mydate=0,record_count=50,retry_limit=1):
    print("The final output file can be downloaded using Download button Anytime")
    # Start a new browser session
    driver5 = webdriver.Chrome(executable_path='chromedriver.exe',options=chrome_options)
    url="https://www.onlinecourses.ooo/"
    driver4=webdriver.Chrome(executable_path='chromedriver.exe',options=chrome_options)
    print("Starting the browser for main page")
    driver4.get(url)
    driver4.implicitly_wait(30)
    # Find the element by its ID
    wait=WebDriverWait(driver4,30)
    limit_of_links=50
    links = [] #links of second page
    useful_links=[] #udemy links
    while True:
        if len(useful_links)>=limit_of_links:
            driver4.quit()
            print(useful_links)
            break
        else:
            #time.sleep(20)
            elements = driver4.find_elements(By.TAG_NAME,'h3') # replace 'div.example-class a' with the CSS selector for the links you want to scrape
            for element in elements:
                anchor_tag= element.find_element(By.TAG_NAME,"a")
                link = anchor_tag.get_attribute('href')
                links.append(link)
                #print(link)
            for i in links:
                print("Starting the browser for subpage")
                driver5.get(i)
                #time.sleep(10)
                print("Trying to collect the Udemy link")
                oururl=driver5.find_element(By.CSS_SELECTOR,'a[class="coupon-code-link"]').get_attribute('href')
                print("Adding the Udemy link for scanning")
                useful_links.append(oururl)
                print("Sending udemy links to scrap courses")
                if check_course_on_udemy(oururl,mydate,record_count,retry_limit)==22:
                    return
                #print(oururl)
            links=[]
        # move to the next page (if there is one)
        print("Searching for the next button")
        next_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#content > div.content-box > div > div.paging > div.pages > a.next.page-numbers'))) # replace 'button.next-page' with the CSS selector for the next page button (if there is one)
        if next_button:
            driver4.execute_script('arguments[0].click();',next_button)
            print('Moving to next page...')
        else:
            print('No more pages to scrape!')
            break
    # close the driver
    print("Exiting the search process for site ",url)
    driver4.quit()

def first_site(mydate=0,record_count=50,retry_limit=1):
    print("The final output file can be downloaded using Download button ANYTIME")
    useless=["https://couponscorpion.com/category/100-off-coupons/","https://couponscorpion.com/category/free100-discount/"]
    driver = webdriver.Chrome(executable_path='chromedriver.exe',options=chrome_options)
    print("Starting browser")
    driver2=webdriver.Chrome(executable_path='chromedriver.exe',options=chrome_options)
    url = 'https://couponscorpion.com/category/100-off-coupons/'
    # Navigate to the webpage
    print("Searching the URL ",url)
    driver.get(url)
    driver.implicitly_wait(30)
    # Find the element by its ID
    wait=WebDriverWait(driver,30)
    links = [] #links of second page
    useful_links=[] #udemy links
    while True:
        elements = driver.find_elements(By.XPATH,'//a[starts-with(text(), "100%")]') # replace 'div.example-class a' with the CSS selector for the links you want to scrape
        for element in elements:
            link = element.get_attribute('href')
            print("Checking the link for any issues")
            if link not in useless:
                print("Link scannable adding it to the main page search list")
                links.append(link)
        print("Now scanning the second page of website for links of Udemy")
        zz=0
        for i in links:
            driver2.get(i)
            time.sleep(10)
            retry_count=0
            max_retry=retry_limit
            while retry_count<max_retry:
                if zz==22:
                    return
                try:
                    oururl=driver2.find_element(By.LINK_TEXT,'GET COUPON CODE').get_attribute('href')
                    useful_links.append(oururl)
                    print("Found an Udemy Link")
                    print("Sending the website link to Udemy Scanner")
                    zz=check_course_on_udemy(oururl,mydate,record_count,retry_limit)
                    break
                except:
                    retry_count +=1
                    time.sleep(5)
                    print("Retrying")
        #driver2.quit()
        links=[]
        #print(useful_links)



        # move to the next page (if there is one)
        print("Searching for next button on the page")
        next_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'body > div.rh-outer-wrap > div > div > div > ul > li.next_paginate_link > a'))) # replace 'button.next-page' with the CSS selector for the next page button (if there is one)
        if next_button:
            driver.execute_script('arguments[0].click();',next_button)
            print('Moving to next page...')
        else:
            print('No more pages to scrape!')
            break
    #print(links)
    # close the driver
    print("Exiting the search process for site ",url)
    driver.quit()
defaultrow = ("Course Name", "Course URL", "Coupon Code", "Expiration Date")
df = pd.DataFrame(columns=defaultrow)
global_var= df
#second_site(mydate=0,record_count=10,retry_limit=1)
#first_site(mydate=0,record_count=10,retry_limit=1)
#third_site(mydate=0,record_count=10,retry_limit=1)
