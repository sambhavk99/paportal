# Project Allotment Portal | MNNIT Allahabad
## Introduction
Group Project - "Time to relax while you watch someone who cares do all the work". Funny as it sounds but isn't actually funny for the one who cares. To overcome this problem for the most important projects, this portal has been created. It automates the process of group creation by letting students choose their own group and then automates the process of alloting Mentors to them based on the group's preferences.

This project has been created as a solution to the following problem statement of Web Development Society | MNNIT Allahabad:

## Problem Statement - Project Allotment Portal for MNNIT
Design and implement website for automating the process for assignment of mentor and formation of groups during project allotment.

### Basic features :
1. Should have a administrator login who would enter the information about professors and number of groups to be assigned to each of them.
2. Choosing group leaders according to CPI and notifying them.
3. Checking the availability of students.
4. Group leaders should be able to send request to free students.
5. Students should be notified about the requests and may choose from the available choices.
6. Filling of preferences of professors.
7. Designing a effective algorithm for the assigning mentor.

### Advance features :
1. Group members can chat with the each other for choice filling of professors.
2. Notification Center for displaying all the notifications regarding project allotment.
3. Students should be able to search professors using their AOI (area of interest)
## Project Description:
All the required basic as well as advanced features of the problem statement has been incorporated in the project.

### Tools, Technologies and Libraries used:
1. Backend Language - Python 3 (v.3.7.2)
2. Framework - Django (v.2.0.1)
3. Database - SQLite
4. Frontend Languages - HTML, CSS, JavaScript
5. Style Library - Bootstrap
### Directions to use the website:
1. The website will be fully controlled by the site admin (also called the superuser), it is advised to have a single superuser for the site.
2. Various departments of the institute that wants to participate in the project allotment shall give the information for their username, password, Department Name, Number of students in a group(optional, if they don't want a fixed number of students in each group) The admin will create accounts of all the departments and inform the concerned authorities about the same.
### Role of Departments:
1. Departments will be notified for providing information of the Mentors and Students for project allotment, they are required to check for notifications on this website from time to time!

2. As and when notified:

	1. Departments will be able to login and add the information about their Students, special care should be taken to fill the registration number of students as once added, it cannot be changed! Added students will be able to login with their Registration number and the password given.
	2. Departments will be able to login and add the information about their Mentors.
	3. Departments shall take care that the total number of groups to be allotted to all the mentors matches the (total number of students taking part in project allotment in the department)/(students in each group). if they don't want to fix the number of students in each group, they shall inform the site admin beforehand.

3. Departments can also edit the information filled by them till the last date of information filling!

4. Departments can change their password once they are logged in by navigating to the user options tab!

### Role of Students:
1. Students will be notified for each and every process of Project Allotment right from the start to the very end!

2. As and when notified, Students will be able to login and see if they are the group leader or not!

3. If they are the group leader, as and when notified:

	1. they will be able to create a group by name of their own choice
	2. they will be able to see a list of all the available students and can send request to add them into their group. However, a request once sent can be canceled before it is accepted by the recipient.
	3. After creating their group, they will be responsible for filling the preferences of Mentors (Mentor details can be accessed by clicking on the Mentor's name). However, they can consult their group members regarding the same, through the Group chat option provided in the portal.
	4. they are also supposed to freeze their choices before the aforementioned due date, failing to do so, the last filled choices will automatically be frozen.
4. Students, other than the group leaders:

	1. will be able to receive requests from Group leaders and will be notified for the same as they log in. On accepting a Group leader's request, they will become a member of that group and the rest of the requests will be deleted. However, they can reject the requests if they want to. Students are advised to be very careful in accepting a particular request, as, once accepted, it cannot be undone!
	2. will be able to access the list of mentors available for preference filling, they can see the Mentor's details by clicking on their name
	3. will be able to chat with their group members and advise them on the preference filling of Mentors.
	4. As and when notified, Students will be able to see the result of mentor allotment by logging into their account under the profiles column!

5. Students can also change their password once they are logged by navigating to the User Options tab!

### SuperUser: The Admin
1. The admin will have the options to allow or restrict various features at different time intervals. They can do this by creating a userdirection object in the admin panel and linking that object with their username.

2. There will be a list of features, they need to select the options they want to allow and save the object.

3. To bring about the changes and to implement the features, the admin needs to visit a url of the type: ```www.<sitedomain>.com/notifications``` Automatic notifications for the allowed features will be created once that url is visited.

4. To restrict a feature, the admin needs to uncheck the option and save the object. They should also delete the relevant notifications from the notifications models manually.

5. Admin can add additional notification by using the add notifications option from the admin page.

6. Admin can also reset the website anytime he wants to by visiting a url of this type: ```www.<sitedomain>.com/reset```. Everything will be reset except the information uploaded by the departments and the userdirections (directions of the admin).

7. Admin can also just reset the result of mentor allotment by visiting a url of this type: ```www.<sitedomain>.com/reset_result```. The mentor alloted to each group will be removed.

### Instructions to run locally
1. Download the project from GitHub. Rename the downloaded file as 'paportal'.
2. Open the project in a python IDE (Pycharm recommended).
3. Make sure that you have installed Django 2.0.1 or higher (Installing in virtual environment is recommended).
4. Set the project Interpretor as Venv/scripts/python.exe where Venv needs to be replaced by name of the virtual environment( if you have one) else select the scripts/python.exe file from wherever Django is installed.
5. In the command line type the following commands to sync the database:
```python manage.py makemigrations```
```python manage.py migrate```
6. Set up a superuser:
```python manage.py createsuperuser```
7. Finally run the server
```python manage.py runserver```
   and you are good to go!!
