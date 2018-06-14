# Thunderhead Monkeys
### _**Cloud Learning Environment**_

--------------------------------------------------------------------------------


**Setup**
###### Environments to run django:
* Python 2.7.x
* Django 1.11.x (install via `pip install django`)    


**Instructions**
###### Deploy webpage on local server
1. Open command prompt/terminal
1. Traverse directory to where the `manage.py` file is
2. Run command `python manage.py runserver` to run local server on your own machine
3. Go to a web browser and type: `localhost:8000` to see whether you've deployed correctly  

_*To get rid of unapplied migration, type command `python manage.py migrate`_


###### Creating Django admin (omit this part as your accounts have already been created)
1.	Run local server `python manage.py runserver` if you have not done so
2.	Launch another terminal/command prompt and run command `python manage.py createsuperuser`
3.	Type in username, email and password
4.	To access account, type `localhost:8000/admin` in the web browser and sign in with created username and password  


###### Accounts (Please enter and change your password):
> * bernadine.admin : temp12345
> * rizudin.admin : temp12345
> * joel.admin : temp12345
> * martin.admin : temp12345  


--------------------------------------------------------------------------------


For the time being, since there is no proper task management tool utilized to keep track of what we're doing every sprint, we will just utilize the README file within this Git repo. As such, everyone is able to gain access to it and maintain transparency within all the group members.

###### **Regulations:**
* Insert a _**'(Completed)'**_ tag beside the task that you have completed  
    - Example:  
        1. _**'(Completed)'**_ Assigned task to respective members for upcoming sprint


--------------------------------------------------------------------------------


# **Collaborative Tasks List:**
* Frontend:
    1. Create logical diagram
    2. _**'(Completed)'**_ Create entity relationship diagram (Relational Data Tables)
    3. _**'(Completed)'**_ Create initial use case  diagram
    4. Create initial sequence diagram


--------------------------------------------------------------------------------


# **Individual Tasks List:**
* Faried:
    1. _**'(Completed)'**_ Create django application
    2. _**'(Completed)'**_ Create and upload data tables (MySQL)
    3. Start coding the data access layer for informational retrieval
    4. Programming of the Login/Logout Logic
        * Forget Password (Good-To-Have)
    5. Password Manager Functionality
        * Prompts user at the start to change password

* Joel:
    1. Start programming the business logic layer (Bootstrap)
    2. Programming of student management functionality
    3. Programming of instructor management functionality

* Martin:
    1. Find templates online to best display bird’s eye view of teams
    2. Find a common theme colour for our overall system
    3. Add interactive buttons using javascript
