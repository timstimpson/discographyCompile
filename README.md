# Discography Compile

The project goal was to create a platform in order to provide automation for a royalties collection agency to create an author or performer dataset of all recordings produced to date.

The full dataset of public recordings is collected from the the [link to discogs.com](http://discogs.com) repository of public maintained data. Business rules were then created in Python utilizing a Django web interface to view and control the data output. An excel spreadsheet is created and sent to the requesting user.

### Prerequistites

* Obtain a copy of the discogs database from [discogs.com](http://discogs.com) which is delivered in XML formatted data. This must be then converted to an SQL format database on your local machine.

* The code is written in Python 3.4 and all required modules are contained in the ** discogs-req.txt file in this repository

* Add the modules in DiscogsApp and DiscogsPro to your Django directory

### Built With

* Python 3.4
* Django 1.9.6
* discogs-client 2.2.1
* SQLite database

### Future development

The discography data requires 3-5 minutes to collect from the database. This is sufficient for the business case but further development in RDDs will enable this time to be reduced.


