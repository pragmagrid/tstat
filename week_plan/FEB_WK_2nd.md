## 2019 FEB WEEK SECOND

#### Things to do

- [x] Fix the bug that all data isn't stored in influxDB completely.

	- Don't insert all data lines in one log file into influxDB.

	Program can insert more than one data with multiple points because I use HTTP API. But, it occurs a bug that all data aren't inserted completely when there are too many lines added at HTTP API curl statement. So, I tested how many lines the program can process.
	
	- Add 'line_limit' to count lines to process in config.py.

	It's upon a personal server, computer, etc. In my environment, 90 lines are proper to insert into influxDB at a time.

	- But, there are difference in process time between bug fix before and after.

	Before bug fixxing, the program took about 1m 30s to process all log files. But, after bug fxxing, the program took about 9m to process all log files. So, it's better to process the all log files to divide into several parts.

RESULT: I divided the all log files into 4 parts.

	Time to process from 2017_12_07_13_54.out to 2017_12_22_16_57.out (Total 166,248 data lines) -> 01:52
	Time to process from 2017_12_22_17_57.out to 2018_01_06_22_18.out (Total 144,252 data lines) -> 01:52
	Time to process from 2018_01_06_23_20.out to 2018_01_22_03_42.out (Total 219,547 data lines) -> 02:49
	Time to process from 2018_01_22_04_44.out to 2018_02_06_09_10.out (Total 156,119 data lines) -> 02:05
	Time to process from 2018_02_06_10_14.out to 2018_02_21_13_38.out (Total 182,949 data lines) -> 02:24

- [ ] Make tstat_to_influx.py file to execute file.

- [ ] Beginning and end file can be set by input arguments.

- [ ] Rewrite the README.md file.

- [ ] Pull & Request to master branch.
