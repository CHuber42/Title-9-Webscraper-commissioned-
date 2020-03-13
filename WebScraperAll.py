import urllib.request
from bs4 import BeautifulSoup
import csv
from selenium import webdriver
import pandas as pd
from selenium.webdriver.chrome.options import Options
import os
import time
from selenium.common.exceptions import NoSuchElementException

###INITIALIZE GLOBAL HOLDERS:
### results: holds all entries which possess the "item-details-link" trait (INCLUDES DUPLICATES)
### governmentjobs_results: holds all novel entries of 'results'; non-duplicates
### driver: the driver instance to get URLs
### myurl: holds the url being accessed (usually job board front-pages)

linkedin_links_list = []
governmentjobs_results = []
number_of_pages = 0

#INITIALIZE BROWSER-DRIVER-CONFIGURATION
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_driver = "C:/bin/phantomjs/bin/chromedriver.exe"


#######################################################################
#def record_results ():





########################################################################

def gj_extract_meaningful_information(result):
    with open("logs/{}".format(time.strftime("%Y-%m-%d, %H-%M")), 'w+') as k :
        k.write("Government Jobs Results:\n")

        for i in result :
            driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
            driver.get(i)
            results_loaded = False
            print(i)
            while results_loaded == False:
                try :
                    pay = driver.find_element_by_xpath("/html/body/div[4]/div[1]/div[1]/div/div/div/div/div[2]/div[1]/div/div[1]/div[1]/div[1]/div[1]/div[2]/div").text
                    job_type = driver.find_element_by_xpath("/html/body/div[4]/div[1]/div[1]/div/div/div/div/div[2]/div[1]/div/div[1]/div[1]/div[2]/div[1]/div[2]/div").text
                    Job_ID = driver.find_element_by_xpath("/html/body/div[4]/div[1]/div[1]/div/div/div/div/div[2]/div[1]/div/div[1]/div[1]/div[3]/div/div[2]/div").text

                    location = driver.find_element_by_xpath("/html/body/div[4]/div[1]/div[1]/div/div/div/div/div[2]/div[1]/div/div[1]/div[1]/div[1]/div[2]/div[2]/div").text
                    department = driver.find_element_by_xpath("/html/body/div[4]/div[1]/div[1]/div/div/div/div/div[2]/div[1]/div/div[1]/div[1]/div[2]/div[2]/div[2]/div").text
                    job_title = driver.find_element_by_xpath('/html/body/div[4]/div[1]/div[1]/div/div/div/div/div[1]/div/div[1]/h2').text
                    posted_date = ""

                    results_loaded = True
                except NoSuchElementException :
                    print("No such element, sleep for 2")
                    time.sleep(2)
                    pass



            driver.close()

            conclusion_list = ("Title: ", job_title, "  ID: ", Job_ID, "  Pay: ", pay, "  Location: ", location, "  Department: ", department,
                    "  Job Type: ", job_type, "  Posted Date: ", "\n")
            conclusion_string = str.join('', conclusion_list)

            k.write(conclusion_string)



##########################################################################################

### THIS FUNC IS ALWAYS CALLED FIRST AND CONTAINS FUNCTIONALITY TO:
### 1. FIND/STRIP HREFs TO JOB LISTINGS ON PAGE 1.
### 2. FIND EXTRA PAGES (2, 3, N) TO GRAB JOB LISTING HREFS FROM
### ---THE # OF EXTRA PAGES IS PASSED TO A GLOBAL, USED FOR LOOPING (gj_extra_pages)
def gj_front_page():
    elements_of_interest = []
    list_found = False
    global number_of_pages
    #OBTAIN MAIN JOB BOARD SITE
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    myurl = "https://www.governmentjobs.com/careers/piercecountywa?"
    driver.get(myurl)

    #FIND THE ELEMENTS (JOB LISTINGS) BY THEIR ITEM-DETAILS-LINK TRAIT


    while list_found == False :
        try:
            elements_of_interest = driver.find_elements_by_class_name('item-details-link')
            if len(elements_of_interest) > 1:
                list_found = True
        except NoSuchElementException:
            print("GJ Front Page List Not Yet Found. Waiting...")
            time.sleep(2)
            pass

    #LOOK UP ELEMENT'S HREF ATTRIBUTE, SAVE TO 2ND CONTAINER
    add_results(elements_of_interest)

    #FIND OTHER PAGES TO ACCESS (?page=2, 3, 4... N)
    print("Checking number of pages on GovernmentJobs.com\n")
    parent_of_pages = driver.find_element_by_class_name('pagination')
    children_of_pages = parent_of_pages.find_elements_by_tag_name('a')

    #LOOP OVER CHILDREN TO FIND THOSE WITH PAGE REFERENCES (len()<13)
    for j in children_of_pages:
        z = len(j.get_attribute('aria-label'))
        if z < 13 :
            number_of_pages += 1

    print("Pages found:", number_of_pages)
    driver.close()

