import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException


log_file = open("logs/{}".format(time.strftime("%Y-%m-%d, %H-%M")), 'a+') # Create record and open for writing


#INITIALIZE BROWSER-DRIVER-CONFIGURATION
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_driver = "C:/bin/phantomjs/bin/chromedriver.exe"

##################################################################################
##################################################################################
##################################################################################

### Used repeatedly to confirm a page's necessary elements have loaded for accessing

def confirm_load(flagging_string, driver):
    success = False
    while success == False:
        try:
            exec(flagging_string)
            success = True
        except NoSuchElementException:
            time.sleep(1)
            pass
        except ElementClickInterceptedException:
            time.sleep(1)
            pass


##########################################################################################
##########################################################################################
##########################################################################################

### This func first accesses the GovernmentJobs board and checks it for the number
### of pages (pagination schema) to loop over/grab results from.

def gj_initialize():

#OBTAIN MAIN JOB BOARD SITE
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    myurl = "https://www.governmentjobs.com/careers/piercecountywa?"
    driver.get(myurl)

    confirm_load("test = driver.find_element_by_class_name('pagination')", driver)      # Load test that pagination is countable
    pagination_list = driver.find_element_by_xpath('/html/body/div[4]/div[1]/div[1]/div/div[3]/div[1]/div[3]/div[1]/div[1]/ul')
    number_of_pages = (len(pagination_list.find_elements_by_tag_name("li")) - 2)        # Locate pagination UL, count Li tags,
                                                                                        # Remove 2 for "Previous" and "Next" buttons

    print("Pages found:", number_of_pages)          # Just a reporter line to confirm everything is running correctly

    driver.close()                                  # We're done with this, and to avoid it "crashing open" in later steps, close it first.

    gj_grab_pages(number_of_pages)                  # Now go loop over the pages for results-stripping.


#####################################################################################

### This func opens a given page of results on governmentjobs and scans it
### for list item holders with the tag <tr>, then extracts some salient data:
### It passes the href for each job post, as well as a dict of [job_title] = when_the_job_was_posted
### These are subsequently used to load a page, extract results, and format a report entry.

def gj_grab_pages(number_of_pages):

    log_file.write("Government Jobs Results:\n")
    for m in range(1,(number_of_pages)):            # Just use the imported index to loop over governmentjobs pages

        driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
        myurl = str("https://www.governmentjobs.com/careers/piercecountywa?page={}").format(m)
        driver.get(myurl)

        confirm_load("test = driver.find_elements_by_tag_name('tr')", driver)       # Confirm the job results list is loaded
        elements_of_interest = driver.find_elements_by_tag_name('tr')
        elements_of_interest.pop(0)                                                 # First tr tag is header - Remove it

        print("Number of posts found: ", len(elements_of_interest))                 # Quick verification of results

        gj_extract_meaningful_information(elements_of_interest, driver)

        driver.close()                                                              # As before: close it in case
                                                                                    # of "crashing open" in subsequent steps

########################################################################

### This is the log writer. It looks up an Href from a list passed to it,
### verifies successful load of the page (See line 41 if necessary),
### then extracts and formats those values into a log entry which is then written.
### Unfortunately the "date posted" attribute isn't available on the main job's
### page, so we have to pass it in from the board where we stripped the href values
### - Thus the posted_dict.

def gj_extract_meaningful_information(result, driver):
    try:                                                                            # Dismiss the "accept cookies" button if present
        driver.find_element_by_xpath("/html/body/div[4]/div[1]/div[2]/div/button").click()
    except NoSuchElementException:
        pass


    for i in result :                                                               # I don't know how to pass i to confirm_load
        while True:                                                                 # So this check happens locally
            try:                                                                    # Functionality: open Job's main post in sidebar
                i.find_element_by_class_name("item-details-link").click()
                break
            except ElementClickInterceptedException:
                time.sleep(1)
                pass

                                                                                    # Confirm side-bar is loaded for element extraction
        confirm_load("test = driver.find_element_by_xpath('/html/body/div[8]/div/div[1]/div[2]/div/div[1]/div[1]/div[1]/div[2]/div[2]/div').text", driver)

                                                                                    # Extract/Assign attributes for logging
        pay = i.find_element_by_class_name("job-table-salary").text
        job_title = i.find_element_by_class_name("item-details-link").text
        Job_ID = i.find_element_by_class_name("job-table-title").get_attribute("data-job-id")
        job_href = i.find_element_by_class_name("item-details-link").get_attribute("href")
        pay = i.find_element_by_class_name("job-table-salary").text
        job_type = i.find_element_by_class_name("job-table-type")
        department = i.find_element_by_class_name("job-table-department").text
        posted_date = i.find_element_by_class_name("job-table-posted").text
        href = i.find_element_by_class_name("item-details-link").get_attribute('href')

        location = driver.find_element_by_xpath("/html/body/div[8]/div/div[1]/div[2]/div/div[1]/div[1]/div[1]/div[2]/div[2]/div").text
        job_number = driver.find_element_by_xpath("/html/body/div[8]/div/div[1]/div[2]/div/div[1]/div[1]/div[3]/div/div[2]/div").text

                                                                                    # Hit the "X" button to prep for next post
                                                                                    # This attempt repeats until succeeded
        confirm_load("driver.find_element_by_xpath('/html/body/div[8]/div/div[1]/div[1]/button').click()", driver)


        conclusion_list = ("Title: ", job_title, "  ID: ", Job_ID, "  Job Numer: ", job_number, "  Pay: ", pay,
                            "  Location: ", location, "  Department: ", department, "  Job Type: ", job_type,
                            "  Posted Date: ", posted_date,  "  Href: ", href, "\n")
        conclusion_string = str.join('', conclusion_list)
        log_file.write(conclusion_string)



