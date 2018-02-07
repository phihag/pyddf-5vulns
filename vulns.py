#!/usr/bin/env python3

import argparse
import http.cookies
import http.server
import json
import re
import multiprocessing


class VulnHandler(http.server.BaseHTTPRequestHandler):
    views = []

    def send_text(self, txt, mime='text/html;charset=utf-8'):
        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.send_header(
            'Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        self.wfile.write(txt.encode('utf-8'))

    def do_GET(self):
        for (rex, v) in self.views:
            if rex.match(self.path):
                return v(self)

        self.send_error(404)


def view(rex_str):
    rex = re.compile(rex_str)

    def decorate(func):
        VulnHandler.views.append((rex, func))
        return func

    return decorate


def _get_cookie(headers, key, default=None):
    c = http.cookies.SimpleCookie(headers['Cookie'])
    morsel = c.get(key)
    return morsel.value if morsel else default


def cur_user(handler):
    session_json = _get_cookie('vulns_session')
    if not session_json:
        return None
    session_data = json.loads(session_json)
    assert isinstance(session_data, dict)
    user = session_data.get('user')
    assert user is None or isinstance(user, str)
    return user


@view(r'^/$')
def _root_handler(handler):
    handler.send_text('''<!DOCTYPE html>
    <html>
    <head><meta charset="utf-8" />
    <style>
    html, body, input, textarea, button {
        font-size: 20px;
    }
    input[name="euro"] {
        width:3em;
        text-align:right;
    }
    </style>
    <title>Vulnerable django app</title></head>
    <body>''' + ('''
        <form action="/logout" method="post" style="margin-bottom:2em">
        <button>Logout</button>
        </form>''' if cur_user(handler) else '''
    <form action="/login" method="post" style="margin-bottom:2em">
    <input type="text" name="user" />
    <input type="password" name="password" />
    <button>Login</button>
    </form>
    ''') + '''<form target="/transfer_money/">
      <input name="euro" value="42"/> € an
      <input name="receiver" value="Max Muster"/>
      <button>überweisen</button>
    </form>
        </body></html>''')


@view(r'^/login$')
def login_view(handler):
    print(handler.method)



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


if __name__ == '__main__':
    main()
