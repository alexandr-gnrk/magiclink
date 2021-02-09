import functools
import secrets
import urllib

import flask

from . import orm


NBYTES = 32
DB = orm.MagiclinkDB()


def verify_access(func):

    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        token = flask.session.pop('token', None)
        route = str(flask.request.url_rule)

        if not token or not verify_connection(token, route):
            return flask.render_template('not_allowed.html')
        else:
            value = func(*args, **kwargs)
            return value

    return wrapper_decorator


def generate_token():
    return secrets.token_urlsafe(NBYTES)


def revoke(token):
    DB.revoke(token)


def save_record(email, token, route):
    DB.add_magiclink(email, token, route)


def update_counter(token):
    DB.increment_counter(token)


def verify_connection(token, route):
    return DB.verify_token_and_route(token, route)


def token_to_magiclink(token):
    return flask.url_for('magiclink', token=token, _external=True)


def token_to_reallink(token):
    route = DB.find_by_token(token).route
    host_url = flask.request.host_url
    url = urllib.parse.urljoin(host_url, route)
    return url

def token_to_revokelink(token):
    return flask.url_for('revoke', token=token, _external=True)


def adapt_records_for_templates():
    records = list()
    for row in DB.get_all():
        records.append({
            'id': row.id,
            'email': row.email,
            'revoke_link': token_to_revokelink(row.token),
            'link': token_to_magiclink(row.token),
            'route': row.route,
            'counter': row.counter,
            'revoked': row.revoked
        })

    return records
