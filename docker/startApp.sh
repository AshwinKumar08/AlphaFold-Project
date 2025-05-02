#!/bin/bash
echo "="
echo "= Fixing file owner for /app/data"
echo "==================================="
chown -R www-data:www-data /app/data
chown -R www-data:www-data /app/results
echo "="
echo "= Running Tests"
echo "==================================="
su -P -s /bin/bash www-data -c 'python -m unittest tests || sleep 120'
echo "="
echo "= Starting Server"
echo "==================================="
su -P -s /bin/bash www-data -c 'flask --debug run --host 0.0.0.0'
