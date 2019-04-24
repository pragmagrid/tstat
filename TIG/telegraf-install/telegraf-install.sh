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
}

installTelegraf() {
	debug "Setting up Telegraf repository..."
cat << EOF | tee /etc/yum.repos.d/influxdb.repo
[influxdb]
name = InfluxDB Repository - RHEL \$releasever
baseurl = https://repos.influxdata.com/rhel/\$releasever/\$basearch/stable
enabled = 1
gpgcheck = 1
gpgkey = https://repos.influxdata.com/influxdb.key
EOF

	debug "Installing Telegraf..."
	yum install -y telegraf 2>>$LOG_FILE
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
			INFLUX_URL\=* )  		INFLUX_URL=`parse $line` ;;
			INFLUX_USER\=* ) 		INFLUX_USER=`parse $line` ;;
			INFLUX_PASSWORD\=* ) 	INFLUX_PASSWORD=`parse $line` ;;
			TELEGRAF_INTERVAL\=* )  TELEGRAF_INTERVAL=`parse $line` ;;
			TELEGRAF_INPUTS\=* )    TELEGRAF_INPUTS=`parse $line` ;;
			* )           ;;
		esac
	done < $file
}

readingTelegrafInputAndGenerateConfigFile () {
	sh -c "telegraf --input-filter $TELEGRAF_INPUTS --output-filter influxdb config | tee > /etc/telegraf/telegraf.conf"
}

setDefaultsAndStartTelegraf() {
	debug "Set defaults variable and configure InfluxDB"

	[[ -z "$INFLUX_URL" ]] 			&& debug "INFLUX_URL variable must be set in configuration file" && exit 1
	[[ -z "$INFLUX_USER" ]] 		&& INFLUX_USER=""	
	[[ -z "$INFLUX_PASSWORD" ]] 	&& INFLUX_PASSWORD=""			
	[[ -z "$TELEGRAF_INTERVAL" ]] 	&& TELEGRAF_INTERVAL="5s"		
	[[ -z "$TELEGRAF_INPUTS" ]] 	&& TELEGRAF_INPUTS="cpu:mem:net:swap:disk:diskio:netstat:system"		

	readingTelegrafInputAndGenerateConfigFile

	sed -i "s/  # urls = \[\"http:\/\/127.0.0.1:8086\"\]/  urls = \[\"${INFLUX_URL}\"\]/" 			/etc/telegraf/telegraf.conf
	exitIfHaveError
	
	sed -i "s/  # username = \"telegraf\"/  username = \"$INFLUX_USER\"/" 							/etc/telegraf/telegraf.conf
	exitIfHaveError
	
	sed -i "s/  # password = \"metricsmetricsmetricsmetrics\"/  password = \"$INFLUX_PASSWORD\"/" 	/etc/telegraf/telegraf.conf
	exitIfHaveError
	
	sed -i "s/  interval = \"10s\"/  interval = \""$TELEGRAF_INTERVAL\""/" 							/etc/telegraf/telegraf.conf
	exitIfHaveError

	sed -i "s/  hostname = \"\"/  hostname = \""$TELEGRAF_HOSTNAME"\"/" 							/etc/telegraf/telegraf.conf
	exitIfHaveError

	systemctl restart telegraf 2>>$LOG_FILE
	exitIfHaveError
}

### MAIN ###
setUpConstants
installDependencies
installTelegraf
readingConfigFile $1
setDefaultsAndStartTelegraf
debug "Telegraf succesfully install at $(date '+%Y-%m-%d %H:%M:%S')"
