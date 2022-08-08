from flask import Flask, jsonify

import motd_playlist

app = Flask(__name__)

@app.route('/api/playlist')
def playlist():
    return motd_playlist.create_playlist()
