VIP Event & Membership Manager
Project Overview
This project implements a VIP Event & Membership Management System using a three-tier architecture. The application allows users to manage members, events, and registrations for a VIP organization. The system supports full CRUD operations and enforces business rules such as membership level restrictions and event capacity limits.
Technology Stack
1.	Database Tier: MySQL hosted on AWS RDS
2.	Logic Tier (API): Python 3.10 with Flask
3.	Testing: Postman for API verification
Schema Database Design
Database contains three main tables:
1. Member
Stores VIP organization members.
Fields:
•	id (Primary Key, Auto Increment)
•	first_name
•	last_name
•	email
•	membership_type
•	join_date
2. Event
Stores event details.
Fields:
•	id (Primary Key, Auto Increment)
•	event_name
•	event_date
•	location
•	description
3. Registration
Links members to events.
Fields:
•	id (Primary Key, Auto Increment)
•	member_id (Foreign Key)
•	event_id (Foreign Key)
•	registration_date
REST API Endpoints
1.	Member APIs
GET	/members	Get all members
GET	/members/	Get member by ID
POST	/members	Create new member
PUT	/members/	Update member
DELETE	/members/	Delete member
2.	Event APIs
GET	/events		Get all events
GET	/events/	Get event by ID
POST	/events		Create new event
PUT	/events/	Update event
DELETE	/events/	Delete event
3.	Registration APIs
GET	/registrations	Get all registrations
GET	/registrations/	Get registration
POST	/registrations	Register member for event
DELETE	/registrations/	Cancel registration
Postman Testing
All APIs were tested using Postman.
Example POST request:
POST /members
Body (JSON):
{
 "first_name": "John",
 "last_name": "Smith",
 "email": "john@email.com",
 "membership_type": "Gold"
}
Expected Response:
{
 "message": "Member created successfully"
}
Validation Rules
•	Member email must be unique
•	Member and Event must exist before registration
•	Foreign key constraints enforced
•	IDs are auto-generated
Installation and Setup
•	Navigate to backend folder
•	cd backend
•	install dependencies
•	pip install flask mysql-connector-python
•	Configure database connection in app.py
•	Run Flask server
•	python app.py
•	The backend API will run at: http://localhost:5000
References
1.	Flask Documentation: https://flask.palletsprojects.com/
2.	MySQL Documentation: https://dev.mysql.com/doc/
3.	Amazon RDS Documentation: https://docs.aws.amazon.com/rds/
4.	MySQL Connector/Python: https://dev.mysql.com/doc/connector-python/en/
5.	Postman Documentation: https://learning.postman.com/docs/
6.	StackOverflow: https://stackoverflow.com/
