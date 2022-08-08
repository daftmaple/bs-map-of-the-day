from flask import Flask, jsonify

import motd_playlist

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello there"

@app.route('/api/playlist')
def playlist():
    return jsonify(motd_playlist.create_playlist())
