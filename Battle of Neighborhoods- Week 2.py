#!/usr/bin/env python
# coding: utf-8

# # Introduction
# New York City is a melting pot for cultures and cuisines. You should be able to find any s of cuisines you can imagine in NYC.
# One of the most delicious and diverse cuisines is Persian (Iranian) food. Persian cuisine’s diversity comes from the variety of cultures in Iran. There are endless varieties of dishes and breads; made with ingredients that are native to Iran, such as saffron, pistachios and walnuts.
# When you Google ‘Persian Restaurants in New York’ a good number of them show up. When you check the Category of the restaurant, they are mostly listed as “Mediterranean Cuisine”! Persian and Mediterranean have a lot of common ground but there are many authentic Iranian dishes that are usually not available in most Mediterranean restaurants. However, I believe since the Mediterranean cuisines are more known in America, Persian restaurant businesses label themselves as such so they appear more in searches! Thus, in order to have a wider search in this project I’m going to request and analyze data related to the Mediterranean restaurants.
# 

# ## Business Problem
# This project can be helpful for all the investors looking for great business opportunities in the restaurant industry. Opening a Persian restaurant in general is a great business idea since it has something to offer for every taste! However, in this project I am about to dig deep into New York City’s neighborhoods to find the best location to open a new Persian restaurant. I am also going to find out where we can find the best Mediterranean food in NYC today! Understanding how current businesses are doing in different neighborhoods can lead us to a better decision on where to open a new one.

# ## Data Required and Sources
# In order to tackle the problem statement, we would need a very thorough data on New York City. In addition to NYC Boroughs and Neighborhoods, we would need the latitude and longitude of each area to be able to use visualization maps and achieve a better analysis. We would also need detail of each venue and Mediterranean restaurant, such as the rankings, number of likes and tips given by customers.
# 
# Many online sources provide data on different locations around the world. In this project, I am going to use data from http://cocl.us/new_york_dataset to get the data on New York City’s boroughs and neighborhoods. The geographical coordination (latitude and longitude) of each neighborhood can then be accesses through Python package called Geocoder. In addition, Folium can be used to create the visualization maps.
# Foursquare has a large database including different venues information. Here, we are interested in restaurants’ data. Getting access to the Foursquare API we can access information on restaurants in New York City’s different neighborhoods. We can also get access to restaurants rankings, and other details such as number of likes and tips given on Foursquare! 
# Putting all the information together we can have a good idea of the number of Mediterranean restaurants in each neighborhood and find the best ranking Mediterranean restaurants in town.  Having all the information discussed in previous sections help the investors decide where is the best location to open a new Mediterranean restaurant. Moreover, by looking at the statistical data on current businesses they can project how successful their business will be in the future!

# In[4]:


#importing libraries and packages that are going to be used.
import numpy as np 
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

import requests 

from bs4 import BeautifulSoup
import os

#installing map rendering library
get_ipython().system('conda install -c conda-forge folium=0.5.0 --yes ')
import folium 

get_ipython().system('conda install -c conda-forge geopy --yes')
from geopy.geocoders import Nominatim #converts an address into latitude and longitude values

# Matplotlib and associated plotting modules
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
get_ipython().run_line_magic('matplotlib', 'inline')

print('Importing is all DONE!')


# To be able to use Foursquare I need to provide my variables:

# In[5]:


#I need to define Foursquare Credentials ( Client ID and the Client Secret ID)
#and the Foursquare API version
CLIENT_ID = 'YX50D425ZLUUX5PTQMTKGCTQYWBYN3FYHWUPZ5HNDJBQBFMO' 
CLIENT_SECRET = 'G5LUPYDPQ12X1DSCYEMTCUNA0UFWXJX1VBLG2CRPMRVHITO2' 
VERSION = '20180605'


# In[6]:


#defining functions to get latitude and longitue of locations
def geo_location(address):
    geolocator = Nominatim(user_agent="foursquare_persian_agent")
    location = geolocator.geocode(address)
    latitude = location.latitude
    longitude = location.longitude
    return latitude,longitude

