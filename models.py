from app import db

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
Show = db.Table('Show', db.Model.metadata,
    db.Column('Venue_id', db.Integer, db.ForeignKey('Venue.id')),
    db.Column('Artist_id', db.Integer, db.ForeignKey('Artist.id')),
    db.Column('start_time', db.DateTime)
)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String())) 
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(255))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500)) 
    image_link = db.Column(db.String(500))
    venues = db.relationship('Artist', secondary=Show, backref=db.backref('shows', lazy='joined'))
   
    def __repr__(self):
        return 'venue_id:{} | venue_name: {}>'.format(self.id, self.name)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String())) # To store multiple Genres, I decided to create an Array Column with String as Datatype
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(255))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500)) # Because descriptions can be a little bit longer, I decided to accept input up to 500 characters
    image_link = db.Column(db.String(500))
    
    def __repr__(self):
        return '<artist_id:{} | artist_name: {}>'.format(self.id, self.name)

