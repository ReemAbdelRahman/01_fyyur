#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
from models import db, Venue, Artist, Show
from flask_migrate import Migrate
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')


migrate = Migrate(app, db)

#https://stackoverflow.com/questions/9692962/flask-sqlalchemy-import-context-issue/9695045#9695045
db.init_app(app)

#https://stackoverflow.com/questions/46540664/no-application-found-either-work-inside-a-view-function-or-push-an-application
with app.app_context():
    db.create_all()

# TODO1: connect to a local postgresql database



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format = "EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format = "EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO5: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  venues = Venue.query.all()
  print(f"venues: {venues}")

  mapper = {}
  for venue in venues:
    print(venue.__dict__)
    if (venue.city, venue.state) not in mapper:
      mapper[(venue.city, venue.state)] = []
    mapper[(venue.city, venue.state)].append(
          {"id": venue.id, "name": venue.name})
  print(f"mapper:{mapper}")        
  data = []
  
  for key, value in mapper.items():
    final_map = {}
    final_map["city"] = key[0]
    final_map["state"] = key[1]
    final_map["venues"] = value
    print(f"final_map: {final_map}")
    data.append(final_map)
    print(f"data in the loop: {data}")

  print(data)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO6: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term')
  # https://stackoverflow.com/questions/42579400/search-function-query-in-flask-sqlalchemy
  venues = Venue.query.filter(Venue.name.like('%' + search_term + '%')).all()
  response ={"count":len(venues),"data":[]}
  for v in venues:
    v_dict = {"id":v.id,
              "name":v.name,
              "num_upcoming_shows": v.shows}
    response["data"].append(v_dict)

  '''response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }'''

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO7: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  print("show_venue")
  print(venue.__dict__)
  data = venue.__dict__
  upcoming_shows = db.session.query(Artist.image_link,
                                    Artist.id,
                                    Show.artist_id,
                                    Show.start_time).join(Artist,Show.artist_id== Artist.id).filter(Venue.id== venue_id,Show.start_time>datetime.now()).all()

  past_shows = db.session.query(Artist.image_link,
                                    Artist.id,
                                    Show.artist_id,
                                    Show.start_time).join(Artist,Show.artist_id== Artist.id).filter(Venue.id== venue_id,Show.start_time<datetime.now()).all()

  print(f"past shows: {past_shows}")

  data['upcoming_shows_count'] = len(upcoming_shows)
  data['past_shows_count'] = len(past_shows)

  upcoming_shows_list =[]
  past_shows_list =[]

  for show in upcoming_shows:
    #https://pythontic.com/containers/namedtuple/_asdict
    upcoming_shows_list.append(show._asdict())

  for show in past_shows:
    past_shows_list.append(show._asdict())

  data['upcoming_shows'] = upcoming_shows_list
  data['past_shows'] = past_shows_list




  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue= Venue.query.filter_by(id = venue_id)
  # TODO17: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO18: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    facebook_link = request.form.get('facebook_link')
    genres = request.form.get('genres')
    image_link = request.form.get('image_link')
    website = request.form.get('website')
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description')

    venue = Venue.query.get(venue_id)

    print(f"venue:{venue}")
    
    venue.name = name
    venue.city = city
    venue.state = state
    venue.address = address
    venue.phone = phone
    venue.facebook_link = facebook_link
    venue.genres = genres
    venue.image_link =image_link
    venue.website = website
    venue.seeking_talent = seeking_talent
    venue.seeking_description = seeking_description
    
    db.session.commit()
    flash('Venue ' + venue.id+ ' was successfully edited!')
  except Exception as e:
    print(e)
    db.session.rollback()
    flash('Venue ' + venue.id+ ' could not be edited!')
  return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO8: insert form data as a new Venue record in the db, instead
  # TODO9: modify data to be the data object returned from db insertion
  try:
    print("did i get here?")
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    facebook_link = request.form.get('facebook_link')
    genres = request.form.get('genres')
    image_link = request.form.get('image_link')
    website = request.form.get('website')
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description')

    print(name, city, facebook_link)
    venue = Venue(name = name, city = city, state = state, 
                  address =address, phone = phone, 
                  facebook_link=facebook_link, genres = genres, image_link = image_link,
                  website = website, seeking_talent = seeking_talent,
                  seeking_description = seeking_description) #image_link is does not exist in the form on venues/create
    print(f"venue: {venue}")              
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    # TODO10: on unsuccessful db insert, flash an error instead.
    print(e)
    db.session.rollback()
    error = True 
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO11: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully deleted')
  except:
    db.session.rollback()
    flash('Venue ' + request.form['name'] + ' could not be deleted')  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  artists = Artist.query.all()
  data = []
  for a in artists:
    data.append({"id":a.id,"name":a.name})

  '''data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]'''

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term')
  # https://stackoverflow.com/questions/42579400/search-function-query-in-flask-sqlalchemy
  artists = Artist.query.filter(Artist.name.like('%' + search_term + '%')).all()
  response ={"count":len(artists),"data":[]}
  for a in artists:
    a_dict = {"id":a.id,
              "name":a.name,
              "num_upcoming_shows": a.shows}
    response["data"].append(a_dict)

  '''response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }'''
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = Artist.query.get(artist_id)

  upcoming_shows = db.session.query(Show.venue_id,
                                    Venue.name,
                                    Venue.image_link,
                                    Show.start_time).join(Venue,Show.venue_id== Venue.id).filter(Artist.id== artist_id,Show.start_time>datetime.now()).all()

  past_shows = db.session.query(Show.venue_id,
                                    Venue.name,
                                    Venue.image_link,
                                    Show.start_time).join(Venue,Show.venue_id== Venue.id).filter(Artist.id== artist_id,Show.start_time<datetime.now()).all()



  data['upcoming_shows_count'] = len(upcoming_shows)
  data['past_shows_count'] = len(past_shows)

  upcoming_shows_list =[]
  past_shows_list =[]

  for show in upcoming_shows:
    upcoming_shows_list.append(show._asdict())

  for show in past_shows:
    past_shows_list.append(show._asdict())

  data['upcoming_shows'] = upcoming_shows_list
  data['past_shows'] = past_shows_list

  print(data)

  '''data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
  data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]'''
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist =  Artist.query.get(artist_id)
    '''artist={
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    }'''
  # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    try:
        edited_artist =  Artist.query.get(artist_id)

        edited_artist.name = request.form.get('name') 
        edited_artist.city = request.form.get('city') 
        edited_artist.state = request.form.get('state') 
        edited_artist.address = request.form['address'] 
        edited_artist.phone = request.form.get('phone') 
        edited_artist.genres = request.form.get('genres') 
        edited_artist.facebook_link = request.form.get('facebook_link')  
        edited_artist.image_link = request.form.get('image_link')  
        edited_artist.website = request.form.get('website') 
        edited_artist.seeking_venue = request.form.get('seeking_venue')  
        edited_artist.seeking_description = request.form.get('seeking_description') 


        db.session.commit()
        flash('Artist ' + request.form.get('name') + ' was successfully edited!')
    except:
        db.session.rollback()
        error = True 
        flash('An error occurred. Artist ' + request.form.get('name')  + ' could not be edited.')

    return redirect(url_for('show_artist', artist_id=artist_id))