#setting variables, and providing url to fetch data from foursquare api
def get_venues(lat,lng):
    radius=400
    LIMIT=100
    url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
#requesting data
    results = requests.get(url).json()
    venue_data=results['response']['groups'][0]['items']
    venue_details=[]
    for row in venue_data:
        try:
            venue_id=row['venue']['id']
            venue_name=row['venue']['name']
            venue_category=row['venue']['categories'][0]['name']
            venue_details.append([venue_id,venue_name,venue_category])
        except KeyError:
            pass
    column_names=['ID','Name','Category']
    df = pd.DataFrame(venue_details,columns=column_names)
    return df

#now doing the same thing but to get venue details such as ratings, tips etc.
def get_venue_details(venue_id):
    url = 'https://api.foursquare.com/v2/venues/{}?&client_id={}&client_secret={}&v={}'.format(
            venue_id,
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION)
    results = requests.get(url).json()
    print(results)
    venue_data=results['response']['venue']
    venue_details=[]
    try:
        venue_id=venue_data['id']
        venue_name=venue_data['name']
        venue_likes=venue_data['likes']['count']
        venue_rating=venue_data['rating']
        venue_tips=venue_data['tips']['count']
        venue_details.append([venue_id,venue_name,venue_likes,venue_rating,venue_tips])
    except KeyError:
        pass
    column_names=['ID','Name','Likes','Rating','Tips']
    df = pd.DataFrame(venue_details,columns=column_names)
    return df

def get_new_york_data():
    url='https://cocl.us/new_york_dataset'
    resp=requests.get(url).json()
    features=resp['features']
    column_names = ['Borough', 'Neighborhood', 'Latitude', 'Longitude'] 
    new_york_data = pd.DataFrame(columns=column_names)
    for data in features:
        borough = data['properties']['borough'] 
        neighborhood_name = data['properties']['name']
        neighborhood_latlon = data['geometry']['coordinates']
        neighborhood_lat = neighborhood_latlon[1]
        neighborhood_lon = neighborhood_latlon[0]
        new_york_data = new_york_data.append({'Borough': borough,
                                          'Neighborhood': neighborhood_name,
                                          'Latitude': neighborhood_lat,
                                          'Longitude': neighborhood_lon}, ignore_index=True)
    return new_york_data

print("All functions are defined!")


# Now that we have imported our libraries and defined our functions and set our requests from Foursquare, it is time to get some data about New York City:

# In[7]:


nyc_data=get_new_york_data()
nyc_data.head(10)


# Seems that each Borough in NYC is consisted of many Neighborhoods. In order to find out how many different Neighborhoods we have in our data we can use the .shape method:

# In[8]:


nyc_data.shape


# Our data includes 306 different Neighborhoods in NYC.

# Just to get an idea, I'm going to use a bar plot visualization to see how many Neighborhoods are there in each Borough:

# In[9]:


clr = "blue"
nyc_data.groupby('Borough')['Neighborhood'].count().plot.bar(figsize=(8,6), color=clr)
plt.title('Neighborhoods per Borough-NYC', fontsize = 18)
plt.xlabel('Borough', fontsize = 14)
plt.ylabel('Number of Neighborhoods',fontsize = 14)
plt.xticks(rotation = 'horizontal')
plt.legend()
plt.show()


# Some of NYC's Boroughs such as Queens has around 80 different Neighborhoods!

# ## Mediterranean Restaurants in Each Neighborhood
# Now it's time to look into each Borough and Neighborhood to see how many Persian restaurants are out there!Just a quick google search and it's obvious that most of Persian Restaurants have identified themselves as Mediterranean cuisine. Since not many people know about Persian Cuisine, it might be wise for businesses to include themselves in a bigger and much known category. If they tag their restaurant as let's say "Mediterranean" then they will show up in more searches! 
# Thus, I'm going to set the Category as 'Mediterranean Restuarant' to catch all possible Persian restuarants in NYC:

