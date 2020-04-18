# COMP1510_hackathon

# Team members

## Shagun  
Student ID: A01211571  
Github ID: [Ishika18](https://github.com/Ishika18)  

## Ronald Liang  
Student ID: A01199458  
Github ID: [ronliang6](https://github.com/ronliang6)  

## Ryan Leung  
Student ID: A01204521  
Github ID: [rleung1004](https://github.com/rleung1004)  

## Terry Lun  
Student ID: A00855225  
Github ID: [TerryLun](https://github.com/TerryLun)  

## Concept
The Wuhan Virus is now an ongoing pandemic of coronavirus disease. As it spreads rapidly around the world, our daily lives are greatly affected. One of the many concerns is it is now less convenient to go to groceries and supermarkets due the line ups and wait times. We are going to build a program to help user pick a perfect store with low wait times within range.

## Description
This program will first get the user’s location. It then finds the closest grocery stores using the geolocation of the user. Next step is to find out travel times and popular times of each store using API and modules. Then the program determines which stores are not too populated while within user’s range. Finally, it will output the top five recommended places for the user to go.

## Installation Instructions
In terminal:

`$ pip install requests`  
`$ pip install folium`  
`$ pip install pandas`  
`$ pip install --upgrade git+https://github.com/m-wrzr/populartimes`  

Please also install the latest version of Google Chrome.  
Link is provided below.  
https://support.google.com/chrome/answer/95346?co=GENIE.Platform%3DDesktop&hl=en&oco=0

Make sure Google Chrome is under the Applications folder.

## Special Notes
Keep in mind that this API uses the Google Places Web Service, where each API call over a monthly budget is priced. 
The API call is SKU'd as "Find Current Place" with additional Data SKUs (Basic Data, Contact Data, Atmosphere Data). 
As of February 2018, you can make 5000 calls with the alloted monthly budget. For more information check 
https://developers.google.com/places/web-service/usage-and-billing and 
https://cloud.google.com/maps-platform/pricing/sheet/#places.

## Credits
https://github.com/m-wrzr/populartimes  
Used under the MIT license.

Web Icons Designed by Kraphix / Freepik

## Paired Programming 
#### Ryan - Ronald
commit implemented: get_current_location() and get_coordinate_data() - dd95545a4cead9e74a2489deb137500d4b86d7e7

76 additions

#### All team members
Most of this project was done together as paired programming


