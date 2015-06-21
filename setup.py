
"""
Flask-RedisSession
-------------

The users can use this extension to add server-side session to your application.
"""
from setuptools import setup


setup(
    name='Flask-RedisSession',
    version='0.1.2',
    url='https://github.com/EricQAQ/Flask-Redis-Session',
    license='MIT',
    author='Eric Zhang',
    author_email='zhangzy93@163.com',
    description='add server-side session, stored by Redis',
    long_description=__doc__,
    packages=['flask_redisSession'],
    test_suite='test',
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask>=0.8'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)