# In[10]:


#queens has most neighborhoods
#prepare neighborhood list that contains persian restaurants
column_names=['Borough', 'Neighborhood', 'ID','Name']
persian_rest_nyc=pd.DataFrame(columns=column_names)
count=1
for row in nyc_data.values.tolist():
    Borough, Neighborhood, Latitude, Longitude=row
    venues = get_venues(Latitude,Longitude)
    persian_restaurants=venues[venues['Category']=='Mediterranean Restaurant']   
    print('(',count,'/',len(nyc_data),')','Persian Restaurants in '+Neighborhood+', '+Borough+':'+str(len(persian_restaurants)))
    print(row)
    for resturant_detail in persian_restaurants.values.tolist():
        id, name , category=resturant_detail
        persian_rest_nyc = persian_rest_nyc.append({'Borough': Borough,
                                                'Neighborhood': Neighborhood, 
                                                'ID': id,
                                                'Name' : name
                                               }, ignore_index=True)
    count+=1


# Since we have limited amount of calls in Foursquare, I'm going to save this data as .csv for our reference:

# In[11]:


#saving the information to a .csv file 
persian_rest_nyc.to_csv('persian_rest_nyc_tocsv1.csv')


# In[12]:


#let's have a glance of our data
persian_nyc = pd.read_csv('persian_rest_nyc_tocsv1.csv')
persian_rest_nyc.head()


# In[13]:


persian_rest_nyc.shape


# There are 39 Mediterranean restuarants in NYC. 
# 
# Now let's see how many are in each New York City's Borough:

# In[14]:


persian_rest_nyc.groupby('Borough')['ID'].count().plot.bar(figsize=(12,6), color=clr)
plt.title('Mediterranean Restaurants per Borough: NYC', fontsize = 18)
plt.xlabel('Borough', fontsize = 14)
plt.ylabel('Number of Mediterranean Restaurants', fontsize=14)
plt.xticks(rotation = 'horizontal')
plt.legend()
plt.show()


# So as you can see Manhattan has the most number of Mediterranean restuarants! Although Manhattan is relatively a small Borough it has around 25 mediterranean restuarants!

# In[15]:


persian_rest_nyc.groupby('Borough')['Neighborhood'].count()


# In[16]:


NumofNeigh = 10 #showing 10 neighborhoods on the graphs
persian_rest_nyc.groupby('Neighborhood')['ID'].count().nlargest(NumofNeigh).plot.bar(figsize=(14,5), color=clr)
plt.title('Mediterranean Restaurants per Neighborhood- NYC', fontsize = 18)
plt.xlabel('Neighborhood', fontsize = 14)
plt.ylabel('Number of Mediterranean Restaurants', fontsize=14)
plt.xticks(rotation = 'horizontal')
plt.legend()
plt.show()


# Flatiron and Soho neighborhoods have the highest number of Mediterranean restuarants.
# Let's just pick the top 5 neighborhoods and check out the restuarants:

# In[17]:


persian_rest_nyc[persian_rest_nyc['Neighborhood']=='Flatiron']


# In[18]:


persian_rest_nyc[persian_rest_nyc['Neighborhood']=='Soho']


# In[23]:


persian_rest_nyc[persian_rest_nyc['Neighborhood']=='Clinton']


# In[19]:


persian_rest_nyc[persian_rest_nyc['Neighborhood']=='Financial District']


# In[20]:


persian_rest_nyc[persian_rest_nyc['Neighborhood']=='Little Italy']


# I can see that there's almost one 'CAVA' in the neighborhoods! out of curiosity I'm going to see out of 39 overall Mediterranean restaurants how many 'CAVA' restaurants are there?!

# In[21]:


persian_rest_nyc[persian_rest_nyc['Name']=='CAVA']


# So there are 5 'CAVA' restuarants and all are in Manhattan!
# 
# Let's look at how many unique Mediterranean restaurants we have:

# In[22]:


