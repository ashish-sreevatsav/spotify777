from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    userName = Column(String(255))
    password = Column(String(255))
    role = Column(String(20))
    songs = relationship('Song', backref='user', lazy=True)
    albums = relationship('Album', backref='user', lazy=True)
    playlists = relationship('Playlist', backref='user', lazy=True)

class Song(Base):
    __tablename__ = 'song'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    lyrics = Column(Text)
    duration = Column(Integer)
    artist = Column(String(255))
    userId = Column(Integer, ForeignKey('user.id'), nullable=False)

    albums = relationship('Album', secondary='album_song_association', back_populates='songs', overlaps="albums")
    playlists = relationship('Playlist', secondary='playlist_song_association', back_populates='songs', overlaps="playlists")

class Album(Base):
    __tablename__ = 'album'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    total_duration = Column(Integer)
    artist = Column(String(255))
    userId = Column(Integer, ForeignKey('user.id'), nullable=False)
    songs = relationship('Song', secondary='album_song_association', back_populates='albums')

class Playlist(Base):
    __tablename__ = 'playlist'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    userId = Column(Integer, ForeignKey('user.id'), nullable=False)
    songs = relationship('Song', secondary='playlist_song_association')


# Define the Album-Song Association model
class AlbumSongAssociation(Base):
    __tablename__ = 'album_song_association'

    album_id = Column(Integer, ForeignKey('album.id'), primary_key=True)
    song_id = Column(Integer, ForeignKey('song.id'), primary_key=True)

# Explicitly set the back_populates without using overlaps
    album = relationship('Album')
    song = relationship('Song')


# Define the Playlist-Song Association model
class PlaylistSongAssociation(Base):
    __tablename__ = 'playlist_song_association'

    playlist_id = Column(Integer, ForeignKey('playlist.id'), primary_key=True)
    song_id = Column(Integer, ForeignKey('song.id'), primary_key=True)
    playlist = relationship('Playlist')
    song = relationship('Song')