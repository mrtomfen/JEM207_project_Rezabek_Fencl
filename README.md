# JEM207_project_Rezabek_Fencl

This is a repository of a project made by Pavel Řežábek and Tomáš Fencl for course JEM207 Data Processing in Python at Institute of Economic Studies, Faculty of Social Sciences, Charles University.

The idea behind this project is following. User fills in a online form with his name, mail adress, desired dates of checkin and checkout and five airbnb url's. Our application then checks the data and saves them into a first database table. When update is called, code scrapes price and availability data and saves them to other database table. Further, app sends the desired data to the user.

Contains: 
  - main python file (rezabek_fencl.py)
  - database (maindb.db)
  - html templates (index.html and login.html)
  - python notebook for creating a database (create_database.ipynb)
  - python notebook for checking database contents (database_contents.ipynb)

Possible extensions would be making the code work on a cloud, creating a cron which would run the update_availability and sendmails commands or editing the form.


