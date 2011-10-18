ChopChop : Simple web interface to list & filter your centralized logs
========================================================

ChopChop is a simple app for viewing and filtering events logged into MongoDb. It's build on Flask (http://flask.pocoo.org/), Jinja2 (http://jinja.pocoo.org/) and Mongokit (https://github.com/namlook/mongokit). I've used CouchDB's admin interface fancy design & graphics.

The app expects the log table to have columns used by python logging module extension for MongoDb log4mongo (https://github.com/log4mongo/log4mongo-python) so typical row looks like:

    {   "_id" : ObjectId("4e9dc89b4379463df4000001"),
        "lineNumber" : 70,
        "thread" : NumberLong("139816043067136"),
        "level" : "INFO",
        "timestamp" : { "t" : 1318963355000, "i" : 886 },
        "message" : "Job finished ['./newsletter.py', '-r', '-t'], time elapsed 0:00:00.143399",
        "fileName" : "/xxx/meh.py",
        "method" : "close_job",
        "loggerName" : "meh"
    }

nevertheless you can modify the template to suit your "scheme" in a breeze.

To see it in action, try this screenshot http://junk.starenka.net/chopchop.png


Setup
-----

To setup the app, just edit your settings either in settings/base.py (used both on dev and production), settings/production.py or settings/local_empty.py to suit your needs. If you edit local_empty.py be sure to copy it as local.py in order to get loaded during development.

The WSGI file should work w/out any tuning. Consult your web server docs to make wsgi work with your server. Sample vhost file for Apache would look like this:


    root@kosmik1:/home/starenka# cat /etc/apache2/sites-available/logs.localhost
        <VirtualHost 127.0.0.1:80>
            ServerName logs.localhost
                WSGIDaemonProcess chopchop user=starenka group=starenka threads=5
                WSGIScriptAlias / /www/chopchop/app.wsgi

                <Directory /www/chopchop>
                    WSGIProcessGroup chopchop
                    WSGIApplicationGroup %{GLOBAL}
                    WSGIScriptReloading On
                    Order deny,allow
                    Allow from all
                </Directory>
        </VirtualHost>


As for nginx and uWSGI & supervisor your config would look like this:

supervisor:
---

    [program:logs.starenka.net]
    command=/usr/local/bin/uwsgi
      --socket /www/logs/uwsgi.sock
      --pythonpath /www/logs
      --touch-reload /www/logs/app.wsgi
      --chmod-socket 666
      --uid starenka
      --gid starenka
      --processes 1
      --master
      --no-orphans
      --max-requests 5000
      --module chopchop
      --callable app
    directory=/www/logs/
    stdout_logfile=/www/logs/uwsgi.log
    user=starenka
    autostart=true
    autorestart=true
    redirect_stderr=true
    stopsignal=QUIT

nginx:
---

    server {
            listen       80;
            server_name  logs.starenka.net;
            root    /www/logs/;

            access_log  /www/logs/access.log;
            error_log /www/logs/error.log;

            location / {
                    uwsgi_pass unix:///www/logs/uwsgi.sock;
                    include        uwsgi_params;
            }

            location /static {
                    alias /www/logs/static;
            }
    }



Have fun!

