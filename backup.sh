#!/bin/bash

export AWS_ACCESS_KEY_ID=$S3_WRITEONLY_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=$S3_WRITEONLY_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=eu-north-1

pip install awscli

pg_dump $DATABASE_URL > tmp

BACKUP_FILE=backup_$(date +"%Y-%m-%dT%H:%M:%S%z")
gpg --symmetric --output $BACKUP_FILE --cipher-algo aes256 --passphrase $DB_BACKUP_ENCRYPTION_KEY --batch tmp
rm tmp

aws s3 cp $BACKUP_FILE s3://$BACKUP_BUCKET_NAME/

