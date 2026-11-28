from flask import render_template, request, session, redirect, url_for
from models import Song, CurrentSong, Results
import time


def register_routes(app, db):

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == "POST" and not session.get("user_voted", False):
            vote_value = request.form.get("vote_result")
            CurrentSong.query.with_for_update().first().vote_sum += int(vote_value)
            CurrentSong.query.with_for_update().first().vote_num += 1
            db.session.commit()

            session["user_voted"] = True

            return redirect(url_for("index"))

        current_song = CurrentSong.query.first()
        if current_song:
            song = Song.query.get(CurrentSong.query.first().song_id)
        else:
            song = False

        return render_template('index.html', song=song, user_voted=session.get("user_voted", False))

    @app.route('/check_timer')
    def check_timer():
        song = Song.query.get(CurrentSong.query.first().song_id)
        finished = False

        if song == None:
            song = Song.query.get(1)
            finished = True

        start_time = CurrentSong.query.first().start_time
        time_remaining = song.length - time.time() + start_time
        available =  0 < time_remaining <= 30

        if not available:
            session["user_voted"] = False

        if time_remaining <= -5:
            if not finished:
                current_song = CurrentSong.query.first()
                if Results.query.get(current_song.song_id) == None:
                    db.session.add(Results(song_id=current_song.song_id, vote_average=current_song.vote_sum/max(current_song.vote_num, 1)))
                else:
                    Results.query.with_for_update().get(current_song.song_id).vote_average = current_song.vote_sum/max(current_song.vote_num, 1)
                CurrentSong.query.with_for_update().first().vote_sum = 0
                CurrentSong.query.with_for_update().first().vote_num = 0

            CurrentSong.query.with_for_update().first().start_time = time.time()
            CurrentSong.query.with_for_update().first().song_id += 1
            db.session.commit()

        playing_song_data = {"song_cover": song.cover, "song_name": song.name, "song_type": song.type, "song_anime": song.anime}

        top_songs_db = Results.query.order_by(Results.vote_average.desc()).limit(3).all()
        top_songs = []
        for i in range(3):
            if len(top_songs_db) > i:
                s = Song.query.get(top_songs_db[i].song_id)
                if not s == None:
                    score = round(Results.query.get(s.song_id).vote_average * 10)
                    top_songs.append({"song_cover": s.cover, "song_score": f"static/ranks/{score}.png", "song_name": s.name, "song_type": s.type, "song_anime": s.anime})
                else:
                    top_songs.append({"song_cover": "static/ranks/NA.png", "song_score": "static/ranks/NA.png", "song_name": "NA", "song_type": "NA", "song_anime": "NA"})
            else:
                top_songs.append({"song_cover": "static/ranks/NA.png", "song_score": "static/ranks/NA.png", "song_name": "NA", "song_type": "NA", "song_anime": "NA"})

        recent_songs_db = Results.query.order_by(Results.song_id.desc()).limit(3).all()
        recent_songs = []
        for i in range(3):
            if len(recent_songs_db) > i:
                s = Song.query.get(recent_songs_db[i].song_id)
                if not s == None:
                    score = round(Results.query.get(s.song_id).vote_average * 10)
                    recent_songs.append({"song_cover": s.cover, "song_score": f"static/ranks/{score}.png", "song_name": s.name, "song_type": s.type, "song_anime": s.anime})
                else:
                    recent_songs.append({"song_cover": "static/ranks/NA.png", "song_score": "static/ranks/NA.png", "song_name": "NA", "song_type": "NA", "song_anime": "NA"})
            else:
                recent_songs.append({"song_cover": "static/ranks/NA.png", "song_score": "static/ranks/NA.png", "song_name": "NA", "song_type": "NA", "song_anime": "NA"})

        return {"available": available, "voted": session.get('user_voted', False), "finished": finished, "current": playing_song_data, "top": top_songs, "recent": recent_songs}

    @app.route('/host', methods=['GET', 'POST'])
    def host():
        if request.method == "POST":
            if request.form.get("password") == "anthony":
                CurrentSong.query.with_for_update().first().song_id = 1
                Results.query.delete()
                db.session.commit()
        return render_template('host.html')

    @app.route('/obs_data')
    def get_obs_data():
        current_song = CurrentSong.query.first()
        song = Song.query.get(current_song.song_id)

        if song == None:
            song = Song.query.get(1)

        start_time = current_song.start_time
        time_remaining = song.length - time.time() + start_time
        playing =  time_remaining > 0

        if time_remaining > 0:
            video = song.video
            cover = song.cover
            song_name = song.name
            anime = song.anime
            type = song.type
        else:
            next_song = Song.query.get(current_song.song_id + 1)
            if next_song == None:
                next_song = Song.query.get(1)
            video = next_song.video
            cover = next_song.cover
            song_name = next_song.name
            anime = next_song.anime
            type = next_song.type

        score = round((current_song.vote_sum/max(1, current_song.vote_num))*10)
        rank = f"static/ranks/{score}.png"

        return {"playing": playing, "video": video, "cover": cover, "rank": rank, "song_name": song_name, "anime": anime, "type": type}

    @app.route('/results_data')
    def get_results():
        results = Results.query.all()
        data = {}
        for row in results:
            data[row.song_id] = row.vote_average
        return data