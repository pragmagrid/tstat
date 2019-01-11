## 2019 JAN WEEK 02

#### Things to do

- [x] Remove old data from influx DB
- [x] Reduce the data storage time

	- tstat_to_influx.py

	Connect to influxDB only at first when executing tstat_to_influx.py
	When the database name overlaps, ask if the user is using the database rather than shutting program down unconditionally.
	Add time module for measuring actual executing time.
	Only the last file name is saved in progress.txt so that whatever the new log file is created later, only single line is read to see how far it has been processed.
	
	- process.py
	
	Change the method which accesses to influxDB, not using python module but using HTTP API.
	Keep the format of being inserted time as epoch.
	Because writing with HTTP API can insert multiple points to influxDB, make a curl-command string per log file.
	Previously, program inserted to DB by line per file so it took many times.
	Also, there's no need to convert string data in log file to integer because it's done by just executing one curl-command via os.system. And ' >/dev/null 2>&1' is appended to not print HTTP API's result on console. Printing it also makes the running time longer.
	Just give 'insert' funcion in influxDB_python.py one curl_command as parameter.
	
	- influxDB_python.py
	
	Check database's existence by implementing 'SHOW FIELD KEYS' in user's database with HTTP API. If the result included "error", the database doesn't exist. Then, create a database with HTTP API.

	- log_tcp_complete.py
	
	As seeing the above description of process.py, there's no need to convert data's type. So, just store data as string type.

RESULT: It takes 1m 34s to process data from 2017_12_07 to 2018_02_21
		  
- [x] Reduce the time to bring data on Chronograf dashboard

	Indicate the exact time in query statements on the dashboards.
	
	Visualize the data in groups by sever's IP address.

RESULT: It takes less than 2s to load data in 5 columns from 2017_12_07 to 2018_02_21 on dashboards.
#### Things to do next week

- Distribute how to process errors more exact. 
- Learn how to use Grafana with Python.
