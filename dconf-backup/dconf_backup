#!/bin/sh

filename="$1"

if [ -z "$filename" ]
then
	echo "You need to specify the section to backup." 1>&2
	exit 1
fi

db_location="${filename#./}"
db_location="/$(echo "${db_location%.dump}" | tr '.' '/')/"

dconf dump "$db_location" > "$filename"
