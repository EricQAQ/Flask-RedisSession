__author__ = 'Eric'


from flask import Flask
from flask_redisSession import RedisSession

app = Flask(__name__)
RedisSession(app)
print('++++++++++++++++++++++++++++')
print(app.config['PERMANENT_SESSION_LIFETIME'])
print('++++++++++++++++++++++++++++')