__author__ = 'Eric'


from flask import Flask, session, request
from flask_redisSession import RedisSession
from datetime import timedelta

import unittest

'''
app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=40)
RedisSession(app)
print('++++++++++++++++++++++++++++')
print(app.config['PERMANENT_SESSION_LIFETIME'])
print('++++++++++++++++++++++++++++')
'''


class FlaskRedisSessionTestClass(unittest.TestCase):

    def test_redis_session_secret_key(self):
        app = Flask(__name__)
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=10)
        app.config['SECRET_KEY'] = '12345'
        RedisSession(app)

        @app.route('/set', methods=['POST'])
        def set():
            session['This is a test'] = request.form['This is a test']
            return 'A test!'
        @app.route('/get')
        def get():
            return session['This is a test']
        @app.route('/delete', methods=['POST'])
        def delete():
            del session['This is a test']
            return 'The test deleted'

        c = app.test_client()
        self.assertEqual(c.post('/set', data={'This is a test': 'Eric'}).data, b'A test!')
        self.assertEqual(c.get('/get').data, b'Eric')
        c.post('/delete')

    def test_redis_session_no_secret_key(self):
        app = Flask(__name__)
        app.config['USE_SECRET_KEY'] = False
        RedisSession(app)

        @app.route('/set', methods=['POST'])
        def set():
            session['This is a test'] = request.form['This is a test']
            return 'A test!'
        @app.route('/get')
        def get():
            return session['This is a test']
        @app.route('/delete', methods=['POST'])
        def delete():
            del session['This is a test']
            return 'The test deleted'

        c = app.test_client()
        self.assertEqual(c.post('/set', data={'This is a test': 'Eric'}).data, b'A test!')
        self.assertEqual(c.get('/get').data, b'Eric')
        c.post('/delete')

if __name__ == "__main__":
    unittest.main()