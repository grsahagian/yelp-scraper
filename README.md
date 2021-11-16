# Disclaimer

* I do not promote, encourage, support or excite any illegal activity or hacking without written permission in general. The repo and author of the repo is no way responsible for any misuse of the information.

* "yelp-scraper" is just a terms that represents the name of the repo and is not a repo that provides any illegal information.

* The Software's and Scripts provided by the repo should only be used for **_EDUCATIONAL PURPOSES ONLY_**. The repo or the author can not be held responsible for the misuse of them by the users.

* I am not responsible for any direct or indirect damage caused due to the usage of the code provided on this site. All the information provided on this repo are for educational purposes only.



## Usage Instructions 

(Google Chrome only; only tested on Mac OS) 

1. Clone repo --> `git clone https://github.com/grsahagian/yelp-scraper`
2. Install dependencies (requirements.txt)
# Extract Browser Cookie
3. Go to https://www.yelp.com/search?find_desc=restaraunt&find_loc=New+york,NY&start=0
4. Inspect Element
5. Navigate to the 'Network' tab
6. Refresh the page
7. Under the name column find the row labelled 'search?find_desc=restaraunt&find_loc=New+york,NY&start=0' 
8. Click this row and look to the right, under the 'Headers' tab, scroll down to the 'Request Headers' 
9. Copy the long string after 'cookie:' and paste this value in quotes to the 'COOKIE' variable in the 'app.py' script 
10. In 'app.py' change location, keyword to preference
11. Run 'app.py'
