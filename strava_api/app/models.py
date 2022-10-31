from app import db


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    distance = db.Column(db.Float)
    moving_time = db.Column(db.Float)
    elapsed_time = db.Column(db.Float)
    total_elevation_gain = db.Column(db.Float)
    type = db.Column(db.String(100))
    sport_type = db.Column(db.String(100))
    start_date = db.Column(db.DateTime)
    average_speed = db.Column(db.Float)
    max_speed = db.Column(db.Float)
    strava_id = db.Column(db.Integer)

    def __repr__(self):
        return "<Activity {} {}>".format(self.name, self.type)