#####################################################################################

### LOOPS OVER EXTRA PAGES OF JOB ENTRIES -
### ASSEMBLES HTTP ADDRESS USING BASIC STRING + PAGE VAR
### THEN OPENS PAGE/FINDS ELEMENTS/EXTRACTS HREF/CALLS RESULTS-ADDING LOOP
def gj_extra_pages():
    print("Grabbing GJ pages after 1st, num of extra pages = ", (number_of_pages - 1))
    for m in range(2,(number_of_pages + 1)):
        list_found = False
        driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
        myurl = str("https://www.governmentjobs.com/careers/piercecountywa?page={}").format(m)
        print("Checking item-details-link objects at: ", myurl)
        driver.get(myurl)

        while list_found == False :
            try:
                elements_of_interest = driver.find_elements_by_class_name('item-details-link')
                if len(elements_of_interest) > 1:
                    list_found = True
            except NoSuchElementException:
                print("GJ 'Extra Pages' List Not Yet Found. Waiting...")
                time.sleep(2)
                pass



        print("Number of elements found: ", len(elements_of_interest))

        add_results(elements_of_interest)
        driver.close()

##########################################################################################

### CALLED AFTER PAGE'S HREFS ARE EXTRACTED: DISCARDS DUPLICATES, APPENDS TO FINAL REPORT
def add_results(elements):
    results = []
    for i in elements:
        job_link = i.get_attribute('href')
        if job_link:
            results.append(job_link)

    for j in results:
        if j not in governmentjobs_results:
            governmentjobs_results.append(j)

##########################################################################################

def get_linkedin ():
    button_found = False


    # Instantiate a webdriver, point to the LI page containing the job listings. DUE TO ODDITIES IN LI'S FORM-POPULATING SCHEME,
    # THIS URL ***MUST*** BE USED, AND NO OTHER. --> Url generated by going to linkedin, clicking on Pierce County's profile page, click 'jobs', click "see all"
    # ANY OTHER METHOD RESULTS IN VERY DIFFERENT HTML AND THIS WILL NOT WORK ON IT.
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    myurl = "https://www.linkedin.com/jobs/search?locationId=OTHERS.worldwide&f_C=231967&trk=job-results_see-all-jobs-link&redirect=false&position=1&pageNum=0"
    driver.get(myurl)

    time.sleep(8)
    try :
        button = driver.find_element_by_xpath('/html/body/main/div/section/button')
        button.click()
    except NoSuchElementException:
        pass
    #Find and click the "see more jobs" button, then wait for the JS to finish executing before grabbing page source


    time.sleep(2)
    # Grab Page Source
    soup = BeautifulSoup(driver.page_source)

    # Grab all 'a' tags in the page. For all 'a' tags, and compare them to a filter. If the class filter matches,
    # grab the href attribute and save it to the linkedin_links_list holder, for utilization later.
    for link in soup.find_all('a'):

        class_filter = str(link.get('class'))
#
        if 'full-card-link' in class_filter:
#
            linkedin_links_list.append(link.get('href'))

    driver.close()



def main():
    gj_front_page()
    gj_extra_pages()
    #get_linkedin()

    print("Government Jobs Results: ", len(governmentjobs_results))
    print("LinkedIn Results: ", len(linkedin_links_list))

    gj_extract_meaningful_information(governmentjobs_results)


main()
