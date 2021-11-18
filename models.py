from flask_sqlalchemy import SQLAlchemy
#https://stackoverflow.com/questions/9692962/flask-sqlalchemy-import-context-issue/9695045#9695045
db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True)
    city = db.Column(db.String(120), nullable=True)
    state = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.String(120), nullable = True)
    website = db.Column(db.String(120), nullable = True)
    seeking_talent = db.Column(db.Boolean, nullable = True)
    seeking_description = db.Column(db.String(120), nullable = True)

    shows = db.relationship("Show", back_populates="venues")

    # TODO2: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    address =db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120), nullable = True)
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable = True)
    seeking_description = db.Column(db.String(120), nullable = True)

    shows = db.relationship("Show", back_populates="artists")

    # TODO3: implement any missing fields, as a database migration using Flask-Migrate

# TODO4 Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


'''show_table = db.Table('show_table',
    db.Column('venue_id', db.Integer, db.ForeignKey(
        'venues.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey(
        'artists.id'), primary_key=True)
)'''


class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)

  venues = db.relationship("Venue", back_populates="shows")
  artists = db.relationship("Artist", back_populates="shows")

  # on shows/create, there are three fields:
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
  # https://docs.sqlalchemy.org/en/13/core/type_basics.html
  start_time = db.Column(db.DateTime, nullable = True)