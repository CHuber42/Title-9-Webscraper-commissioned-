# README

#### Developed and Implemented by: Christopher Huber
#### Development Timeline: 2-28-2020 : 3-12-2020

<p>Hello, and welcome to this Webscraper.
This project was commissioned to facilitate research into Title 9 compliance;
as it has no options or command-line args it can accept, there isn't much need
for a README. </p>

### DISCLAIMER: As this project was done as a pet project early in my git-familiarity
### and without any other developers, I opted not to use git to track my updates/branches
##### Therefore, given the lack of visible changes, I will instead use this space
##### to document my development timeline, progression, and skills learned.

<p>The original task before me was to scrape certain data from job listings on
particular job boards, for use in later analysis. I began by modularizing each
job board into its own file, as each will be handled independently. </p>



<ol>
<li>GovernmentJobs.com</li>
<li>LinkedIn</li>
<li>Indeed.com</li>
</ol>

##### Stage 1
<p>I started by teaching myself how to instantiate web handlers (in this case, Chrome)
in order to process a page. Secondly, how to use methods (using Selenium) to access
elements in a page, or attributes of elements, and so forth. The "first stage" finished
with looping over each entry on the front page of the job board to extract the href to
the master-post.</p>

##### Stage 2
<p>Stage two involved developing the ability to - by reading html elements - figure
out how many total pages were present for the job board, access each, and repeat the
above loop for each page, to give a full scrape of every entry on the job board,
resulting in a list of hrefs to the main job posts (for later scraping).
Footnote: GJ uses pagination.</p>

##### Stage 3
<p>Next, I moved on to developing the LinkedIn Module. This module was delayed by
two major factors:
<ul>
<li>The HTML Selenium was encountering was not what I was encountering, as
I was viewing LinkedIn *while logged in*. This actually changes how the results are presented.
In particular:</li>
<li>At the time this stage took place, there were >25 results on LinkedIn.
While logged in, more results beyond the first 25 are accessed through pagination (sort of)
If not logged in, a "see more jobs" button is presented in leiu of the page selector,
which, when clicked, expands the maximum list size.</li>

The net effect of these is that,

<ol>
<li>I had to learn a method for accessing Selenium's HTML (not mine)(accomplished
  with the .page_source method in Selenium), to dump to a doc and analyze. This led to:</li>
<li>Locating the "see more listings" button, and clicking it, which in turn led to:</li>
<li>**many** hours of not understanding why I was not capturing >25 elements. Final result:</li>
<li>Installing a time.sleep() period to ensure the HTML is re-captured post-JS update.</li>

<p>Stage 3 then ended with iterating each job entry, extracting its href, and adding those
to a results list for later utilization.</p>

<p>ADD'l: It was discovered during this time that the Indeed.com results are next-to-impossible
to filter without further assistance from the client, who is currently out of contact. Therefore
this module is suspended for the time being.</p>

##### Stage 4
<p>Stage 4 is fairly straightforward: establish a file structure and format
to dump the results to. In this case, it's figuring out how to import the current time
as a string and use it as a filename, while replacing all non-acceptable characters (:). </p>

##### Stage 5
<p>Stage 5 is where the question "what data are we capturing" becomes relevant.
For now, the list given (Basic stats such as employer, date listed, title, etc) are
not all capturable from the listings' main pages. IE, the hrefs for all jobs are
insufficient and often require information only published on the "preview" for the job.</p>

<p>This requires something of a major re-write. The GovernmentJobs entries' data
is now *primarily* extracted from the preview listing, and only minor elements from the listings' page.</p>

<p>Similarly, the exact publish date of a listing on LinkedIn is (basically) only found on
the preview page. Therefore a dict utilizing the job's title as the key was implemented,
which passes the values to the results writer for lookup/assignment/writing.

#####Stage 6
(NEXT STEPS)


Contact with the client is required for further development.
Possible things to add:
<ul>
<li>Extra data extraction, such as 'job description' tracking(see number 3 below)</li>
<li>A means of comparing the day's logged data to previous days', to discern what jobs
have been un-listed, and when.</li>
<li>Some form of data analysis to perform, as, for now, all we're doing is collecting stats.</li>
<li>Update in-line comments to be consistent with Stage 5's re-write.</li>
