import secrets
import urllib

import flask

import orm


NBYTES = 32
DB = orm.MagiclinkDB()


def generate_token():
    return secrets.token_urlsafe(NBYTES)

def save_record(email, token, route):
    # save record to DB
    DB.add_magiclink(email, token, route)

def update_counter(token):
    DB.increment_counter(token)

def token_to_magiclink(token):
    return flask.url_for(f'magiclink', token=token, _external=True)

def token_to_reallink(token):
    route = DB.find_by_token(token).route
    host_url = flask.request.host_url
    url = urllib.parse.urljoin(host_url, route)
    # add token parametr
    url += '?token={}'.format(token) 
    return url

def adapt_records_for_templates():
    records = list()
    for row in DB.get_all():
        records.append({
            'id': row.id,
            'email': row.email,
            'link': token_to_magiclink(row.token),
            'route': row.route,
            'counter': row.counter,
            'revoked': row.revoked
        })

    return records
