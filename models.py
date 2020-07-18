from app import db


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
    address = db.Column(db.String())
    city = db.Column(db.String())
    state = db.Column(db.String())
    phone = db.Column(db.String())
    website = db.Column(db.String())
    facebook_link = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(), nullable=False) 
    image_link = db.Column(db.String())
    venues = db.relationship('Artist', secondary=Show, backref=db.backref('shows', lazy='joined'))

    def __repr__(self):
        return 'venue_id:{} | venue_name: {}>'.format(self.id, self.name)
    
    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String())) 
    city = db.Column(db.String())
    state = db.Column(db.String())
    phone = db.Column(db.String())
    website = db.Column(db.String())
    facebook_link = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String()) 
    image_link = db.Column(db.String())

    def __repr__(self):
        return '<artist_id:{} | artist_name: {}>'.format(self.id, self.name)

    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

