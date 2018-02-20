## 2018 FEB WEEK 01

#### Updated

- Implemented all the codes from local to the server

>Examples are tested via local machine so it is implemented on the server and it is good to go.

- Created config file

>To prevent any changes directly to the code, created external config file

- 4 Dashboards on Chronograph

>Window Scale, Round Trip Time, Time Duration and Data Payload has been created

- README file updated

>Updates on README.md file

#### Will be Updated

- Parsing speed needs to be faster (NVM)

>Currently it takes a lot of time to parse, considering of using threads.

- Constraint policy confirm (NVM)

>Retention : how long am I going to keep data for?
>Constraint : until when do we want to collect data?
>These two needs to be confirmed and programmed.

- Optimization for Create_DB

>using get list db can reduce the amount of calling create_db function

- Export Dashboard

>Exporting Dashboard is necessary when case of using chronograph in different server, and for backup

- Track of log files

>Need to know how far log files have been process, so that I do not have lost log files and also faster process



## 2018 FEB WEEK 02

#### Updated

- Optimization for Create_DB

>Get list DB will return the list of DB in InfluxDB, search_dictionaries function will search through the list of DB and if there is already DB exist it will not call Create_DB function.

- Count for Processed Files, Error files

>At run.py, Analyze function will print number of processed log files and error files after every job is done.

- Error Handle

>Simple Handler has been added to let user know which error has been Occurred.

- Export Dashboard

>Dashboard will be exported through export.sh (shell script). But it only exports the dashboard frame not the datas. Also it will create a JSON file of dashboard on export directory in case of backup.

#### Will be Updated

- Track of log files (working on currently)

>Need to know how far log files have been process, so that I do not have lost log files and also faster process.

- Exporting Shell Script's External Configuration File

>To be adopted in different environments, it needs an file to configure settings.

- Chronograph Default Style Dashboard

>Needs to find out how to set a default dashboard so that anytime other user install this, certain format of dashboard is installed as well

- User Setting

>Adds some kind of security on accessing and editing DB.