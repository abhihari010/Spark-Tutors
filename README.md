# SPARK TUTORS
#### How to run:
This project can be viewed on your local host. First, clone this repo to the directory of your choosing and then navigate to the directory containing the project. Afterwards, set up a virtual environment and download the requirements necessary by pip installing the requirements.txt file. Lastly, in the terminal, type "flask run" to run the website and you will be able to view it on your local host. 
#### Description:
This project is a website I created for a friends tutoring company. He did not have a website and although he didn't ask me to create one for him, I decided that it would be a great opportunity for me to enhance my coding knowledge in Python, CSS, JS, and HTML. For this website I utilized Python, Flask, and firebases authentication and realtime database to store my users info, the messages they send, and the appointments they create.

#### Templates:

###### Index.html File:
My templates folder includes all of my html files. My first html file I created was the index.html file and it served as my layout for the rest of my pages because I used jinja to extend the layout of this page to the rest of my html pages. The index.html file included my navbar as well as the layout for that all of my pages would follow. It also made subtle changes whether there were a user in the session or not.

###### Home.html File:
The next file I implemented was the home.html file. This file extends from the index.html file so that the navbar is still included but also adds more to the page. It implements a tutoring image as well as also including a small subsection at the bottom that allows users to get started registering and also provides a small description about the company.

###### Offer.html File:
This file, using jinja, also extends from the index.html file. In this page, descriptions on what the company offers is included. Spark Tutoring is a SAT, College Application, and College Essay tutoring company, so in this file I implemented three small cards that included information on how exactly they would help in these categories.

###### Contact.html:
This file was slightly more complicated as it was changed whether there was a user in session or not. If there was no user in session and they wanted to send a message, they would have to provide their name, email, and the message they would like to give to us. However, if there was a user in session, the user would only have to provide the message they wish to send us because we already have their name and email in our database. Then, from this, the message would also be submitted to our database and the user would receive a reply as soon as possible.

###### plans.html:
This page is very similar to offer page in that there are multiple cards displaying information. However, this page is more about the different types of plans and the pricing of each plan that the company has. Spark Tutors has four different plans that all come in at different costs and so I displayed this information in the neatest way possible so that any user could understand and know which plan they would like to pursue.

###### register.html:
The register page allows a user to register an account for spark tutors so that they can start scheduling appointments and getting in contact with tutors. All the necessary restraints and checks were put into place to ensure that multiple users can't have the same username or email, and I also made sure that each field was filled out. This information would then be submitted and stored into the User table in the database, and so the information could be remembered for when a user would want to login.

###### login.html:
The login page is very similar to the register page, however, this is for users who already have an account and they must provide their email and password correctly to login.

###### appointment.html:
The appointment page allows a user who has registered to Spark Tutors to schedule a session. I have ensured that if any other user has taken up a time slot, that the current user is unable to choose that time slot. I have also made sure that if a user tries to choose a time slot that is on a weekend, that they are met with an error letting them know that weekends are unavailable. This appointment is then submitted to the database to the Schedule table and is later called on by the schedule.html page.

###### schedule.html:
The schedule page provides the upcoming schedule for any user based on the appointments that they have created. It is listed by using the schedule table in the database.

###### account.html:
The account page provides the different details of the user and allows them to change their details if they would like.

###### index.js
This javascript file adds to the appointment and account page. The javascript in this file makes it so that when users have chosen a specific time slot on a given day, no other user can choose that time slot on that day. Additionally, it allows user to edit their account details. When first viewing the account details page, a users details are disabled from being changed until they hit edit. The edit button then enables the different text fields for the user to change their details.

###### app.py:
This includes all of my python code as well as initiliazing the implementation of firebases authentication system and realtime databse with the Message, User, and Schedule tables. It has the various routes for each html page and ensures that each html page is error free. This page also initilizes flask so that the website can actually be viewed.

###### styles.css:
My styles.css provides the styling for all of my html pages and also is what allows the different plan flashcards to move when hovered in the plans page.

###### Summary:
This was my final CS50 Project and I am very happy I did this course as I learned a lot and also enjoyed every minute of it. Thank you for viewing my project!
