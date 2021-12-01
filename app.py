#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
                                                                              
import json
import dateutil.parser
import babel
import datetime
from flask import (
                  Flask,
                  render_template,
                  request,
                  Response,
                  flash,
                  redirect,
                  url_for,
                  abort)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from forms import *
from models import *


#----------------------------------------------------------------------------#
# App Config
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# Connect to a local postgresql database
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
      date = dateutil.parser.parse(value)
      if format == 'full':
          format = "EEEE MMMM, d, y 'at' h:mma"
      elif format == 'medium':
          format = "EE MM, dd, y h:mma"
      
      return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime        


#----------------------------------------------------------------------------#
# Controllers
#----------------------------------------------------------------------------#

@app.route('/')
def index():
      return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
      venue_data = []
      areas = db.session.query(Venue.city, Venue.state
                              ).distinct(Venue.city, Venue.state)
      try:
            for area in areas:
                  venues_in_area = db.session.query(Venue.id, 
                                    Venue.name
                                    ).filter(Venue.city == area[0]
                                    ).filter(Venue.state == area[1])
                  venue_data.append({
                        "city": area[0],
                        "state": area[1],
                        "venues": venues_in_area
                  })
      
            return render_template('pages/venues.html', 
                                   areas=venue_data)
      except Exception as e:
            print(e)
            abort(500)


@app.route('/venues/search', methods=['POST'])
def search_venues():
      try:
            search_term = request.form.get('search_term', '')
            result = db.session.query(Venue
                                    ).filter(Venue.name.ilike(f'%{search_term}%')
                                    ).all()
            count = len(result)
      
            response={
                  "count": count,
                  "data": result
            }
            
            return render_template('pages/search_venues.html', 
                              results=response, 
                              search_term=request.form.get('search_term', 
                                                            ''))
      except Exception as e:
            print(e)
            abort(404)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
      venue = Venue.query.filter(Venue.id == venue_id).first()
      past = db.session.query(Show).filter(Show.venue_id == venue_id
                                  ).filter(Show.start_time < datetime.now()
                                  ).join(Artist, Show.artist_id == Artist.id
                                  ).add_columns(Artist.id, 
                                                Artist.name,
                                                Artist.image_link,
                                                Show.start_time).all()
      upcoming = db.session.query(Show).filter(Show.venue_id == venue_id
                                      ).filter(Show.start_time > datetime.now()
      ).join(Artist, Show.artist_id == Artist.id).add_columns(Artist.id,
                                                            Artist.name,
                                                            Artist.image_link,
                                                            Show.start_time).all()
  
      past_shows = []
      upcoming_shows = []
      
      for p in past:
            past_shows.append({
                  'artist_id': p[1],
                  'artist_name': p[2],
                  'image_link': p[3],
                  'start_time': str(p[4])
            })
            
      for u in upcoming:
            upcoming_shows.append({
                  'artist_id': u[1],
                  'artist_name': u[2], 
                  'image_link': u[3],
                  'start_time': str(u[4])
            })
          
      if venue is None:
            abort(404)   
            
      response={
            "id": venue.id,
            "name": venue.name,
            "genres": [venue.genres],
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past),
            "upcoming_shows_count": len(upcoming),
      }
      
      return render_template('pages/show_venue.html', venue=response)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
      form = VenueForm()
      return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
      # Inserting form data as a new Venue record in the db
      form = VenueForm(request.form)
      try:
        venue = Venue(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            address=request.form['address'],
            phone=request.form['phone'],
            genres=request.form.getlist('genres'),
            image_link=request.form['image_link'],
            facebook_link=request.form['facebook_link'],
            website=request.form['website'],
            seeking_talent=json.loads(request.form['seeking_talent'].lower()),
            seeking_description=request.form['seeking_description']
            )
        form.populate_obj(venue)
        db.session.add(venue)
        db.session.commit()
        # On successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully added.')
        # On unsuccessful db insert, flash an error instead
      except Exception as e:
            db.session.rollback()
            print(e)
            flash('An error occured. Venue ' + request.form['name'] + ' could not be added.')
            abort(500)
      finally:
            db.session.close()
      
      return render_template('pages/home.html')


#  Update Venue
#  ----------------------------------------------------------------

