from flask import render_template, request, Response, flash, redirect, url_for, jsonify
from flask import current_app as app
from models import db, Venue, Artist, Show
from sqlalchemy import func, inspect
import dateutil.parser
from datetime import datetime
from forms import *
import babel


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(str(value))
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
    db.create_all()
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  for i in (db.session.query(Venue.city,Venue.state).group_by(Venue.city,Venue.state)):
      i_dict = i._asdict()  
      data.append(i_dict)

  for area in data:
    area['venues'] = [ven.__dict__ for ven in Venue.query.filter_by(city = area['city']).all()]
    for ven in area['venues']:
      ven['num_shows'] = db.session.query(func.count(Show.c.Venue_id)).filter(Show.c.Venue_id == ven['id']).filter(Show.c.start_time > datetime.now()).all()[0][0]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  query=request.form.get('search_term', '') 

  count = (db.session.query(
    func.count(Venue.id))
    .filter(Venue.name.contains(query))
    .all())

  result = Venue.query.filter(Venue.name.contains(query)).all()

  response={
    "count": count[0][0],
    "data": result
  }

  return render_template('pages/search_venues.html', results=response, search_term=query)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)

  venue.past_shows = (db.session.query(
    Artist.id.label("artist_id"), 
    Artist.name.label("artist_name"), 
    Artist.image_link.label("artist_image_link"), 
    Show)
    .filter(Show.c.Venue_id == venue_id)
    .filter(Show.c.Artist_id == Artist.id)
    .filter(Show.c.start_time <= datetime.now())
    .all())
  
  venue.upcoming_shows = (db.session.query(
    Artist.id.label("artist_id"), 
    Artist.name.label("artist_name"), 
    Artist.image_link.label("artist_image_link"), 
    Show)
    .filter(Show.c.Venue_id == venue_id)
    .filter(Show.c.Artist_id == Artist.id)
    .filter(Show.c.start_time > datetime.now())
    .all())

  venue.past_shows_count = (db.session.query(
    func.count(Show.c.Venue_id))
    .filter(Show.c.Venue_id == venue_id)
    .filter(Show.c.start_time < datetime.now())
    .all())[0][0]

  venue.upcoming_shows_count = (db.session.query(
    func.count(Show.c.Venue_id))
    .filter(Show.c.Venue_id == venue_id)
    .filter(Show.c.start_time > datetime.now())
    .all())[0][0]

  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form) 
  flashType = 'danger' 
  if form.validate():
    try:
      newVenue = Venue()
      newVenue.name = request.form['name']
      newVenue.genres = request.form.getlist('genres')
      newVenue.address = request.form['address']
      newVenue.city = request.form['city']
      newVenue.state = request.form['state']
      newVenue.phone = request.form['phone']
      newVenue.website = request.form['website']
      newVenue.facebook_link = request.form['facebook_link']
      newVenue.seeking_talent = (True if request.form['seeking_talent'] == 'y' else False)
      newVenue.seeking_description = request.form['seeking_description']
      newVenue.image_link = request.form['image_link']
      newVenue.insert()
      flashType = 'success'
      flash('Venue {} was successfully listed!'.format(newVenue.name))
    except: 
      flash('Error in DB insertion. {} could not be listed.'.format(request.form['name']))
    finally:
      db.session.close()
  else:
    flash(form.errors)
    flash('Error in Form validation. {} could not be listed.'.format(request.form['name']))
  
  return render_template('pages/home.html', flashType = flashType)

#  Update Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form) 
  flashType = 'danger' 
  if form.validate():
    try:
      venue = Venue.query.get(venue_id)
      venue.name = request.form['name']
      venue.genres = request.form.getlist('genres')
      venue.address = request.form['address']
      venue.city = request.form['city']
      venue.state = request.form['state']
      venue.phone = request.form['phone']
      venue.website = request.form['website']
      venue.facebook_link = request.form['facebook_link']
      venue.seeking_talent = (True if request.form['seeking_talent'] == 'y' else False)
      venue.seeking_description = request.form['seeking_description']
      venue.image_link = request.form['image_link']
      venue.update()
      flashType = 'success'
      flash('Venue {} was successfully updated!'.format(venue.name))
    except: 
      flash('Error in DB change. {} could not be listed.'.format(request.form['name']))
    finally:
      db.session.close()
  else:
    flash(form.errors)
    flash('Error in Form validation. {} could not be listed.'.format(request.form['name']))
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Delete Venue
#  ----------------------------------------------------------------

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
    flash('This will alert User that Venue could not be deleted because they are still Shows attached') 
    return render_template('pages/home.html')
  finally:
    db.session.close()
  flash('Venue was successfully deleted!')
  return render_template('pages/home.html')
  

