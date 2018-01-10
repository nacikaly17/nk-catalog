# Udacity FSND Project Item Catalog  #
This project is connected to the _Full Stack Web Developer Nanodegree Program_ course by **Udacity**.

This python based **web application** provides a list of items within a variety of **categories** as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.
## Install ##
All project files can be downloaded as zip file from
```
    https://github.com/nacikaly17/nk-catalog.zip
```
or clone with HTTPS
```
    Use Git or checkout with SVN using the web URL.
    git@github.com:nacikaly17/nk-catalog.git
```
After unzip this file you will get a folder and subfolder with following files:
./nk-catalog/
* --init--.py
* app_config.py
* controllers.py
* client_secrets.json
* endpoint_tester.py
* forms.py
* init_catalog.py
* model_catalog.py
* run.wsgi
* README.md
* LICENSE.txt
* MANIFEST.in
* /db 
    * catalog.db
* /static 
    * styles.css
    * blank_user.gif
* /templates
    * catalog.html
    * deleteCategory.html
    * deleteItem.html
    * editCategory.html
    * editItem.html
    * header.html
    * items.html
    * login.html
    * main.html
    * newCategory.html
    * newItem.html
    * signup.html
## Environment ##
This program requires **Python** and Linux based virtual machine . Therefore VM and Python must be on your machine.
* install [Python]("https://www.python.org/">Python</a>) on your computer
* Install Linux based virtual machine on your computer
## Adaption for your local environment ##
1. app_config.py file contains 2 path definitions, which are required in case if it is deployed on apache2 web server or localhost test environment ( uncommend 2 variables for your requirement )
Default delivery is for apache2 web server deployment.
```
# configuration for local host
#client_secrets_path = 'client_secrets.json'
#db_path = 'sqlite:///db/catalog.db'+'?check_same_thread=False'

# configuration for deployment on apache server
client_secrets_path = '/var/www/html/nk-catalog/client_secrets.json'    
db_path = 'sqlite:////var/www/html/nk-catalog/db/catalog.db'+'?check_same_thread=False'
```
2. File run.wsgi is wsgi modul to run this app  on apache2 web server. sys.path.insert must be defined as absolute path. You have to change this in case you have different path.
```
sys.path.insert(0, '/var/www/html/nk-catalog')
```
3. File client_secrets.json contains client_id from Google APIs to use the Google OAuth authentication and authorization. This filed is empty . For your usage , please put your client_secrets.json content into this file.
```
{"web":{"client_id":"......"}}
```
## Initial Test Data ##
To test this application, you can setup database with initial test data. It creates **9 categories** with some items.
* start a _Terminal_ comand line window
* change to the folder, where you have unzipped  **nk-catalog.zip**
* and run **init_catalog.py** from your Terminal with following command.
```
python init_catalog.py
```
Program connects to the **db/catalog.db** database and inserts some test data.
It creates 2 test users, which can be used during login procerude.
It is also possible with google account to login.
```
Created initial users (password = 'Udacity')
    username = naci
    username = reviewer
```
## Run the application ##
* start a _Terminal_ comand line window
* change to the folder, where you have unzipped  **nk-catalog.zip**
* and run **controllers.py** from your Terminal with following command.
```
python controllers.py
```
A local web server starts on url =  ***http://localhost:8000***  
You can put this url to your favorite browser to use this Catalog App.
## Testing of application endpoints : API's ##
To test  API's application must be running on web server ( s. Run the application ).
* start a _Terminal_ comand line window
* change to the folder, where you have unzipped  **nk-catalog.zip**
* and run **endpoint_tester.py** from your Terminal with following command.
```
python endpoint_tester.py
```
It calls following endpoint API's on local webserver ***http://localhost:8000*** with user credentials:
username = 'naci'
password = 'Udacity'

* Test 1: Creating two new Categories
    * **/api/categories?name=Ironman**
    * **/api/categories?name=TourDeFrance**
* Test 2: Read all Categories ( There must be 11 now )
    * **/api/categories**
* Test 3: Read last created Category
    * **/api/category/11**
* Test 4: Update name of  last created Category ( with id = 11)
    * **/api/category/11?name=TourDe-Udacity**
* Test 5: Delete last created Category ( with id = 11)
    * **/api/category/11**
* Test 6: Creating two new Items (Id: 6 and 7 ) to last created Category ( with id = 10)
    * **/api/category/10/items?title=Neopren&description=needed**
    * **/api/category/10/items?title=Cycle&description=For180Km**
* Test 7: Read all items of  last created Category
    * **/api/category/10/items**
* Test 8: Update Item of last created Category
    * **/api/category/10/items/6?title=Patrick+Lange&description=from+Darmstadt**
* Test 9: Delete last created Item to last created Category
    * **/api/category/10/items/7**
## Supported Python versions ##
This program runs with python 2.7 and higher.
## Licence ##
It is free to use only for learning purposes. 
