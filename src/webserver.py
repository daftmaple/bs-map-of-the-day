from flask import request, Flask, jsonify

import motd_playlist

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello there"

@app.route('/api/playlist')
def playlist():
    active = request.args.get('active')
    
    if active is None:
        active = False
    else:
        active = active.lower() == 'true'

    return jsonify(motd_playlist.create_playlist(active))
