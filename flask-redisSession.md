# Flask-RedisSession
--
This is a server-side session extension for Flask, which uses Redis to store the session.

The users can use this extension to add server-side session to your application.
    The flask/werkzeug uses client-side session, that is, the cookies, to store the state.
    This extension can only be used in Python3.

:license: MIT, see LICENSE for more details.
:Date: June, 2015

##How to use this extension
First, you have to import the extension like this:

	from flask.ext.redisSession import RedisSession
Then, there are two ways to use this extension to make a server-side session for your application

* Just like the simple flask application:

```python
app = Flask(__name__)
RedisSession(app)
```

* The other way is create a object and run the application latter:

```python
redisSession = RedisSession()
app = Flask(__name__)

def create_app(self, app):
	redisSession.init_app(app)
	return app
```
Be sure that you already have **Redis Database** and **redis-py**. If you do not have **redis-py**, you can install it like this:

	pip install redis
##Config
in this extension, it has following configuration:

configuration  | default | mean
:-------------: | :-------------: | :-------------:
SESSION\_KEY\_PREFIX  | 'sessionID:' | The key prefix
REDIS_SESSION  | None | whether has redis instance
USE\_SECRET\_KEY | True | use the signer or not
SESSION\_REFRESH\_EACH_REQUEST | True
REDIS_HOST | 'localhost' | The host of the Redis
REDIS_PORT | 6379 | The port of the Redis
REDIS_DB | 0 | The database of the Redis to use
REDIS_PASSWORD | None | The password of the Redis
USE\_REDIS\_CONNECTION_POOL | False | whether use the connection pool
MAX_CONNECTION | None | the max number of the connection

You have to set these configurations in your config file, or using the default value.