persian_rest_nyc.Name.unique()


# There are 32 unique restaurants so some of them are chain restuarants such as 'CAVA'!

# Now let's get into more detail and see which one of these restaurants have the highest ranking:

# In[23]:


column_names=['Borough', 'Neighborhood', 'ID','Name','Likes','Rating','Tips']
persian_rest_stats_nyc=pd.DataFrame(columns=column_names)
count=1
for row in persian_rest_nyc.values.tolist():
    Borough,Neighborhood,ID,Name=row
    try:
        venue_details=get_venue_details(ID)
        print(venue_details)
        id,name,likes,rating,tips=venue_details.values.tolist()[0]
    except IndexError:
        print('No data available for id=',ID)
        #I will assign 0 value for these resturants as they may have been 
        #opened recently or information doesn't exist in FourSquare Database
        id,name,likes,rating,tips=[0]*5
    print('(',count,'/',len(persian_rest_nyc),')','processed')
    persian_rest_stats_nyc = persian_rest_stats_nyc.append({'Borough': Borough,
                                                'Neighborhood': Neighborhood, 
                                                'ID': id,
                                                'Name' : name,
                                                'Likes' : likes,
                                                'Rating' : rating,
                                                'Tips' : tips
                                               }, ignore_index=True)
    count+=1
persian_rest_stats_nyc.tail()


# In[24]:


#saving the data to a .csv file
persian_rest_stats_nyc.to_csv('persian_rest_stats_nyc_csv.csv') 


# In[25]:


persian_rest_stats_nyc.shape


# Let's check some information such as data types in our dataframe:

# In[26]:


persian_rest_stats_nyc.info()


# We need to convert the likes, rating and tips data values from string values (objects) to floats, to be able to perform further statical analysis in Python:

# In[32]:


persian_rest_stats_nyc['Likes'] = persian_rest_stats_nyc['Likes'].astype('float64')
persian_rest_stats_nyc['Tips'] = persian_rest_stats_nyc['Tips'].astype('float64')
persian_rest_stats_nyc['Rating']=persian_rest_stats_nyc['Rating'].astype('float64')
persian_rest_stats_nyc.info()


# To get more statistical insight, I'm going to use the .describe method to get some overall detail on the Mediterranean restaurants in NYC:

# In[29]:


persian_rest_stats_nyc.describe()


# In[30]:


#restaurant with the most number of Likes
persian_rest_stats_nyc.iloc[persian_rest_stats_nyc['Likes'].idxmax()]


# So based on results, Jack's Wife Freda located in Soho (Manhattan) has the highest number of likes. This restuarant has 1,720 likes! The ranting of this restaurant is 8.7 out of 10.
# 
# Now let's find the Mediterranean restuarant with the highest ranking:

# In[33]:


#Restaurant with most Ratings
persian_rest_stats_nyc.iloc[persian_rest_stats_nyc['Rating'].idxmax()]


# Looks like one of the CAVA restaurants (located in Little Italy in Manhattan) has the highest ranking of 9.3 out of 10.

# Now let's see the average Mediterranean restaurant ratings in different neighborhoods, and which neighborhood has the highest and lowest average ratings:

# In[43]:


nyc_neighborhood_stats=persian_rest_stats_nyc.groupby('Neighborhood',as_index=False).mean()[['Neighborhood','Rating']]
nyc_neighborhood_stats.columns=['Neighborhood','Avg. Rating']
nyc_neighborhood_stats.sort_values(['Avg. Rating'],ascending=False).head(30)


# The results are in and it seems that West Village has the highest average rating among the Mediterranean restaurant (average rating of 9.30). On the other hand, Rockaway Park has the lowest averge ranking of 6.2.
# Soho that is one of the neighborhoods with highest number of Mediterranean restaurants has an average rating of 8.90.

# In[40]:


nyc_borough_stats=persian_rest_stats_nyc.groupby('Borough',as_index=False).mean()[['Borough','Rating']]
nyc_borough_stats.columns=['Borough','Avg. Rating']
nyc_borough_stats.sort_values(['Avg. Rating'],ascending=False).head()


