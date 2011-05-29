ChopChop : Simple web interface to list & filter your centralized logs
========================================================

ChopChop is a simple app for viewing and filtering events logged into MongoDb. It's build on Flask (http://flask.pocoo.org/), Jinja2 (http://jinja.pocoo.org/) and Mongokit (https://github.com/namlook/mongokit). I've used CouchDB's admin interface fancy design & graphics.

The app expects the log table to have columns used by python logging module extension for MongoDb mongolog (https://github.com/andreisavu/mongodb-log) so typical row looks like:

    { "_id" : ObjectId("4d402bd7437946334300000f"), "args" : [ ],
        "name" : "traffic-info", "level" : "debug", "line_no" : 154,
        "funcname" : "notify", "host" : "kosmik1", "user" : "starenka",
        "file" : "./tinfo.py", "time" : "Wed Jan 26 2011 16:12:39 GMT+0100 (CET)",
        "msg" : "Item 8ad5a3b7-2d98-5ff7-012d-c13ce5c01319 has no wanted event code",
        "exc_info" : null
    }

nevertheless you can modify the template to suit your "scheme" in a breeze.

To see it in action, try this screenshot http://junk.starenka.net/chopchop.png


Setup
-----

To setup the app, just edit DB settings either in settings/base.py, settings/production.py or settings/local_empty.py to suit your needs. If you edit local_empty.py be sure to copy it as local.py in order to get loaded. The wsgi file should work w/out any tuning. Consult your web server docs to make wsgi work with your server. Sample vhost file for apache would look like this:

    root@kosmik1:/home/starenka# cat /etc/apache2/sites-available/logs.localhost
        <VirtualHost 127.0.0.1:80>
            ServerName logs.localhost
                WSGIDaemonProcess chopchop user=starenka group=starenka threads=5
                WSGIScriptAlias / /www/chopchop/chopchop.wsgi

                <Directory /www/chopchop>
                    WSGIProcessGroup chopchop
                    WSGIApplicationGroup %{GLOBAL}
                    WSGIScriptReloading On
                    Order deny,allow
                    Allow from all
                </Directory>
        </VirtualHost>

Have fun!

