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


class VulnHandler(http.server.BaseHTTPRequestHandler):
    views_by_method = {}

    def send_text(self, txt, mime='text/html;charset=utf-8'):
        bts = txt.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', '%s' % len(bts))
        self.send_header(
            'Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        self.wfile.write(bts)

    def send_headers(self, headers):
        for k, v in headers.items():
            self.send_header(k, v)

    def redirect(self, to, code=302, headers=None):
        self.send_response(code)
        self.send_header('Location', to)
        self.send_header('Content-Type', 'text/plain')
        if headers:
            self.send_headers(headers)
        self.end_headers()
        self.wfile.write(('Redirect to %s' % to).encode('utf-8'))

    def handle_parsed_request(self):
        views = self.views_by_method.get(self.command, [])
        for (rex, v) in views:
            if rex.match(self.path):
                return v(self)

        self.send_error(404)

    do_GET = handle_parsed_request
    do_POST = handle_parsed_request
    do_HEAD = handle_parsed_request


def view(rex_str, method='GET'):
    rex = re.compile(rex_str)

    def decorate(func):
        views = VulnHandler.views_by_method.setdefault(method, [])
        views.append((rex, func))
        return func

    return decorate


def _get_cookie(headers, key, default=None):
    c = http.cookies.SimpleCookie(headers['Cookie'])
    morsel = c.get(key)
    return morsel.value if morsel else default


def cur_user(handler):
    session_b64 = _get_cookie(handler.headers, 'vulns_session')
    if not session_b64:
        return None
    session_json = base64.b64decode(session_b64)
    session_data = json.loads(session_json)
    assert isinstance(session_data, dict)
    user = session_data.get('user')
    assert user is None or isinstance(user, str)
    return user


def parse_post(handler):
    content_length = handler.headers['Content-Length']
    if content_length is None:
        return handler.send_error(411)
    length = int(content_length)

    raw_body = handler.rfile.read(length)
    tuples = urllib.parse.parse_qsl(raw_body)
    dct = {k.decode('utf-8'): v.decode('utf-8') for k, v in tuples}
    return dct


@view(r'^/$')
def root_handler(handler):
    user = cur_user(handler)

    handler.send_text('''<!DOCTYPE html>
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


@view(r'^/login$', method='POST')
def login(handler):
    post = parse_post(handler)
    assert post['user']

    session = {
        'user': post['user'],
    }
    session_json = json.dumps(session)
    session_b64 = base64.b64encode(session_json.encode('utf-8'))

    expires = datetime.datetime.utcnow() + datetime.timedelta(days=400)
    expires_str = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
    handler.redirect('/', code=303, headers={
        'Set-Cookie': 'vulns_session=' + session_b64.decode('utf-8') + '; expires=' + expires_str,
    })


@view(r'^/logout$', method='POST')
def logout(handler):
    handler.redirect('/', code=303, headers={
        'Set-Cookie': 'vulns_session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT',
    })


@view(r'^/transfer$', method='POST')
def transfer(handler):
    self.send_text('%s € wurde an %s überwiesen!' % (post['e'], post['to']))


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
    httpd = http.server.HTTPServer((args.addr, args.port), VulnHandler)
    httpd.serve_forever()


def dev(args):
    p = multiprocessing.Process(target=run_server, args=(args,))
    p.start()

    subprocess.check_output(['inotifywait', '-q', '-e', 'close_write', __file__])

    p.terminate()
    p.join()

    os.execv(__file__, sys.argv)


if __name__ == '__main__':
    main()
