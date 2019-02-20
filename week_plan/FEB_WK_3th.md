## 2019 FEB WEEK THIRD

#### Things to do

- [x] Rewrite the README.md file.

  I rewrote the tstat/src/process/README.md file.
  
- [x] Pull & Request to master branch.

- [x] Skip the port number 22 in progress file.

- [x] Total number of processed lines is written in progress file.

- [ ] Fix query in Grafana.

	I found it can be more efficient to use 'custom all value' in variable. When user select 'ALL' and suppose I set the 'custom all value' as 80 in port dashboard, then the dashboard display the data points where port number is 80. But, I can't adapt to it. I fix the query that it can extract the value of data just over than zero. And I understood there's no reason to use aggregation function but without aggregation function, I can't grouping the graphs. I have tried to fix it for a two weeks, but the result of searching on google is same.  

- [x] Change 'classes' to 'python codes' in tstat/src/process/README.md

- [x] 'Naming Schema' go in 'python codes' in tstat/src/process/README.md

- [x] Write how to install Grafana in setup.

- [x] Write what user needs to input in config.py in tstat/src/process/README.md

- [x] Clearfy the environment that commands is run in tstat/src/process/READM.md. (Local or Server)

- [x] Write example the run tstat_to_influx.py command in tstat/src/process/REAMD.md

- [x] Write how to create dashboard.

- [x] Process the exception when program run the curl command through 'os.system' function.

	If the return value of os.system is zero, there's no error in running command. But the other value is returned, it means there's a error.
