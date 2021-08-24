# shellcheck disable=SC2006
DUMP_FILE_NAME="backupOn$(date +%Y-%m-%d-%H-%M).dump"
echo "Creating dump: $DUMP_FILE_NAME"

# shellcheck disable=SC2164
cd var/backups

export PGPASSWORD="$POSTGRES_PASSWORD"

pg_dump -C --dbname="$POSTGRES_DB" --host="$POSTGRES_HOST" --username="$POSTGRES_USER" --format=c --blobs >"$DUMP_FILE_NAME"

# shellcheck disable=SC2181
if [ $? -ne 0 ]; then
  rm "$DUMP_FILE_NAME"
  echo "Back up not created, check db connection settings"
  exit 1
fi

echo 'Successfully Backed Up'
exit 0
