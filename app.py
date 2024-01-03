from flask import Flask, flash, render_template, request, redirect, url_for, session, jsonify, send_file
from music_app_services import UserService, SongService, AlbumService, PlaylistService, PlaylistSongService, AlbumSongService
import os
from werkzeug.utils import secure_filename
from music_app_models import Song
from json import dumps
from flask_cors import CORS
import eyed3 

UPLOAD_FOLDER = "./static"
app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
CORS(app, resources={r"/static/*": {"origins": "*"}})
app.secret_key = '1998' 



# Only allow certain file types
ALLOWED_EXTENSIONS = {'mp3','png','jpeg'}

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['registerUsername']
    password = request.form['registerPassword']
    role = request.form['role'] 
    print(username+" "+password)
    if role == 'General User' or role == 'Creator':
        user = UserService.create_user(username, password, role)
        if user:
            return redirect(url_for('index'))
        else:
            return "Unable to create user"
    else:
        return "Invalid role selected. Please try again."

@app.route('/login', methods=['POST'])
def login():
    username = request.form['loginUsername']
    password = request.form['loginPassword']
    user = UserService.get_user_by_username(username)
    if user and user.password == password:
        session['user_id'] = user.id
        return redirect(url_for('dashboard'))
    else:
        return "Invalid credentials. Please try again."

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        user = UserService.get_user_by_id(user_id)
        users = UserService.get_all_users()
        songs = SongService.get_all_songs()
        albums = AlbumService.get_all_albums()
        if user.role == 'Admin':
            return render_template('admin_dashboard.html', users=users, songs=songs, albums=albums)
        elif user.role == 'Creator':
            return render_template('creator_dashboard.html', songs=songs, albums=albums)
        else:
            return render_template('user_dashboard.html', songs=songs, albums=albums)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))



@app.template_filter('tojson')
def to_json_filter(obj):
    # Custom serialization method for Song objects
    if isinstance(obj, Song):
        return {
            'id': obj.id,
            'name': obj.name if obj.name is not None else "null",
            'lyrics': obj.lyrics if obj.lyrics is not None else "null",
            'duration': obj.duration if obj.duration is not None else "null",
            'artist': obj.artist  if obj.artist is not None else "null",
            'userId': obj.userId,
            # Add other attributes as needed
        }
    elif isinstance(obj, list) and all(isinstance(item, Song) for item in obj):
        return [to_json_filter(item) for item in obj]
    # Default serialization for other objects
    return dumps(obj)

@app.route('/get_playlists', methods=['GET'])
def get_playlists():
    if 'user_id' in session:
        user_id = session['user_id']
        
        # Call a service method to get the user's playlists
        playlists = PlaylistService.get_all_playlists_for_user(user_id)
        
        # Convert playlists to a format suitable for JSON response
        playlists_data = [{'id': playlist.id, 'name': playlist.name} for playlist in playlists] if playlists else []
        return jsonify({'playlists': playlists_data})
    else:
        return redirect(url_for('login'))

# Add a song to a playlist
@app.route('/add_song_to_playlist', methods=['POST'])
def add_song_to_playlist():
    if 'user_id' in session:
        user_id = session['user_id']
        playlist_id = request.form["playlist_id"]
        song_id = request.form["song_id"]
        
        # Call a service method to add the song to the playlist
        PlaylistSongService.create_association(playlist_id, song_id)
        
        # Return success message or handle as needed
        return jsonify({'message': 'Song added to playlist successfully'})
    else:
        return redirect(url_for('login'))

@app.route('/add_playlist', methods=['POST'])
def add_playlist():
    if 'user_id' in session:
        playlist_name = request.form.get('playlist_name')
        playlist_id = PlaylistService.create_playlist(playlist_name,session['user_id'])
        return jsonify({'playlistId': playlist_id})
    else:
        return redirect(url_for('login'))

@app.route('/user_playlists', methods=['GET'])
def user_playlists():
    if 'user_id' in session:
        playlists = PlaylistService.get_all_playlists_for_user(session['user_id'])
        playlistSongs = [{'name':playlist.name,'songs': [SongService.get_song_by_id(x.song_id) for x in PlaylistSongService.get_association_by_ids(playlist.id)]} for playlist in playlists]
        songs = SongService.get_all_songs()
        return render_template("user_playlists.html", playlists = playlistSongs, songs=songs)
    else:
        redirect(url_for('login'))

@app.route('/add_song', methods=['GET','POST'])
def add_song():
    if 'user_id' in session:
        songs = SongService.get_all_songs()
        return render_template('add_song.html', songs = songs)
    else:
        return render_template(url_for('index'))

@app.route('/upload_song', methods=['POST'])
def upload_song():
    if 'user_id' in session:
        name = request.form['name']
        artist = request.form['artist']
        user_id = session['user_id']
        lyrics = request.form['lyrics']
        
        if 'song' not in request.files or 'img' not in request.files:
            flash('Both song file and image file are required')
            return 'Both song file and image file are required'
        
        song_file = request.files['song']
        img_file = request.files['img']
        
        # Save the song file to a temporary location
        song_filename = secure_filename(f'{artist.replace(" ","")}-{name.replace(" ","")}.mp3')
        song_path = os.path.join(app.config['UPLOAD_FOLDER'], 'songs', song_filename)
        song_file.save(song_path)

        # Extract the duration of the song using eyed3
        audiofile = eyed3.load(song_path)
        duration_seconds = audiofile.info.time_secs if audiofile.info else None

        # Convert duration to mm:ss format
        if duration_seconds is not None:
            minutes, seconds = divmod(int(duration_seconds), 60)
            duration_formatted = f'{minutes:02d}:{seconds:02d}'
        else:
            duration_formatted = None

        # Save the image file to a temporary location
        img_filename = secure_filename(f'{name.replace(" ","")}.jpg')
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'img', img_filename)
        img_file.save(img_path)

        # Save the song details to the database
        SongService.create_song(name, lyrics, duration_formatted, artist, user_id)
        songs = SongService.get_all_songs()
        return render_template('add_song.html',songs = songs)

    else:
        return render_template(url_for('index'))

@app.route('/make_album', methods=['GET'])
def make_album():
    if 'user_id' in session:
        albums = AlbumService.get_all_albums()
        albumSongs = [{'album':album, 'songs':[SongService.get_song_by_id(x.song_id) for x in AlbumSongService.get_association_by_ids(album.id)]} for album in albums] 
        songs = SongService.get_all_songs()
        return render_template('make_album.html', songs = songs, albums = albumSongs)
    else:
        return render_template(url_for('index'))


@app.route('/upload_album', methods=['POST'])
def upload_album():
    if 'user_id' in session:
        try:
            data = request.get_json()
            name = data['name']
            artist = data['creator']

            # Assuming your service method returns the album ID
            album_id = AlbumService.create_album(name, 0, artist, session['user_id'])

            # Assuming you want to send a success message back
            response_data = {'success': True, 'message': 'Album added successfully', 'album_id': album_id}
            return jsonify(response_data), 200

        except Exception as e:
            # Handle exceptions and return an error response
            error_message = str(e)
            response_data = {'success': False, 'error': error_message}
            return jsonify(response_data), 500
    else:
        # Redirect to login or handle unauthorized access
        response_data = {'success': False, 'error': 'User not logged in'}
        return jsonify(response_data), 401

if __name__ == '__main__':
    app.run(debug=True, threaded=False)