#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
    try:
        print("did i get here?")
        '''name = request.form.get('name') 
        city = request.form.get('city') 
        state = request.form.get('state') 
        address = request.form.get('address')
        phone = request.form.get('phone') 
        genres = request.form.get('genres') 
        facebook_link = request.form.get('facebook_link')  
        image_link = request.form.get('image_link')  
        website = request.form.get('website') 
        seeking_venue = request.form.get('seeking_venue')  
        seeking_description = request.form.get('seeking_description')'''

        ar = Artist(
        name = request.form.get('name'), 
        city = request.form.get('city') ,
        state = request.form.get('state') ,
        address = request.form.get('address'),
        phone = request.form.get('phone'),
        genres = request.form.get('genres'),
        facebook_link = request.form.get('facebook_link'),  
        image_link = request.form.get('image_link'),  
        website = request.form.get('website'), 
        seeking_venue = request.form.get('seeking_venue'),  
        seeking_description = request.form.get('seeking_description') ) #image_link is does not exist in the form on venues/create
        print(f"ar: {ar}")              
        db.session.add(ar)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form.get('name') + ' was successfully listed!')
    except Exception as e:
        print(e)
        db.session.rollback()
        error = True   
    # TODO21: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' + request.form.get('name')  + ' could not be listed.')
    return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO22: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = Show.query.all()

  '''data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]'''
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    # called to create new shows in the db, upon submitting new show listing form
    # TODO23: insert form data as a new Show record in the db, instead
    show = Show(artist_id = request.form.get('artist_id'), 
                  venue_id = request.form.get('venue_id'),
                  start_time = request.form.get('start_time')) 
    db.session.add(show)
    db.session.commit() 
    print(f"show:{show}")             
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    error = True
    flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
