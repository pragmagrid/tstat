#!/bin/bash

debug() { # Call this function with string parameter which will parse to std:output and log file
	message=$1
	echo $message | tee -a $LOG_FILE
}

setUpConstants() {
	echo "Setting up constants..."

	# Preparing log destination refers to script file name
	THIS_FILE=$(basename "$0")
	THIS_FILE_EXTENSION="${THIS_FILE#*.}"
	THIS_FILE_NAME=$(basename $THIS_FILE .$THIS_FILE_EXTENSION)

	LOG_DIR="/var/log/$THIS_FILE_NAME"
	mkdir -p $LOG_DIR
	LOG_FILE="$LOG_DIR/$(date +%Y-%m-%d_%H-%M-%S).log"
	touch LOG_FILE
	echo "Log will be written at $LOG_FILE"

	SLEEP_TIME=0.5s
}


exitIfHaveError() { # Call this function after execute commands to check exit code (error or not)
	error_code=${PIPESTATUS[0]}

	if [ $error_code -ne 0 ] ; then
		debug "Error code from last command is $error_code"
		echo "Error! exit!"
		exit $error_code
	fi
}

installDependencies() {
	debug "Installing dependencies..."

	debug "Installing expect package..."
	yum install -y expect 2>>$LOG_FILE 		# for mkpasswd 
	exitIfHaveError
}

installAndStartInfluxDB() {
	debug "Installing and starting influxdb..."
	
	debug "Setting up InfluxDB repository..."
cat << EOF | tee /etc/yum.repos.d/influxdb.repo
[influxdb]
name = InfluxDB Repository - RHEL \$releasever
baseurl = https://repos.influxdata.com/rhel/\$releasever/\$basearch/stable
enabled = 1
gpgcheck = 1
gpgkey = https://repos.influxdata.com/influxdb.key
EOF

	debug "Installing InfluxDB..."
	yum install -y influxdb 2>>$LOG_FILE
	exitIfHaveError

	debug "Starting InfluxDB background process..."
	systemctl start influxdb 2>>$LOG_FILE
	sleep $SLEEP_TIME	 # Waiting for influxdb service start properly

	exitIfHaveError
}

createDefaultInfluxAdmin() {
	debug "Creating default InfluxDB admin with user password..."

	CREATE_ADMIN_QUERY="influx -execute \"CREATE USER $1 WITH PASSWORD '$2' WITH ALL PRIVILEGES\""
	debug "Query: $CREATE_ADMIN_QUERY"

	while true ;
	do
		CREATE_ADMIN_RESULT=$(eval "$CREATE_ADMIN_QUERY" 2>&1)
		if [ "$CREATE_ADMIN_RESULT" == "" ]; then # Query execute successfully with no errors
			break
		fi
		debug "Query result: $CREATE_ADMIN_RESULT"
		sleep $SLEEP_TIME	 # Waiting for influxdb service start properly
	done

	# enable authentication
	sed -i "s/# auth-enabled = false/auth-enabled = true/" /etc/influxdb/influxdb.conf

	# restart service
	debug "Restarting InfluxDB background service to apply default admin authentication..."
	systemctl restart influxdb 2>>$LOG_FILE
	exitIfHaveError
}

parse() {
  echo $1 | awk -F'=' '{print $2}'
}

readingConfigFile() {
	file=$1
	if [ -z "$1" ] ; then
		debug "Don't have configuration file"
		return
	fi

	debug "Reading configuration from file $file"

	if [ ! -f $file ] ; then
		debug "File $file not found"
		return
	fi

	while IFS= read -r line; do
		case $line in
			DB_CONF_DIR\=* )    DB_CONF_DIR=`parse $line` ;;
			DB_STORAGE_DIR\=* ) DB_STORAGE_DIR=`parse $line` ;;
			DB_PORT\=* )     	DB_PORT=`parse $line` ;;
			DB_USER\=* )    	DB_USER=`parse $line` ;;
			DB_PASSWORD\=* )    DB_PASSWORD=`parse $line` ;;
			* )           ;;
		esac
	done < $file
}

getPassword () {
    word=`mkpasswd -l $1 -s 0 2>>$LOG_FILE`
    echo $word
}

setDefaults() {
	debug "Set defaults variable and configure InfluxDB"

	[[ -z "$DB_CONF_DIR" ]] 	&& DB_CONF_DIR=/etc/influxdb
	[[ -z "$DB_STORAGE_DIR" ]] 	&& DB_STORAGE_DIR=/var/lib/influxdb	
	[[ -z "$DB_PORT" ]] 		&& DB_PORT=8086			
	[[ -z "$DB_USER" ]] 		&& DB_USER=pragma_admin		

	if [ -z "$DB_PASSWORD" ] ; then
		debug "Generating random password..."
		DB_PASSWORD=$(getPassword 10)
	fi

	# Change bind port
	sed -i "s/# bind-address = \":8086\"/bind-address = \":$DB_PORT\"/" /etc/influxdb/influxdb.conf
	exitIfHaveError

	createDefaultInfluxAdmin $DB_USER $DB_PASSWORD

	createPassFile
}

createPassFile () {
    # create a file with pasword for DB access, save previous if exist
	PASS_FILE=$DB_CONF_DIR/$DB_USER.pass

	debug "Writing password file at $PASS_FILE"
    echo $DB_PASSWORD > $PASS_FILE 2>>$LOG_FILE
    chmod 600 $PASS_FILE 
}

## MAIN ##
setUpConstants
installDependencies
installAndStartInfluxDB
readingConfigFile $1
setDefaults
debug "InfluxDB succesfully install at $(date '+%Y-%m-%d %H:%M:%S')"