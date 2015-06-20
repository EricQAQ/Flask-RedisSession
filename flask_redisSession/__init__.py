"""
    flask-redis-session
    ----------------------------
    The users can use this extension to add server-side session to your application.
    The flask/werkzeug uses client-side session, that is, the cookies, to store the state.

    :license: MIT, see LICENSE for more details.
    :Date: June, 2015
    :written by Eric
"""

try:
    import pickle
except ImportError:
    import cPickle as pickle
from uuid import uuid4
from flask.sessions import SessionInterface, SessionMixin, total_seconds
from werkzeug.datastructures import CallbackDict
from itsdangerous import Signer, BadSignature

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

    def __init__(self, app=None):
        """This method is going to init the flask app.
        :param app: The flask application that you want to init
        :param session_expire_time: set the session expire time,
                which default value is PERMANENT_SESSION_LIFETIME
        :return: None
        """
        if app is not None:
            self.app = app
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        config = app.config
        config.setdefault('SESSION_KEY_PREFIX', 'sessionID:')
        config.setdefault('REDIS_SESSION', None)    #whether has redis instance
        config.setdefault('USE_SECRET_KEY', True)   #use the signer or not

        config.setdefault('SESSION_REFRESH_EACH_REQUEST', True)

        #following config is just for the app do not have redis instance
        config.setdefault('REDIS_HOST', 'localhost')
        config.setdefault('REDIS_PORT', 6379)
        config.setdefault('REDIS_DB', 0)
        config.setdefault('REDIS_PASSWORD', None)
        config.setdefault('USE_REDIS_CONNECTION_POOL', False)   #use the connection pool or not
        config.setdefault('MAX_CONNECTION', None)   #the max number of connections.Valid when using connection pool

        app.session_interface = ServerSessionInterface(
            config['REDIS_SESSION'], config['USE_SECRET_KEY'],
            config['SESSION_KEY_PREFIX'], config['USE_REDIS_CONNECTION_POOL'],
            config['PERMANENT_SESSION_LIFETIME'], config['REDIS_HOST'],
            config['REDIS_PORT'], config['REDIS_DB'],
            config['REDIS_PASSWORD'], config['MAX_CONNECTION']
        )


class ServerSession(CallbackDict, SessionMixin):
    """Base class. It will be called by the methods of the ServerSessionInterface"""
    def __init__(self, initial=None, session_id=None):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.modified = True
        self.permanent = True   #store the session. Without this, the session will not be stored
        self.session_id = session_id


class ServerSessionMixin(object):
    def generate_sessionid(self):
        return str(uuid4())


class ServerSessionInterface(SessionInterface, ServerSessionMixin):

    serialization_method = pickle

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
        sessionid = request.cookies.get(app.session_cookie_name, None)
        if sessionid is None:
            sessionid = self.generate_sessionid()
            return ServerSession(session_id=sessionid)

        if self.use_sign and app.secret_key:
            signer = Signer(app.secret_key, salt='flask-redis-session',
                            key_derivation='hmac')
            try:
                sessionid = signer.unsign(sessionid).decode('utf-8')
            except BadSignature:
                sessionid = None

        data = self.redis.get(self.session_prefix + sessionid)
        if data is None:
            return ServerSession(session_id=sessionid)
        try:
            json_data = self.serialization_method.loads(data)
            return ServerSession(json_data, session_id=sessionid)
        except:
            return ServerSession(session_id=sessionid)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        if not session:
            if session.modified:
                self.redis.delete(self.session_prefix + session.session_id)
                response.delete_cookie(app.session_cookie_name,
                                       domain=domain, path=path)
            return

        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        expire = self.get_expiration_time(app, session)
        serialize_session = self.serialization_method.dumps(dict(session))
        pipe = self.redis.pipeline()
        pipe.set(self.session_prefix + session.session_id, serialize_session)
        pipe.expire(self.session_prefix + session.session_id, total_seconds(self.expire_time))
        pipe.execute()

        if self.use_sign:
            session_id = Signer(app.secret_key, salt='flask-redis-session',
                                key_derivation='hmac').sign(session.session_id.encode('utf-8'))
            session_id = session_id.decode('utf-8')

        else:
            session_id = session.session_id
            print('session_id:', session_id)
        response.set_cookie(key=app.session_cookie_name, value=session_id,
                            max_age=self.expire_time, expires=expire,
                            path=path, domain=domain,
                            secure=secure, httponly=httponly)