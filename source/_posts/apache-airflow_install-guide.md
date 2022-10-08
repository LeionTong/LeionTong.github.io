---
title: installation guide for apache-airflow
date: 2018-08-15T16:05:00.000Z
tags: null
---
# installation guide for apache-airflow

## install requisitions

`yum install python python-pip python-setuptools python-dev`

or if you use python34:

`yum install python34 python34-pip python34-setuptools python34-dev`

or python36:

`yum install python36 python36-pip python36-setuptools python36-dev`


## install airflow

`su - deploy   #切换到普通用户`

```
# airflow needs a home, ~/airflow is the default,
# but you can lay foundation somewhere else if you prefer
# (optional)
export AIRFLOW_HOME=~/airflow

# install from pypi using pip
pip install apache-airflow

# initialize the database
airflow initdb

# start the web server, default port is 8080
airflow webserver -p 8080
```

<!-- more --> 

## Problem：

```
$ airflow webserver -p 8080
[2018-08-15 14:45:46,337] {__init__.py:45} INFO - Using executor SequentialExecutor
  ____________       _____________
 ____    |__( )_________  __/__  /________      __
____  /| |_  /__  ___/_  /_ __  /_  __ \_ | /| / /
___  ___ |  / _  /   _  __/ _  / / /_/ /_ |/ |/ /
 _/_/  |_/_/  /_/    /_/    /_/  \____/____/|__/

/usr/lib64/python2.7/site-packages/flask/exthook.py:71: ExtDeprecationWarning: Importing flask.ext.cache is deprecated, use flask_cache instead.
  .format(x=modname), ExtDeprecationWarning
Traceback (most recent call last):
  File "/bin/airflow", line 27, in <module>
    args.func(args)
  File "/usr/lib/python2.7/site-packages/airflow/bin/cli.py", line 678, in webserver
    app = cached_app(conf)
  File "/usr/lib/python2.7/site-packages/airflow/www/app.py", line 161, in cached_app
    app = create_app(config)
  File "/usr/lib/python2.7/site-packages/airflow/www/app.py", line 59, in create_app
    from airflow.www import views
  File "/usr/lib/python2.7/site-packages/airflow/www/views.py", line 49, in <module>
    from jinja2.sandbox import ImmutableSandboxedEnvironment
  File "/usr/lib64/python2.7/site-packages/jinja2/sandbox.py", line 25, in <module>
    from markupsafe import EscapeFormatter
ImportError: cannot import name EscapeFormatter
```
## Solution：
sudo pip install -U markupsafe
