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



## 2018 FEB WEEK 03

#### Updated

- Track of log Files

> As main.py runs, directories which are processed completely and inserted in influxDB will be recorded in a progress.txt file. Directories which are recorded in the progress.txt file will not be read again.

- Chronograph Pre-Created Dashboard (Discard)

> Changing in telegraf.conf [input plugins] will allow chronograf to use several pre-created dashboards. With this, trying to use dashboard that is already made.
> Problem : need to install plugin into telegraf (GO)

- Exporting Shell Script's External Configuration File

> To be adopted in different environments, it needs an file to configure settings.

- Importing Pre-Defined Dashboard into Chronograph

> /python/export/import.sh is the shell script.
> Able to configure to select JSON file to import and which server to import.

#### Will be updated

- User Authentication (Continue)

> Create admin user, without accessing authorized ID can not access influxDB
> telegraf, InfluxDB is now secure but still wondering about chronograf
>  https://docs.influxdata.com/chronograf/v1.4/administration/managing-security/#tls--transport-layer-security-and-https
