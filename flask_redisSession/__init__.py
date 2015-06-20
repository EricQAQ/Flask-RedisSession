"""
    flask-redis-session
    ----------------------------
    The users can use this extension to add server-side session to your application.
    The flask/werkzeug uses client-side session, that is, the cookies, to store the state.

    :license: MIT, see LICENSE for more details.
    :Date: June, 2015
    :written by Eric
"""

import datetime
from uuid import uuid4
from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict


class RedisSession(object):
    """The users can use This class to make a server-side session.
    There are two ways to use this extension to make a server-side session for your application

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
    """

    def __init__(self, app=None, session_expire_time=None):
        """This method is going to init the flask app.
        :param app: The flask application that you want to init
        :param session_expire_time: set the session expire time,
                which default value is PERMANENT_SESSION_LIFETIME
        :return: None
        """
        if app is not None:
            self.app = app
            if session_expire_time is not None:
                self.init_app(app, session_expire_time)
            else:
                self.init_app(app, session_expire_time=app.config['PERMANENT_SESSION_LIFETIME'])
        else:
            self.app = None

    def init_app(self, app, session_expire_time=None):
        config = app.config
        config.setdefault('SESSION_KEY_PREFIX', 'sessionID:')
        config.setdefault('REDIS_SESSION', None)    #whether has redis instance
        config.setdefault('USE_SECRET_KEY', True)   #use the signer or not

        #following config is just for the app do not have redis instance
        config.setdefault('REDIS_HOST', 'localhost')
        config.setdefault('REDIS_PORT', 6379)
        config.setdefault('REDIS_DB', 0)
        config.setdefault('REDIS_PASSWORD', None)
        config.setdefault('USE_REDIS_CONNECTION_POOL', False)   #use the connection pool or not
        config.setdefault('MAX_CONNECTION', None)   #the max number of connections.Valid when using connection pool

        if session_expire_time is not None and isinstance(session_expire_time, int): #change the session expire time
            config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(session_expire_time)

        app.session_interface = ServerSessionInterface(
            config['REDIS_SESSION'], config['USE_SECRET_KEY'],
            config['SESSION_KEY_PREFIX'], config['USE_REDIS_CONNECTION_POOL'],
            config['PERMANENT_SESSION_LIFETIME'], config['REDIS_HOST'],
            config['REDIS_PORT'], config['REDIS_DB'],
            config['REDIS_PASSWORD'], config['MAX_CONNECTION'])


class ServerSession(CallbackDict, SessionMixin):
    """Base class. It will be called by the methods of the ServerSessionInterface"""
    def __init__(self, initial=None, sessionid=None):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.modified = True
        self.permanent = True   #store the session. Without this, the session will not be stored
        self.sessionid = sessionid

class ServerSessionMixin(object):
    def generate_sessionid(self):
        return str(uuid4())


class ServerSessionInterface(SessionInterface, ServerSessionMixin):

    def __init__(self, redis, use_sign, session_prefix, use_redis_connection_pool,
                 expire_time, redis_host, redis_port, redis_db, redis_pw, max_conn=None):
        if redis is None:
            from redis import StrictRedis
            if use_redis_connection_pool:
                from redis import ConnectionPool
                pool = ConnectionPool(host=redis_host, port=redis_port,
                                      db=redis_db, max_connections=max_conn)
                redis = StrictRedis(connection_pool=pool)
            else:
                redis = StrictRedis(host=redis_host, port=redis_port,
                                    db=redis_db, password=redis_pw)
        self.redis = redis
        self.use_sign = use_sign
        self.session_prefix = session_prefix
        self.expire_time = expire_time

    def open_session(self, app, request):
        pass


    def save_session(self, app, session, response):
        pass