from app import db


class Song(db.Model):
    __tablename__ = 'songs'

    song_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    anime = db.Column(db.Text)
    type = db.Column(db.Text)
    cover = db.Column(db.Text)
    video = db.Column(db.Text)
    length = db.Column(db.Integer)

    def __repr__(self):
        return f'{self.name} - {self.type} - {self.anime}'

class CurrentSong(db.Model):
    __tablename__ = "current_song"

    song_id = db.Column(db.Integer, primary_key=True)
    vote_sum = db.Column(db.Integer, default=0)
    vote_num = db.Column(db.Integer, default=0)
    start_time = db.Column(db.Float)

    def __repr__(self):
        return f'{self.song_id} - {self.vote_sum/self.vote_num} - {self.start_time}'

class Results(db.Model):
    __tablename__ = "results"

    song_id = db.Column(db.Integer, primary_key=True)
    vote_average = db.Column(db.Float, default=0)

    def __repr__(self):
        return f'{self.song_id} - {self.vote_average}'
