#config.py

CONFIG = {
	'host' 		: 'pc-170.calit2.optiputer.net',	#domain
	'dbname' 	: 'tstat',				#name of DB
	'hostname' 	: 'pc-170',				#name of host(server)
	'port' 		: 8086,					#port number for influxDB
	'path'		: '/export/data',			#path where log files are
	'id'		: 'admin',					#id for database auth
	'password'	: 'admin',					#pwd for database auth
	'time_constraint'	: 2592000,			#2592000 = 1 month in seconds
	'file_list_path'	: '/export/home/chojpsh1/python',	#path to store the progress
        'start_file'    : '20xx_xx_xx_xx_xx.out',               #the file which processed as start
        'end_file'      : '20xx_xx_xx_xx_xx.out'                #the file which processed as end 
}
