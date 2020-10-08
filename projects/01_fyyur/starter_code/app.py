#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Artist, Venue, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []

  cities = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)

  for city in cities:
    venues_in_a_city = db.session.query(Venue.id, Venue.name).filter(Venue.city == city[0]).filter(Venue.state == city[1])
    data.append({
      "city": city[0],
      "state": city[1],
      "venues": venues_in_a_city
    })
  
  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  # Store search terms in a variable
  search_term = request.form.get('search_term', '')
  
  # Use ILIKE for pattern matching to create a query to filter the db. Hold the output in a variable
  results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  # Return the response inc. calculated search result length
  response={
      "count": len(results),
      "data": [{
        "id": Venue.id,
        "name": Venue.name,
      } for Venue in results]
    }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  # Create variables to hold query data from Venue and Show tables
  venue = db.session.query(Venue).filter(Venue.id == venue_id).one()
  shows = db.session.query(Show).filter(Show.venue_id == venue_id)
  
  # Create arrays to hold show data
  past_shows = []
  future_shows = []

  # Iterate through artists to find shows that match the venue
  for show in shows:
    artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).one()
    data = {
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(str(show.datetime))
    }
    if show.datetime > datetime.now():
      future_shows.append(data)
    else:
      past_shows.append(data)

  # Map data to a data object
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "past_shows_count": len(past_shows),
    "future_shows": future_shows,
    "future_shows_count": len(future_shows)
  }  
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # Crate a form variable for ease
  form = VenueForm(request.form)

  # Create a new Venue object in the db, mapping form data to the relevant Columns
  venue = Venue(
    name = form.name.data,
    genres = form.genres.data,
    address = form.address.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    website = form.website.data,
    facebook_link = form.facebook_link.data,
    seeking_talent = form.seeking_talent.data,
    seeking_description = form.seeking_description.data,
    image_link = form.image_link.data
  )
  try:
    db.session.add(venue)
    db.session.commit()
    # On successful db insert, flash success
    flash('Venue was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    # On unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue could not be added.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:
      venue = Venue.query.get(venue_id)
      venue_name = venue.name

      db.session.delete(venue)
      db.session.commit()

      flash('Venue ' + venue_name + ' was deleted')
  except:
    db.session.rollback()
    flash('an error occured and Venue ' + venue_name + ' was not deleted')
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  # Empty array for our data
  data = []

  # Grab all artists from db
  artists = Artist.query.all()

  # Append data from our list of artists to individual instances of the artist object
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  # Store search terms in a variable
  search_term = request.form.get('search_term', '')
  
  # Use ILIKE for pattern matching to create a query to filter the db. Hold the output in a variable
  results = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  # Return the response inc. calculated search result length
  response={
      "count": len(results),
      "data": [{
        "id": Artist.id,
        "name": Artist.name,
      } for Artist in results]
    }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  artist = db.session.query(Artist).filter(Artist.id == artist_id).one()
  shows = db.session.query(Show).filter(Show.artist_id == artist_id)
  
  # Create arrays to hold show data
  past_shows = []
  future_shows = []

  # Iterate through artists to find shows that match the venue
  for show in shows:
    venue = db.session.query(Venue.name, Venue.image_link).filter(Venue.id == show.venue_id).one()
    data = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": format_datetime(str(show.datetime))
    }
    if show.datetime > datetime.now():
      future_shows.append(data)
    else:
      past_shows.append(data)

  # Map data to a data object
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venues": artist.seeking_venues,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "past_shows_count": len(past_shows),
    "future_shows": future_shows,
    "future_shows_count": len(future_shows)
  }  

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  artist = Artist.query.get(artist_id)

  artist_data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "facebook_link": artist.facebook_link,
        "image_link": artist.image_link
    }  

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm(request.form)
  artist = db.session.query(Artist).filter(Artist.id == artist_id).one()

  edited_artist = {
    "name": form.name.data,
    "genres": form.genres.data,
    "address": form.address.data,
    "city": form.city.data,
    "state": form.state.data,
    "phone": form.phone.data,
    "website": form.website.data,
    "facebook_link": form.facebook_link.data,
    "seeking_venues": form.seeking_venues.data,
    "seeking_description": form.seeking_description.data,
    "image_link": form.image_link.data
  }

  try:
    db.session.query(Artist).filter(Artist.id == artist_id).update(edited_artist)
    db.session.commit()
    flash('Artist ' + form.name.data + 'was successfully listed.')
  except:
    flash('An error occurred. Artist could not be added.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  
  venue = db.session.query(Venue).filter(Venue.id == venue_id).one()

  edited_venue={
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "image_link": venue.image_link
  }  

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  form = VenueForm()
  venue = db.session.query(Venue).filter(Venue.id == venue_id).one()

  edited_venue={
    "name": form.name.data,
    "genres": form.genres.data,
    "address": form.address.data,
    "city": form.city.data,
    "state": form.state.data,
    "phone": form.phone.data,
    "website": form.website.data,
    "facebook_link": form.facebook_link.data,
    "seeking_talent": form.seeking_talent.data,
    "image_link": form.image_link.data
  } 

  try:
    db.session.commit()
    flash('Venue ' + form.name.data + 'was successfully listed.')
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

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

  form = ArtistForm(request.form)

  artist = Artist(
    name = form.name.data,
    city = form.city.data,
    state = form.city.data,
    phone = form.phone.data,
    genres = form.genres.data,
    image_link = form.image_link.data, 
    facebook_link=form.facebook_link.data
    )

  try:
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  shows = Show.query.order_by(db.desc(Show.datetime))
  
  data = []

  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(str(show.datetime))
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  try:
    show = Show(
    artist_id = request.form['artist_id'],
    venue_id = request.form['venue_id'],
    datetime = request.form['start_time']
    )

    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed.')
  except expression as identifier:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
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
