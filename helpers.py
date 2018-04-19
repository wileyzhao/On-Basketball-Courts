import csv
import urllib.request
import random

from flask import redirect, render_template, request, session, url_for
from functools import wraps


def usd(value):
    """Formats value as USD."""
    return "${:,.2f}".format(value)

def apology(message=""):
    return render_template("apology.html", message=message)


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function