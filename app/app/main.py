from __future__ import unicode_literals
import os

from flask import Flask, flash, render_template, request, jsonify
from flask_httpauth import HTTPBasicAuth
from requests.status_codes import codes as status_codes
import youtube_dl

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

app.jinja_env.globals.update({
    'app_title': 'Midnight Athletics Radio',
    'app_description': (
        'Commercial free radio featuring contemporary underground dance '
        'music from around the world.'
    ),
    'app_url': 'http://midnightathletics.com/',
})

auth = HTTPBasicAuth()


@auth.get_password
def get_pw(username):
    return os.environ['ICECAST_SOURCE_PASSWORD']


@app.route('/', methods=['GET'])
def root():
    return render_template('root.html')


@app.route('/mixes.json', methods=['GET'])
@auth.login_required
def mixes():
    mixes = os.listdir('/data/mixes')
    return jsonify(mixes), status_codes.OK


@app.route('/upload', methods=['GET', 'POST'])
@auth.login_required
def upload():
    if request.method == 'POST':
        url = request.form.get('url')
        filename = request.form.get('filename')
        if not url or not filename:
            flash('URL and filename required.', category='danger')
        try:
            ydl_args = {'outtmpl': '/data/mixes/{}.%(ext)s'.format(filename)}
            with youtube_dl.YoutubeDL(ydl_args) as ydl:
                ydl.download([url])
            flash('Uploaded {}'.format(filename), category='success')
        except youtube_dl.utils.DownloadError as e:
            flash(str(e), category='danger')
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
