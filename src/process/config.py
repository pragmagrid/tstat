#config.py

CONFIG = {
	'host' 		: 'pc-170.calit2.optiputer.net',	#domain
	'dbname' 	: 'network',				#name of DB
	'hostname' 	: 'pc-170',				#name of host(server)
	'port' 		: 8086,					#port number for influxDB
	'path'		: '/export/data',			#path where log files are
	'id'		: '',					#id for database auth
	'password'	: '',					#pwd for database auth
	'time_constraint'	: 2592000,			#2592000 = 1 month in seconds
	'file_list_path'	: '/export/home/minsung/python'	#path to store the progress
}
