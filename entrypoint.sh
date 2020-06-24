#!/bin/sh

RETRY=${RETRY:-7}

echo 'ENTRYPOINT: ********************Cleaning __pycache__********************'
find . -regex '^.*\(__pycache__\|\.py[co]\)$' -delete

IS_DB_AWARE=1
test -n "${DB_HOST}" || IS_DB_AWARE=0
test -n "${DB_NAME}" || IS_DB_AWARE=0
test -n "${DB_HOST}" || IS_DB_AWARE=0
test -n "${DB_HOST}" || IS_DB_AWARE=0
if [ "${IS_DB_AWARE}" -eq 1 ]; then
  echo 'ENTRYPOINT: *******************Preparing the database*******************'

  if python manage.py wait_for_db --retry "${RETRY}" && [ "${DB_MIGRATE}" = "true" ]; then
    python manage.py migrate
  else
    exit 1
  fi
fi

echo 'ENTRYPOINT: ****************************EXEC****************************'
exec "$@"
