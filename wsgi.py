#!/usr/bin/env python
# coding=utf-8

from app import app as flask_app
application = flask_app

if __name__ == "__main__":
    application.run()