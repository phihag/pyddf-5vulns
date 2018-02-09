#!/usr/bin/env python3

import argparse
import base64
import datetime
import http.cookies
import http.server
import json
import multiprocessing
import os
import re
import subprocess
import sys
import urllib.parse

import bottle



def _cur_user():
    session_b64 = bottle.request.get_cookie('vulns_session')
    if not session_b64:
        return None
    session_json = base64.b64decode(session_b64)
    session_data = json.loads(session_json)
    assert isinstance(session_data, dict)
    user = session_data.get('user')
    assert user is None or isinstance(user, str)
    return user


def require_user(func):
    def handler():
        user = _cur_user()
        if not user:
            bottle.abort(403, 'Please log in to user this function')
            return
        return func(user)

    return handler

@bottle.route('/')
def root():
    user = _cur_user()

    return ('''<!DOCTYPE html>
    <html>
    <head><meta charset="utf-8" />
    <style>
    html, body, input, textarea, button {
        font-size: 20px;
    }
    input[name="to"] {
        width:7em;
    }
    input[name="e"] {
        width:3em;
        text-align:right;
    }
    </style>
    <title>Vulnerable django app</title></head>
    <body>''' + ('''
        <form action="/logout" method="post" style="margin-bottom:2em">
        Eingeloggt als ''' + user + '''<button>Logout</button>
        </form>

    <form action="/transfer">
      <input name="e" value="42"/> € an
      <input name="to" value="Max Muster" />
      <button>überweisen</button>
    </form>
    ''' if user else '''
    <form action="/login" method="post" style="margin-bottom:2em">
    <input type="text" required="required" name="user" placeholder="Benutzername" autofocus="autofocus" />
    <input type="password" name="password" placeholder="Passwort" />
    <button>Login</button>
    </form>
    ''') + '''
        </body></html>''')


@bottle.route('/login', method='POST')
def login():
    user = bottle.request.forms.get('user')
    assert user

    session = {
        'user': user,
    }
    session_json = json.dumps(session)
    session_b64 = base64.b64encode(session_json.encode('utf-8'))

    expires = datetime.datetime.utcnow() + datetime.timedelta(days=400)
    bottle.response.set_cookie('vulns_session', session_b64.decode('utf-8'), expires=expires)
    bottle.redirect('/')


@bottle.route('/logout', method='POST')
def logout():
    bottle.response.set_cookie('vulns_session', '', expires=0)
    bottle.redirect('/')


@bottle.route('/transfer')
@require_user
def transfer(user):
    e = bottle.request.query['e']
    to = bottle.request.query['to']
    # TODO: Überweisungslogik hier
    return '%s € wurde von %s an %s überwiesen!' % (e, user, to)


def main():
    parser = argparse.ArgumentParser(description='vulnerable web server')
    parser.add_argument(
        '--port', metavar='PORT',
        type=int, default=8007,
        help='Port to bind to (default %(default)s)')
    parser.add_argument(
        '--addr', metavar='ADDRESS',
        default='',
        help='IP address to bind to (default: unspecified)')
    parser.add_argument(
        '--dev',
        action='store_true',
        help='Respawn on file changes')
    args = parser.parse_args()

    if args.dev:
        dev(args)
    else:
        run_server(args)


def run_server(args):
    bottle.run(host=args.addr, port=args.port, debug=True)


def dev(args):
    p = multiprocessing.Process(target=run_server, args=(args,))
    p.start()

    subprocess.check_output(['inotifywait', '-q', '-e', 'close_write', __file__])

    p.terminate()
    p.join()

    os.execv(__file__, sys.argv)


if __name__ == '__main__':
    main()
