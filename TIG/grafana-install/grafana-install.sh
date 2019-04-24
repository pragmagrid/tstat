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

installAndStartGrafana() {
	debug "Installing and starting grafana..."
	yum -y install https://dl.grafana.com/oss/release/grafana-5.4.2-1.x86_64.rpm
	exitIfHaveError

	# service grafana-server start 2>>$LOG_FILE
	exitIfHaveError
}

modifyGrafanaConfiguration() {
	MODIFY_VARIABLE=$1
	VARIABLE_VALUE=$2
	if [ -z "$MODIFY_VARIABLE" ] || [ -z "$VARIABLE_VALUE" ]; then
		debug "Don't have value to modify ($MODIFY_VARIABLE, $VARIABLE_VALUE)"
		return
	fi

	MODIFY_PHRASE=$MODIFY_VARIABLE=$VARIABLE_VALUE
	GF_SYS_CONF_FILE=/etc/sysconfig/grafana-server
	if grep -Fq "$MODIFY_VARIABLE" $GF_SYS_CONF_FILE
	then # already have configuration
		sed -i "s/$MODIFY_VARIABLE=.*/$MODIFY_PHRASE/g" $GF_SYS_CONF_FILE 2>>$LOG_FILE
		debug "Replace config $MODIFY_PHRASE at $GF_SYS_CONF_FILE"
		exitIfHaveError
	else # not found configuration
		echo "$MODIFY_PHRASE" >> $GF_SYS_CONF_FILE
		debug "Add config $MODIFY_PHRASE to $GF_SYS_CONF_FILE"
	fi
}

modifyGrafanaConfigurationAndStart() {
	debug "Modify grafana configuration and restart..."

	modifyGrafanaConfiguration "GF_AUTH_ANONYMOUS_ENABLED" $GF_AUTH_ANONYMOUS_ENABLED
	modifyGrafanaConfiguration "GF_SECURITY_ADMIN_USER" $GF_SECURITY_ADMIN_USER
	modifyGrafanaConfiguration "GF_SECURITY_ADMIN_PASSWORD" $GF_SECURITY_ADMIN_PASSWORD
	modifyGrafanaConfiguration "GF_SERVER_HTTP_PORT" $GF_SERVER_HTTP_PORT
	modifyGrafanaConfiguration "GF_SERVER_ROOT_URL" $GF_SERVER_ROOT_URL:$GF_SERVER_HTTP_PORT

	service grafana-server start 2>>$LOG_FILE
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
			GF_AUTH_ANONYMOUS_ENABLED\=* )  GF_AUTH_ANONYMOUS_ENABLED=`parse $line` ;;
			GF_SECURITY_ADMIN_USER\=* ) 	GF_SECURITY_ADMIN_USER=`parse $line` ;;
			GF_SECURITY_ADMIN_PASSWORD\=* ) GF_SECURITY_ADMIN_PASSWORD=`parse $line` ;;
			GF_SERVER_HTTP_PORT\=* )    	GF_SERVER_HTTP_PORT=`parse $line` ;;
			GF_SERVER_ROOT_URL\=* )    		GF_SERVER_ROOT_URL=`parse $line` ;;
			CONF_DIR\=* )    				CONF_DIR=`parse $line` ;;
			* )           ;;
		esac
	done < $file
}

getPassword () {
    word=`mkpasswd -l $1 -s 0 2>>$LOG_FILE`
    echo $word
}

setDefaults() {
	debug "Set defaults variable and configure for Grafana"

	setcap 'cap_net_bind_service=+ep' /usr/sbin/grafana-server # Give port 80 permission to Grafana

	[[ -z "$GF_AUTH_ANONYMOUS_ENABLED" ]] 	&& GF_AUTH_ANONYMOUS_ENABLED=false
	[[ -z "$GF_SECURITY_ADMIN_USER" ]] 		&& GF_SECURITY_ADMIN_USER=pragma_admin
	[[ -z "$GF_SERVER_HTTP_PORT" ]] 		&& GF_SERVER_HTTP_PORT=3000			
	[[ -z "$GF_SERVER_ROOT_URL" ]] 			&& GF_SERVER_ROOT_URL=http://localhost	
	[[ -z "$CONF_DIR" ]] 					&& CONF_DIR=/etc/grafana

	if [ -z "$GF_SECURITY_ADMIN_PASSWORD" ] ; then
		debug "Generating random password..."
		GF_SECURITY_ADMIN_PASSWORD=$(getPassword 10)
	fi

	modifyGrafanaConfigurationAndStart

	createPassFile
}

createPassFile () {
    # create a file with pasword for DB access, save previous if exist
	PASS_FILE=$CONF_DIR/$GF_SECURITY_ADMIN_USER.pass

	debug "Writing password file at $PASS_FILE"
    echo $GF_SECURITY_ADMIN_PASSWORD > $PASS_FILE 2>>$LOG_FILE
    chmod 600 $PASS_FILE 
}

## MAIN ##
setUpConstants
installDependencies
installAndStartGrafana
readingConfigFile $1
setDefaults
debug "Grafana succesfully install at $(date '+%Y-%m-%d %H:%M:%S')"