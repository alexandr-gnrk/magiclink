import os
import secrets
import urllib

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from . import orm
from . import utils


app = Flask(__name__)
app.secret_key = os.getenv('MAGICLINK_KEY')


@app.route('/', methods=['GET', 'POST'])
def root():
    magiclink = None
   
    if request.method == 'POST':
        email = request.form['email']
        # extract path from url
        route = urllib.parse.urlparse(
            request.form['route']).path

        token = utils.generate_token()
        utils.save_record(email, token, route)

        magiclink = utils.token_to_magiclink(token)

    records = utils.adapt_records_for_templates()
    return render_template(
        'index.html',
        magiclink=magiclink,
        records=records)


@app.route('/magiclink/<token>')
def magiclink(token):
    utils.update_counter(token)
    session['token'] = token
    return redirect(utils.token_to_reallink(token))


@app.route('/revoke/<token>')
def revoke(token):
    utils.revoke(token)
    return redirect(url_for('root'))


@app.route('/treasure')
@utils.verify_access
def treasure():
    return render_template('treasure.html')


@app.route('/password')
@utils.verify_access
def password():
    return render_template('password.html')


if __name__ == '__main__':
    app.run(debug=True)