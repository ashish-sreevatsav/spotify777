from music_app_models import User, Album, Song, Playlist, PlaylistSongAssociation, AlbumSongAssociation
from sqlalchemy.orm import sessionmaker, configure_mappers
from sqlalchemy import create_engine

engine = create_engine('sqlite:///music_database.db')
Session = sessionmaker(bind=engine)
session = Session()

class UserService:

    @staticmethod
    def create_user(userName, password, role):
        user = User(userName=userName, password=password, role=role)
        session.add(user)
        session.commit()
        return user

    @staticmethod
    def get_user_by_id(user_id):
        return session.query(User).get(user_id)
    
    @staticmethod
    def get_user_by_username(username):
        return session.query(User).filter_by(userName=username).first()

    @staticmethod
    def get_all_users():
        return session.query(User).all()
    
 
    @staticmethod
    def get_all_playlists_for_user(user_id):
        return session.query(Playlist).filter_by(user_id=user_id).all()
    
    @staticmethod
    def update_user(user_id, new_data):
        user = session.query(User).get(user_id)
        if user:
            for key, value in new_data.items():
                setattr(user, key, value)
            session.commit()
        return user
    
    @staticmethod
    def delete_user(user_id):
        user = session.query(User).get(user_id)
        if user:
            session.delete(user)
            session.commit()
        return user


class SongService:

    @staticmethod
    def create_song(name, lyrics, duration, artist, userId):
        song = Song(name=name, lyrics=lyrics, duration=duration, artist=artist, userId=userId)
        session.add(song)
        session.commit()
        return song
    
    @staticmethod
    def get_song_by_id(song_id):
        return session.query(Song).get(song_id)
    
    @staticmethod
    def get_songs_by_user_id(user_id):
        return session.query(Song).filter_by(userId=user_id).all()

    @staticmethod
    def get_all_songs():
        return session.query(Song).all()

    @staticmethod
    def update_song(song_id, new_data):
        song = session.query(Song).get(song_id)
        if song:
            for key, value in new_data.items():
                setattr(song, key, value)
            session.commit()
        return song

    @staticmethod
    def delete_song(song_id):
        song = session.query(Song).get(song_id)
        if song:
            session.delete(song)
            session.commit()
        return song


class AlbumService:

    @staticmethod
    def create_album(name, total_duration, artist, userId):
        album = Album(name=name, total_duration=total_duration, artist=artist, userId=userId)
        session.add(album)
        session.commit()
        return album

    @staticmethod
    def get_album_by_id(album_id):
        return session.query(Album).get(album_id)

    @staticmethod
    def get_all_albums():
        return session.query(Album).all()

    @staticmethod
    def update_album(album_id, new_data):
        album = session.query(Album).get(album_id)
        if album:
            for key, value in new_data.items():
                setattr(album, key, value)
            session.commit()
        return album

    @staticmethod
    def delete_album(album_id):
        album = session.query(Album).get(album_id)
        if album:
            session.delete(album)
            session.commit()
        return album


class PlaylistService:

    @staticmethod
    def create_playlist(name, userId):
        playlist = Playlist(name=name, userId=userId)
        session.add(playlist)
        session.commit()
        return playlist.id

    @staticmethod
    def get_playlist_by_id(playlist_id):
        return session.query(Playlist).get(playlist_id)

    @staticmethod
    def get_all_playlists():
        return session.query(Playlist).all()

    @staticmethod
    def get_all_playlists_for_user(user_id):
        return session.query(Playlist).filter_by(userId=user_id).all()
    
    @staticmethod
    def update_playlist(playlist_id, new_data):
        playlist = session.query(Playlist).get(playlist_id)
        if playlist:
            for key, value in new_data.items():
                setattr(playlist, key, value)
            session.commit()
        return playlist

    @staticmethod
    def delete_playlist(playlist_id):
        playlist = session.query(Playlist).get(playlist_id)
        if playlist:
            session.delete(playlist)
            session.commit()
        return playlist

class PlaylistSongService:

    @staticmethod
    def create_association(playlist_id, song_id):
        association = PlaylistSongAssociation(playlist_id=playlist_id, song_id=song_id)
        session.add(association)
        session.commit()
        return association

    @staticmethod
    def get_association_by_ids(playlist_id):
        return session.query(PlaylistSongAssociation).filter_by(playlist_id=playlist_id).all()

    @staticmethod
    def get_all_associations():
        return session.query(PlaylistSongAssociation).all()

    @staticmethod
    def delete_association(playlist_id, song_id):
        association = PlaylistSongService.get_association_by_ids(playlist_id, song_id)
        if association:
            session.delete(association)
            session.commit()
        return association

class AlbumSongService:
    
    @staticmethod
    def create_association(album_id, song_id):
        association = AlbumSongAssociation(album_id=album_id, song_id=song_id)
        session.add(association)
        session.commit()
        return association

    @staticmethod
    def get_association_by_ids(album_id):
        return session.query(AlbumSongAssociation).filter_by(album_id=album_id).all()

    @staticmethod
    def get_all_associations():
        return session.query(AlbumSongAssociation).all()

    @staticmethod
    def delete_association(album_id, song_id):
        association = AlbumSongService.get_association_by_ids(album_id, song_id)
        if association:
            session.delete(association)
            session.commit()
        return association
