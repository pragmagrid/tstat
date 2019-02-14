## 2019 FEB WEEK SECOND

#### Things to do

- [x] Fix the bug that all data isn't stored in influxDB completely.

	- Don't insert all data lines in one log file into influxDB.

	Program can insert more than one data with multiple points because I use HTTP API. But, it occurs a bug that all data aren't inserted completely when there are too many lines added at HTTP API curl statement. So, I tested how many lines the program can process.
	
	- Add 'line_limit' to count lines to process in config.py.

	It's upon a personal server, computer, etc. In my environment, 700 lines are proper to insert into influxDB at a time.

	- But, there are difference in process time between bug fix before and after.

	Before bug fixxing, the program took about 1m 30s to process all log files. But, after bug fxxing, the program took about 9m to process all log files. So, it's better to process the all log files to divide into several parts.

RESULT: I divided the all log files into 4 parts and the line_limit is 700.

	Time to process from 2017_12 to 2018_01 (Total 583,400 data lines) -> 04:30
	Time to process from 2018_01 to 2018_02 (Total 201,685 data lines) -> 01:34

- [x] Beginning and end file can be set by input arguments.

	- When execute tstat_to_influx.py, user can set the range of file to process by inputting arguments.

	The first argument is beginning file and the format of input can be the whole name of file (ex. 2017_12_07_13_54.out) or just year (ex. 2017), year_month (ex. 2017_12) and etc..whatever user wants.

	<pre><code>python tstat_to_influx.py 2017_12 2018_01</pre></code>

	In upon example, the program will process the files from 2017_12 to 2018_01.
	If there are no arguments, then the program will process the all log files.

- [x] Creating progress_'executting time'.txt file whenever program executes.

	Everytime program executes, the error log file (the format of file's name is progress_'executting time'.txt) will be createtd.

- [x] Simplify the curl statements.

	I added variables that are statements to be processed by the os.system function to simplify the process.py file.
	So, I just delieve the values to proper format in influxDB_python structure's variable.
	For example, I create the influxDB_python structure named 'db' in process.py file and I want to use the insert curl statement.
	<pre><code>curl_insert = db.insert_query % (config.CONFIG['host'], config.CONFIG['port'], config.CONFIG['dbname'], config.CONFIG['id'], config.CONFIG['password'])</pre></code>


- [x] Make tstat_to_influx.py file to execute file.

	- Just run one command, I can make a python script executable.

	<pre><code>chmod 755 tstat_to_influx.py</pre></code>

	Then, I can execute the python script as './tstat_to_influx.py beginning_date end_date'.
	I create a 'prev_setting.sh' file. In this file, there are commands that initial python and main file(tstat_to_influx.py)'s authority setting.

	<pre><code>module load opt-python
	chmod 755 tstat_to_influx.py</pre></code>
	
- [ ] Rewrite the README.md file.

- [ ] Pull & Request to master branch.