#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  query=request.form.get('search_term', '')

  count = db.session.query(func.count(Artist.id)).filter(Artist.name.contains(query)).all()
  
  result = Artist.query.filter(Artist.name.contains(query)).all()
  
  response={
    "count": count[0][0],
    "data": result
  }
  return render_template('pages/search_artists.html', results=response, search_term=query)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)

  artist.past_shows = (db.session.query(
    Venue.id.label("venue_id"), 
    Venue.name.label("venue_name"), 
    Venue.image_link.label("venue_image_link"), 
    Show)
    .filter(Show.c.Artist_id == artist_id)
    .filter(Show.c.Venue_id == Venue.id)
    .filter(Show.c.start_time <= datetime.now())
    .all())
  
  artist.upcoming_shows = (db.session.query(
    Venue.id.label("venue_id"), 
    Venue.name.label("venue_name"), 
    Venue.image_link.label("venue_image_link"), 
    Show)
    .filter(Show.c.Artist_id == artist_id)
    .filter(Show.c.Venue_id == Venue.id)
    .filter(Show.c.start_time > datetime.now())
    .all())

  artist.past_shows_count = (db.session.query(
    func.count(Show.c.Artist_id))
    .filter(Show.c.Artist_id == artist_id)
    .filter(Show.c.start_time < datetime.now())
    .all())[0][0]
  
  artist.upcoming_shows_count = (db.session.query(
    func.count(Show.c.Artist_id))
    .filter(Show.c.Artist_id == artist_id)
    .filter(Show.c.start_time > datetime.now())
    .all())[0][0]

  return render_template('pages/show_artist.html', artist=artist)

#  Update Artist
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form) 
  flashType = 'danger' 
  if form.validate():
    try:
      artist = Artist.query.get(venue_id)
      artist.name = request.form['name']
      artist.genres = request.form.getlist('genres')
      artist.city = request.form['city']
      artist.state = request.form['state']
      artist.phone = request.form['phone']
      artist.website = request.form['website']
      artist.facebook_link = request.form['facebook_link']
      artist.seeking_venue = (True if request.form['seeking_venue'] == 'y' else False)
      artist.seeking_description = request.form['seeking_description']
      artist.image_link = request.form['image_link']
      artist.update()
      flashType = 'success'
      flash('Aritst {} was successfully updated!'.format(artist.name))
    except: 
      flash('Error in DB change. {} could not be listed.'.format(request.form['name']))
    finally:
      db.session.close()
  else:
    flash(form.errors)
    flash('Error in Form validation. {} could not be listed.'.format(request.form['name']))
  return redirect(url_for('show_artist', artist_id=artist_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form) 
  flashType = 'danger' 
  if form.validate():
    try:
      newArtist = Artist()
      newArtist.name = request.form['name']
      newArtist.genres = request.form.getlist('genres')
      newArtist.city = request.form['city']
      newArtist.state = request.form['state']
      newArtist.phone = request.form['phone']
      newArtist.website = request.form['website']
      newArtist.facebook_link = request.form['facebook_link']
      newArtist.seeking_venue = (True if request.form['seeking_venue'] == 'y' else False)
      newArtist.seeking_description = request.form['seeking_description']
      newArtist.image_link = request.form['image_link']
      newArtist.insert()
      flashType = 'success'
      flash('Artist {} was successfully listed!'.format(newArtist.name))
    except:
      flash('Error in DB insertion. {} could not be listed.'.format(request.form['name']))
    finally:
      db.session.close()
  else:
    flash(form.errors)
    flash('Error in Form validation. {} could not be listed.'.format(request.form['name']))
  
  return render_template('pages/home.html', flashType = flashType)


#  Delete Venue
#  ----------------------------------------------------------------

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  try:
    Artist.query.filter_by(id=artist_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
    flash('This will alert User that Artist could not be deleted because they are still Shows attached') 
    return render_template('pages/home.html')
  finally:
    db.session.close()
  flash('Artist was successfully deleted!')
  return render_template('pages/home.html')
 


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = (db.session.query(
    Venue.id.label("venue_id"), 
    Venue.name.label("venue_name"),
    Artist.id.label("artist_id"), 
    Artist.name.label("artist_name"), 
    Artist.image_link.label("artist_image_link"), 
    Show)
    .filter(Show.c.Venue_id == Venue.id)
    .filter(Show.c.Artist_id == Artist.id)
    .all())
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form) 
  flashType = 'danger' 
  if form.validate():
    try:
      newShow = Show.insert().values(
        Venue_id = request.form['venue_id'],
        Artist_id = request.form['artist_id'],
        start_time = request.form['start_time']
      )
      db.session.execute(newShow) 
      db.session.commit()
      flashType = 'success'
      flash('Show was successfully listed!')
    except:
      flash('Error in DB insertion')
    finally:
      db.session.close()
  else:
    flash(form.errors)
    flash('Error in Form validation')
  
  return render_template('pages/home.html', flashType = flashType)

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