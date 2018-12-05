# -*- coding: utf-8 -*-
"""
@author: Manu kumar
"""

############################ IMPORTING PACKAGES ##########################
from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import datetime
from datetime import date
import mysql.connector
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders 

############################# MYSQL CONNECTION #####################

db = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="root",
  database="userShows"
)

#################################### CREATION OF DATABASE ###############################

cursor = db.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS userShows")

sql = """CREATE TABLE IF NOT EXISTS ShowDetails (
             Name VARCHAR(100),
             Email_address VARCHAR(100),
             TV_Series VARCHAR(1000)
             )"""
cursor.execute(sql)

#################################### GETTING INPUTS FROM USER ####################################

Name_input = input("Input your name: ")
Email_address_input = input("Email address: ")
TV_Series_input = input("TV Series: ")

fromaddr = "imdbscriptManukumar@gmail.com"
toaddr = Email_address_input

############################### MAKING CHANGES IN DATABASE ###################################
        
try:
   entry = ("INSERT INTO ShowDetails (Name, Email_address, TV_Series) VALUES (%s, %s, %s)")
   val = (Name_input, Email_address_input, TV_Series_input)
   # Execute the SQL command
   cursor.execute(entry, val)
   # Commit changes in the database
   db.commit()
   print("\nData stored into database")
except:
   # Rollback in case there is any error
   db.rollback()

# disconnect from server
db.close()

###################### OBTAINING CURRENT DATE #################################################  
Status = []    
Ser_inv_name = []
today = date.today()
today = str(today)

########################### WORKING ON INDIVIDUAL SERIES SEARCH #########################################

TV_Series = TV_Series_input.split(", ")
l = (len(TV_Series))

for indivSeries in TV_Series:
    Ser_inv_name.append(indivSeries)
    series_search = "+".join((indivSeries).split())

    base_url = "https://www.imdb.com/search/title?title="
    new_url = base_url+series_search+'&title_type=tv_series'

    #base_url = "http://www.imdb.com/find?q="
    #new_url = base_url+series_search+'&s=all'

####################### FETCHING URL SEARCH RESULTS #####################################

    x = urlopen(new_url)
    source = x.read()
    #source = requests.get(new_url).text
    soup = BeautifulSoup(source, "xml")

########################## FETCHING LINK OF A SPECIFIC SHOW ################################

    res_url = soup.find('div', class_='lister-item mode-advanced')
    res_url = res_url.find('div', class_='lister-item-content').h3.a
    res_url = res_url.get('href')
    
    base_res_url = "https://www.imdb.com"
    showIMDBlink = base_res_url+res_url

####################### SCRAPPING OF DATA ###################################

    y = urlopen(showIMDBlink)
    source1 = y.read()
    soupa = BeautifulSoup(source1, "xml")
    
    first_link = soupa.find(id = "main_bottom", class_='main')
    
    seasonNum = first_link.find('div', class_='seasons-and-year-nav')
    currentSeason = seasonNum.find('a')
    currentSeasonNum = currentSeason.text

############################ FETCHING LINK OF LATEST SEASON ##########################
    season_url = seasonNum.find('a')
    season_url = season_url.get('href')
    season_url = season_url.replace("=tt", "&ref_=tt")
    
    seasonIMDBlink = base_res_url+season_url
#    print(seasonIMDBlink)

######################### SCRAPPING FROM LATEST SEASON #################################

    z = urlopen(seasonIMDBlink)
    source2 = z.read()
    soupb = BeautifulSoup(source2, "xml")

################## Checking if the show has finished streaming all its episodes ###########

    showOver = soupb.find('div', class_='subpage_title_block')
    showOver = showOver.find('div', class_='parent').h3
    showOver = showOver.find('span', class_='nobr').text.strip()
    
    showOver1 = showOver.split("–")[1]
    showOverYear = showOver1.strip(")")

    if showOverYear != " ":
        emailMsg = "Status: The show has finished streaming all its episodes."
        Status.append(emailMsg)
#        print(emailMsg)

####################### SHOW HAS NOT FINISHED STREAMING #######################################

    else:
        ans=[]
        allD=[]
        sizes=[]
        
        episodeDates = soupb.find('div', class_='list detail eplist')

        for epDates in episodeDates.find_all('div', {"class":"airdate"}):
            epDates = epDates.text.strip()
            epDates = epDates.replace(".", "")
            sz = len(epDates)
            sizes.append(len(epDates))
            allD.append(epDates)
            
            if((sz) > 4):
                epDates = datetime.strptime(epDates, '%d %b %Y')
                epDates = str(epDates)
                epDates = datetime.strptime(epDates, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                ans.append(epDates)
        n = len(ans)
        
###################################################################################################################################################
        
        if((len(str(allD[0]))) == 4):
            epDates = datetime.strptime(allD[0], '%Y')
            epDates = str(epDates)
            epDates = datetime.strptime(epDates, '%Y-%m-%d %H:%M:%S').strftime('%Y')
            emailMsg = "Status: The next season begins in {0}.".format(epDates)
            Status.append(emailMsg)
#            print(emailMsg)
            
#####################################################################################################################################            

        else:
            for i in range (0,n):
                if(ans[i] > today and i<n):
                    break
                else:
                    i+=1
        
            if(i==n):
                emailMsg = "Status: The show has finished streaming all its episodes."
                Status.append(emailMsg)
#                print(emailMsg)
        
            else:
                emailMsg = "Status: Next episode airs on {0}.".format(ans[i])
                Status.append(emailMsg)
#                print(emailMsg)
#print(Status) 
#print(Ser_inv_name)
finalbody = []
finalPrintBody = []
body = "TV Series: "
space = " "         
for j in range (0,l):
    bodyprint = body + TV_Series[j]
    finalbody.append(bodyprint)
    j+=1

#print(finalbody)

for k in range (0, l): 
    finalPrintBody.append(finalbody[k])
    finalPrintBody.append(Status[k])
    finalPrintBody.append(space)

#print(*finalPrintBody,sep='\n')

msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Show Details"
body = ''
for row in finalPrintBody:
    body += '%s\n' % row

msg.attach(MIMEText(body, 'plain'))

mail = smtplib.SMTP('smtp.gmail.com', 587)

mail.ehlo()

mail.starttls()

mail.ehlo()

mail.login(fromaddr, "manukumar")

text = msg.as_string()

mail.sendmail(fromaddr, toaddr, text)

mail.close()

print("\nEmail sent to the provided Email address")