##########################################################################################
##########################################################################################
##########################################################################################

### LinkedIn uses a very different results publisher from GovernmentJobs; as with GJ
### There is (unique) salient data in both the listing plate and the main page, so we must
### access both. Also, LinkedIn doesn't use pagination unless you're logged in, (which we aren't doing)
### so we have to use a system for checking if the "show more jobs" button is present, and if so, pressing it.
### However, that also is a bit beyond us atm, so instead we just attempt to click the
### "See more jobs" button 5 times and then exit. We don't expect the results to be > 125 so this
### should be safe.

def get_linkedin ():
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    myurl = "https://www.linkedin.com/jobs/search?locationId=OTHERS.worldwide&f_C=231967&trk=job-results_see-all-jobs-link&redirect=false&position=1&pageNum=0"
    driver.get(myurl)

    confirm_load("test = driver.find_element_by_xpath('/html/body/main/div/section/ul')", driver)

# This loop (safely) attempts to expand the jobs results list up to 125

    try:
        for i in range(0,5):
            button = driver.find_element_by_xpath('/html/body/main/div/section/button')
            button.click()
            time.sleep(1)
    except NoSuchElementException:
        pass

    unordered_list = driver.find_element_by_xpath("/html/body/main/div/section/ul")     # Quick filtering to find only the list items we're
    list_items = unordered_list.find_elements_by_tag_name("li")                         # Looking for.

    push_linkedin_results(list_items, driver)                                           # Push the results; the "smart" implementation for this requires
                                                                                        # handing it the HTML, so don't driver.close() until after.
    driver.close()                                                                      # Clean up after ourselves.

#####################################################################################

### Logic: for each result in the left-handled list, click it to "slide out" a modular
### version of the main post. Verify that has been done. Upon verification, strip out
### the relevant data from each side; some come from the results placard (i.element)
### Others from the job-page-preview (driver.element)

def push_linkedin_results(list_items, driver):
    log_file.write("\n\nLinkedIn Results:\n")

    for i in list_items:
        i.click()                               # Click the element to call its full-page-preview
        time.sleep(1)                           # Pause to ensure JS has had adequate time to update the page

# Pseudo-standard "was it loaded correctly" verification. See line 41 for details.
# Extra component: a second flag (reload_index) in case loading has stalled and needs
# to be re-initiated.
        full_page_loaded = False
        reload_index = 0
        confirm_load("seniority_level =  driver.find_element_by_xpath('/html/body/main/section/div[2]/section[2]/ul/li[1]/span').text", driver)

# Grab a bunch of data from i.stuff or driver.stuff for formatting into a line to log
        href = i.find_element_by_class_name("result-card__full-card-link").get_attribute('href')
        job_title = i.find_element_by_class_name("result-card__title").text
        job_location =  i.find_element_by_class_name("job-result-card__location").text
        job_publisher =  i.find_element_by_class_name("result-card__subtitle-link").text
        posting_date = i.find_element_by_class_name("job-result-card__listdate").get_attribute('datetime')
        job_function =  driver.find_element_by_xpath("/html/body/main/section/div[2]/section[2]/ul/li[3]/span").text
        job_industry =  driver.find_element_by_xpath("/html/body/main/section/div[2]/section[2]/ul/li[4]/span").text
        employment_type =  driver.find_element_by_xpath("/html/body/main/section/div[2]/section[2]/ul/li[2]/span").text
        seniority_level =  driver.find_element_by_xpath("/html/body/main/section/div[2]/section[2]/ul/li[1]/span").text

# Format the data, write the line in the logs
        conclusion_list = ("Title: ", job_title, "  Location: ", job_location, "  Employment Type: ", employment_type,
                            "  Posted Date: ", posting_date,  "  Publisher: ", job_publisher, "  Seniority Level: ", seniority_level, "  Job Functions: ", job_function,
                            "  Job Industry: ", job_industry, "  Href: ", href, "\n")
        conclusion_string = str.join('', conclusion_list)
        log_file.write(conclusion_string)




#####################################################################################
#####################################################################################
#####################################################################################


def main():
    gj_initialize()
    get_linkedin()


main()
