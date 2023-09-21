#!/bin/bash
# Add the backup dir location, MySQL root password, MySQL and mysqldump location
DATE=$(date +%d-%m-%Y)
BACKUP_DIR="/backups/"
USER="root"
PASSWORD="dbrootdevel"

mkdir -p $BACKUP_DIR/$DATE

databases=`mysql -u $USER -p$PASSWORD -e "SHOW DATABASES ;" | tr -d "| " | grep -v Database`

for db in $databases; do
    if [[ "$db" != "information_schema" ]] && [[ "$db" != "performance_schema" ]] && [[ "$db" != "mysql" ]] && [[ "$db" != _* ]] ; then
        echo "Dumping database: $db"
        mysqldump --force --opt -u $USER -p$PASSWORD --lock-tables --databases $db | gzip > "$BACKUP_DIR/$DATE/$db.sql.gz" 
    fi
done


# Delete the files older than 10 days
find $BACKUP_DIR/* -mtime +10 -exec rm {} \;


# Delete empty folders
find $BACKUP_DIR/* -type d -empty -delete
