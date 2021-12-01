#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import dateutil.parser


db = SQLAlchemy()


#----------------------------------------------------------------------------#
# Models
#----------------------------------------------------------------------------#

class Venue(db.Model):
      __tablename__ = 'venues'

      id = db.Column(db.Integer, primary_key=True)
      name = db.Column(db.String)
      city = db.Column(db.String(120))
      state = db.Column(db.String(120))
      address = db.Column(db.String(120))
      phone = db.Column(db.String(120))
      genres = db.Column(db.String(120))
      image_link = db.Column(db.String(500))
      facebook_link = db.Column(db.String(120))
      website = db.Column(db.String(120))
      seeking_talent = db.Column(db.Boolean, default=False)
      seeking_description = db.Column(db.String(300))
      shows = db.relationship('Show', 
                              backref='venues', 
                              lazy='dynamic', 
                              passive_deletes=True)
      
      def __repr__(self):
            return f'<Venue {self.id} {self.name}>'
          

class Artist(db.Model):
      __tablename__ = 'artists'

      id = db.Column(db.Integer, primary_key=True)
      name = db.Column(db.String)
      city = db.Column(db.String(120))
      state = db.Column(db.String(120))
      phone = db.Column(db.String(120))
      genres = db.Column(db.String(120))
      image_link = db.Column(db.String(500))
      facebook_link = db.Column(db.String(120))
      website = db.Column(db.String(120))
      seeking_venue = db.Column(db.Boolean, default=False)
      seeking_description = db.Column(db.String(300))
      shows = db.relationship('Show', 
                              backref='artists', 
                              lazy=True, 
                              passive_deletes=True)
      
      def __repr__(self):
            return f'<Artist {self.id} {self.name}>'
   
        
class Show(db.Model):
      __tablename__ = 'shows'
      
      id = db.Column(db.Integer, primary_key=True)
      start_time = db.Column(db.DateTime, 
                             default=datetime.utcnow(), 
                             nullable=False)
      artist_id = db.Column(db.Integer, 
                            db.ForeignKey('artists.id', 
                                          ondelete='CASCADE'), 
                            nullable=False)
      venue_id = db.Column(db.Integer, 
                           db.ForeignKey('venues.id', 
                                         ondelete='CASCADE'), 
                           nullable=False)
      
      def __repr__(self):
            return f'<Show {self.id} {self.artist_id} {self.venue_id} {self.start_time}>'