@app.route('/venues/<venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
      form = VenueForm()
      venue = {
            "id": 1,
            "name": "The Musical Hop",
            "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
            "address": "1015 Folsom St",
            "city": "San Francisco", 
            "state": "CA",
            "phone": "123-123-1234",
            "website": "https://www.themusicalhop.com",
            "facebook_link": "https://www.facebook.com/TheMusicalHop",
            "seeking_talent": True,
            "seeking_description": "We are looking for an artist to work with us or regular basis",
            "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60" 
            }
      
      return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
      return redirect(url_for('show_venue', venue_id=venue_id))
    

#  Delete Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
      try:
            Venue.query.filter(Venue.id == venue_id).delete()
            db.session.commit()
      except Exception as e:
            print(e)
            db.session.rollback()
            abort(422)
      finally:
            db.session.close()
      
      return render_template('pages/home.html')
  

#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
      # Queryng for artists
      try:
            response = Artist.query.all()
            return render_template('pages/artists.html', artists=response)
      except Exception as e:
            print(e)
            abort(500)


@app.route('/artists/search', methods=['POST'])
def search_artists():
      try:
            search_term = request.form.get('search_term', '')
            result = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
            count = len(result)  
            
            response={
            "count": count,
            "data": result
            }
      
            return render_template('pages/search_artists.html', results=response, search_term=search_term)
      except Exception as e:
            print(e)
            abort(404)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
      artist = Artist.query.filter(Artist.id == artist_id).first()
      
      past = db.session.query(Show).filter(Show.artist_id == artist_id
                                  ).filter(Show.start_time < datetime.now()
                                  ).join(Venue, Show.venue_id == Venue.id).add_columns(Venue.id,
                                                                                      Venue.name,
                                                                                      Venue.image_link,
                                                                                      Show.start_time).all()     
      upcoming = db.session.query(Show).filter(Show.artist_id == artist_id
                                      ).filter(Show.start_time > datetime.now()
                                      ).join(Venue, Show.venue_id == Venue.id).add_columns(Venue.id,
                                                                                           Venue.name,
                                                                                           Venue.image_link,
                                                                                           Show.start_time).all()
      past_shows = []
      upcoming_shows = []
      
      for p in past:
            past_shows.append({
                  'venue_id': p[1],
                  'venue_name': p[2],
                  'image_link': p[3],
                  'start_time': str(p[4])
                  })
            
      for u in upcoming:
            upcoming_shows.append({
                  'venue_id': u[1],
                  'venue_name': u[2],
                  'image_link': u[3],
                  'start_time': str(u[4])
                  })
      
      if artist is None:
            abort(404)
      
      response = {
            "id": artist.id,
            "name": artist.name,
            "genres": [artist.genres],
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description":  artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past_shows,
            "past_shows_count": len(past),
            "upcoming_shows": upcoming_shows,
            "upcoming_shows_count": len(upcoming)
            }
  
      return render_template('pages/show_artist.html', artist=response)


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
      form = ArtistForm()
      return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
      # Inserting form data as a new Venue record in the db
      form = ArtistForm(request.form)
      try:
            artist = Artist(
                  name=request.form['name'],
                  city=request.form['city'],
                  state=request.form['state'],
                  phone=request.form['phone'],
                  image_link=request.form['image_link'],
                  genres=request.form.getlist('genres'),
                  facebook_link=request.form['facebook_link'],
                  website=request.form['website'],
                  seeking_venue=json.loads(request.form['seeking_venue'].lower()),
                  seeking_description=request.form['seeking_description']
                  )
            form.populate_obj(artist)
            db.session.add(artist)
            db.session.commit()
            # On successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully added.')
            # On unsuccessful db insert, flash an error instead
      except Exception as e:
            db.session.rollback()
            print(e)
            flash('An error occured. Artist ' + request.form['name'] + ' could not be added.')
            abort(500)
        
      finally:
            db.session.close()
      
      return render_template('pages/home.html')


#  Update Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
      form = ArtistForm()
      artist = Artist.query.filter(Artist.id == artist_id).first()
      return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
      return redirect(url_for('show_artist', artist_id=artist_id))


#  Delete Artist
#  ----------------------------------------------------------------

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
      try:
        Artist.query.filter(Artist.id == artist_id).delete()
        db.session.commit()
      except Exception as e:
            print(e)
            db.session.rollback()
            abort(422)
      finally:
            db.session.close()
      return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
      # Displaying a list of shows at /shows
      show_data = db.session.query(Show).join(Venue).join(Artist).all()

      response = []
      
      try:
            for show in show_data:
                  response.append({
                  "venue_id": show.venues.id,
                  "venue_name": show.venues.name,
                  "artist_id": show.artists.id,
                  "artist_name": show.artists.name,
                  "artist_image_link": show.artists.image_link,
                  "start_time": str(show.start_time)
                  })
      
            return render_template('pages/shows.html', shows=response)
      except Exception as e:
            print(e)
            abort(500)


#  Create Show
#  ----------------------------------------------------------------
@app.route('/shows/create')
def create_shows():
      # Renders form
      form = ShowForm()
      return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
      form = ShowForm(request.form)
      # Called to create new shows in the db, upon submitting new show listing form
      # # Inserting form data as a new Show record in the db
      try:
            show = Show(
                  artist_id=form.artist_id.data,
                  venue_id=form.venue_id.data,
                  start_time=form.start_time.data
      )
            form.populate_obj(show)
            db.session.add(show)
            db.session.commit()
            # On successful db insert, flash success
            flash('Show was successfully added.')
      # On unsuccessful db insert, flash an error instead
      except Exception as e:
            db.session.rollback()
            print(e)
            flash('An error occured. Show could not be added.')
            abort(500)
      finally:
            db.session.close()
      
      return render_template('pages/home.html')


@app.errorhandler(400)
def bad_request(error):
      return render_template('errors/400.html'), 400

@app.errorhandler(404)
def not_found(error):
      return render_template('errors/404.html'), 404

@app.errorhandler(422)
def unprocessable(error):
      return render_template('errors/422.html'), 422

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
# Launch
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