# Looks like Manhattan has the highest average rating among the Mediterranean restuarants!(are we surprised?)
# 
# Now let's filter our Neighborhoods with average ratings of 8.5 and higher:

# In[38]:


nyc_neighborhood_stats=nyc_neighborhood_stats[nyc_neighborhood_stats['Avg. Rating']>=8.5]
nyc_neighborhood_stats


# It's time to merge this data with our nyc_data to get the latitude and lonitude of restaurants for visualization purposes:

# In[44]:


nyc_neighborhood_stats=pd.merge(nyc_neighborhood_stats,nyc_data, on='Neighborhood')
nyc_neighborhood_stats=nyc_neighborhood_stats[['Borough','Neighborhood','Latitude','Longitude','Avg. Rating']]
nyc_neighborhood_stats


# In[46]:


#creating map using Folium and displaying it
nyc_map = folium.Map(location=geo_location('New York'), zoom_start=12)
#creating a feature group for the ratings in the dataframe
rating = folium.map.FeatureGroup()

# loop through the ratings and add each to the neighborhood feature group
for lat, lng, in nyc_neighborhood_stats[['Latitude','Longitude']].values:
    rating.add_child(
        folium.CircleMarker(
            [lat, lng],
            radius=10, 
            color='red',
            fill=True,
            fill_color='blue',
            fill_opacity=0.6
        )
    )
    
nyc_map


# In[50]:


nyc_neighborhood_stats['Label']=nyc_neighborhood_stats['Neighborhood']+', '+nyc_neighborhood_stats['Borough']+'('+nyc_neighborhood_stats['Avg. Rating'].map(str)+')'
# add pop-up text to each marker on the map
for lat, lng, label in nyc_neighborhood_stats[['Latitude','Longitude','Label']].values:
    folium.Marker([lat, lng], popup=label).add_to(nyc_map)        
# add ratings to map
nyc_map.add_child(rating)


# So now if we click on any of the tags you can see the name of the neighborbood, its borough and also the Mediterranean restaurants's average ratings!

# ## Results
# 
# Based on our data analysis, there re total of 39 Mediterranean restaurants listed in Foursquare API in the city of New York!
# With 27 Mediterranean restaurants, Manhattan has the highest number among other boroughs!
# Soho and Flatiron neighborhoods have highest number of Mediterranean restaurants (5 each!).
# After filtering results, I found out there are 32 unique restuarants, and the remaining 7 are all chain restaurants.
# 
# Then I dug into the restaurants details;
# By changing some of the data type values from 'object' to 'float64', I was able to perform some statistical analysis.
# The restaurant with the highest rating is CAVA- located in Little Italy, Manhattan. This location has a rating of 9.30.
# The Jack's Wife Freda located in Soho, Manhattan, has the highest number of 'Likes'! (total of 1,720)
# 
# After sorting the neighborhoods based on their Mediterranean restaurants' average ratings, West Village has the highest average rating (9.30). Rockaway has the lowest average rating of 6.20 amongst other neighborhoods. There are some neighborhoods with no Mediterranean restaurant ratings such as Belmont!
# 
# The Mediterranean restuarants in Manhattan have the highest average rating!

# ## Conclusion

# In conclusion, I would suggest the investors to open their new Persian restaurant in Manhattan and in Soho neighborhood! Although Soho has 5 other Mediterranean restaurant it seems that they all have a high rate of success! It seems that due to high demand, Manhattan has many restaurants and majority are successful! Based on the name of the restaurants, unfortunately I did not detect any Persian restaurants! Which might be a great news to the invetors since it shows there's a huge opportunity in opening a brand new Persian restaurant in the heart of Soho!
# I would also make sure I try out the Jack's Wife Freda next time in town!
# Finally, I would suggest a more thorough analysis using multiple location data sources! All the analysis in this report depend on the Foursquare data accuracy and limitations! 
