##2018 FEB WEEK 01

####Updated

- Implemented all the codes from local to the server

>Examples are tested via local machine so it is implemented on the server and it is good to go.

- Created config file

>To prevent any changes directly to the code, created external config file

- 4 Dashboards on Chronograph

>Window Scale, Round Trip Time, Time Duration and Data Payload has been created

- README file updated

>Updates on README.md file

####Will be Updated

- Parsing speed needs to be faster

>Currently it takes a lot of time to parse, considering of using threads.

- Constraint policy confirm

>Retention : how long am I going to keep data for?
>Constraint : until when do we want to collect data?
>These two needs to be confirmed and programmed.

- Optimization for create_db

>using get list db can reduce the amount of calling create_db function

- Export Dashboard

>Exporting Dashboard is necessary when case of using chronograph in different server, and for backup

- Track of log files

>Need to know how far log files have been process, so that I do not have lost log files and also faster process
