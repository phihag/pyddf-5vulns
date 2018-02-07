from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.middleware.csrf import get_token


@login_required
def home(request):
    html = '''<!DOCTYPE html>
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
<body>
<form action="/accounts/logout/" method="post" style="margin-bottom:2em">
<input type="hidden" name="csrfmiddlewaretoken" value="%s" />
<button>Logout</button>
</form>

<form target="/transfer_money/">
  <input name="euro" value="42"/> € an
  <input name="receiver" value="Max Muster"/>
  <button>überweisen</button>
</form>
    </body></html>''' % (get_token(request))
    return HttpResponse(html)


@require_login
def transfer_money(request):
  # TODO require login
  return HttpResponse(
      '<html> base64 {}!</html>'.format(b64))
