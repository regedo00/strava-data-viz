from app import db


class Access(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    client_id = db.Column(db.String(120), index=True)
    client_secret = db.Column(db.String(128))
    refresh_token = db.Column(db.String(128))

    def __repr__(self):
        return "<User {}>".format(self.name)


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

    def __repr__(self):
        return "<Activity {} {}>".format(self.name, self.type)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "distance": self.distance,
            "type": self.type,
            "start_date": self.start_date,
            "average_speed": self.average_speed,
        }
