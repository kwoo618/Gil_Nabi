start /min "" cmd /c "cd /d C:\Program Files\Redis && redis-server.exe redis.windows.conf"
python manage.py runserver
