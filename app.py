# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# COMPLETED: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

venue_genres = db.Table('Venue_Genres',
                        db.Column('venue_id',
                                  db.Integer,
                                  db.ForeignKey('Venue.id'),
                                  primary_key=True),
                        db.Column('genre_id',
                                  db.Integer,
                                  db.ForeignKey('Genre.id'),
                                  primary_key=True))

artist_genres = db.Table('Artist_Genres',
                         db.Column('artist_id',
                                   db.Integer,
                                   db.ForeignKey('Artist.id'),
                                   primary_key=True),
                         db.Column('genre_id',
                                   db.Integer,
                                   db.ForeignKey('Genre.id'),
                                   primary_key=True))


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    # Relationships
    address_id = db.Column(db.Integer,
                           db.ForeignKey('Address.id'),
                           nullable=False)
    seeking_talent = db.relationship("Talent_Seeking",
                                     uselist=False,
                                     backref=db.backref("venue"),
                                     cascade='all, delete-orphan',
                                     passive_deletes=True)
    genres = db.relationship('Genre',
                             secondary=venue_genres,
                             backref=db.backref('venues'))
    shows = db.relationship('Show',
                            backref='venue',
                            cascade='all, delete-orphan',
                            passive_deletes=True)
    # COMPLETED: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    # Relationships
    city_id = db.Column(db.Integer,
                        db.ForeignKey('City.id'),
                        nullable=False)
    seeking_venue = db.relationship("Venue_Seeking",
                                    uselist=False,
                                    backref=db.backref("artist"),
                                    cascade='all, delete-orphan',
                                    passive_deletes=True)
    genres = db.relationship('Genre',
                             secondary=artist_genres,
                             backref=db.backref('artists'))
    shows = db.relationship('Show',
                            backref='artist',
                            cascade='all, delete-orphan', passive_deletes=True)


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime())
    # Relationships
    venue_id = db.Column(db.Integer,
                         db.ForeignKey('Venue.id', ondelete="cascade"),
                         nullable=True)
    artist_id = db.Column(db.Integer,
                          db.ForeignKey('Artist.id', ondelete="cascade"),
                          nullable=True)


class Talent_Seeking(db.Model):
    __tablename__ = 'Talent_Seeking'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)

    venue_id = db.Column(db.Integer,
                         db.ForeignKey('Venue.id', ondelete="cascade"),
                         nullable=False)


class Venue_Seeking(db.Model):
    __tablename__ = 'Venue_Seeking'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    artist_id = db.Column(db.Integer,
                          db.ForeignKey('Artist.id', ondelete='cascade'),
                          nullable=False)


class Genre(db.Model):
    __tablename__ = 'Genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, index=True)


class Address(db.Model):
    __tablename__ = 'Address'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    # Relationships
    city_id = db.Column(db.Integer,
                        db.ForeignKey('City.id', ondelete='cascade'),
                        nullable=False)
    venues = db.relationship('Venue', backref='address')


class City(db.Model):
    __tablename__ = 'City'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    # Relationships
    state_id = db.Column(db.Integer,
                         db.ForeignKey('State.id', ondelete='cascade'),
                         nullable=False)
    addresses = db.relationship('Address',
                                backref='city',
                                cascade='all, delete-orphan', passive_deletes=True)
    artists = db.relationship('Artist',
                              backref='city')


class State(db.Model):
    __tablename__ = 'State'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, index=True)
    # Relationships
    cities = db.relationship('City',
                             backref='state',
                             cascade='all, delete-orphan', passive_deletes=True)

    # COMPLETED: implement any missing fields, as a database migration using Flask-Migrate


# COMPLETED Implement Show and Artist models,
# and complete all model relationships and properties, as a database migration.
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


def find_by_prop(item_arg, items_list, prop):
    return next((item for item in items_list if getattr(item, prop) == item_arg), None)


def reduce_venues_by_city(venues):
    cities = []
    for venue in venues:
        city = find_by_prop(venue.address.city.id, cities, 'id')
        if (city):
            city.venues.append(venue)
        else:
            cities.append(venue.address.city)
            venue.address.city.venues = [venue]
    return cities


def count_upcomping_shows(shows):
    count = 0
    for show in shows:
        if show.start_time > datetime.now():
            count += 1
    return count


def format_venues(venues):
    formatted_venues = []
    for venue in venues:
        num_upcoming_shows = count_upcomping_shows(venue.shows)
        formatted_venues.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_upcoming_shows
        })
    return formatted_venues


def format_genres(genres):
    formatted_genres = []
    for genre in genres:
        formatted_genres.append(genre.name)
    return formatted_genres


def filter_shows(shows):
    shows_result = {
        "past_shows": [],
        "upcoming_shows": []
    }
    for show in shows:
        if show.start_time > datetime.now():
            shows_result["upcoming_shows"].append(show)
        else:
            shows_result["past_shows"].append(show)
    return shows_result


def format_shows(shows):
    formatted_shows = []

    if not shows:
        return []

    for show in shows:
        formatted_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": str(show.start_time)
        })
    return formatted_shows


def format_artists(artists):
    formatted_artists = []
    if not artists:
        return formatted_artists
    for artist in artists:
        num_upcoming_shows = count_upcomping_shows(artist.shows)
        formatted_artists.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": num_upcoming_shows
        })
    return formatted_artists


# ----------------------------------------------------------------------------#
# Providers.
# ----------------------------------------------------------------------------#

def find_address_or_create(address, city, state, commit=True):
    new_address = find_address(address, city, state)
    if not new_address:
        new_address = create_address(address, city, state)
    if commit:
        db.session.commit()
    return new_address


def find_city_or_create(city, state, commit=True):
    new_city = find_city(city, state)
    if not new_city:
        new_city = create_city(city, state)
    if commit:
        db.session.commit()
    return new_city


def find_city(city, state):
    city_instance = City \
        .query \
        .filter_by(name=city) \
        .join(State, State.name == state) \
        .first()
    return city_instance


def create_city(city, state, commit=True):
    state_instance = State \
        .query \
        .filter_by(name=state) \
        .first()

    if not state_instance:
        new_city = City(name=city)
        new_state = State(name=state)

        new_city.state = new_state

        db.session.add(new_state)
        if commit:
            db.session.commit()
        return new_city

    city_instance = City.query \
        .filter_by(name=city) \
        .join(State, State.name == state) \
        .first()

    if not city_instance:
        new_city = City(name=city)
        new_city.state = state_instance
        db.session.add(new_city)
        if commit:
            db.session.commit()
        return new_city

    return city_instance


def find_address(address, city, state):
    address_instance = Address \
        .query \
        .filter_by(name=address) \
        .join(City, City.name == city) \
        .join(State, State.name == state) \
        .first()
    return address_instance


def create_address(address, city, state, commit=True):
    state_instance = State \
        .query \
        .filter_by(name=state) \
        .first()

    if not state_instance:
        new_address = Address(name=address)
        new_city = City(name=city)
        new_state = State(name=state)

        new_address.city = new_city
        new_city.state = new_state

        db.session.add(new_state)
        db.session.commit()
        return new_address

    city_instance = City.query \
        .filter_by(name=city) \
        .join(State, State.name == state) \
        .first()

    if not city_instance:
        new_address = Address(name=address)
        new_city = City(name=city)
        new_address.city = new_city
        new_city.state = state_instance
        db.session.add(new_city)
        db.session.commit()
        return new_address

    new_address = Address(name=address)
    new_address.city = city_instance
    db.session.add(new_address)
    db.session.commit()
    return new_address


def find_genres_or_create(genres, commit=True):
    if not genres:
        return []

    filter_args = or_(*map(lambda genre_name: Genre.name == genre_name, genres))
    genres_instance = Genre.query.filter(filter_args).all()

    for genre in genres:
        has_genre = find_by_prop(genre, genres_instance, 'name')
        if not has_genre:
            new_genre = create_genre(genre, False)
            genres_instance.append(new_genre)

    if commit:
        db.session.commit()
    return genres_instance


def create_genre(genre, commit=True):
    genre_instance = Genre \
        .query \
        .filter_by(name=genre) \
        .first()
    if genre_instance:
        return genre_instance
    new_genre = Genre(name=genre)
    db.session.add(new_genre)
    if commit:
        db.session.commit()
    return new_genre


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    venues = Venue.query.all()
    cities = reduce_venues_by_city(venues)

    data = []

    for city in cities:
        formatedVenues = format_venues(city.venues)
        data.append({
            "city": city.name,
            "state": city.state.name,
            "venues": formatedVenues
        })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # COMPLETED: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    search = "%{}%".format(search_term)
    venues = Venue.query.filter(Venue.name.ilike(search)).all()
    response = {
        "count": len(venues),
        "data": format_venues(venues)
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    print('Show venue by id', venue_id)
    # shows the venue page with the given venue_id
    # COMPLETED: replace with real venue data from the venues table, using venue_id

    venue = Venue.query.get(venue_id)
    if not venue:
        return abort(404)

    filtered_shows = filter_shows(venue.shows)
    past_shows = format_shows(filtered_shows["past_shows"])
    upcoming_shows = format_shows(filtered_shows["past_shows"])

    data = {
        "id": venue.id,
        "name": venue.name,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "image_link": venue.image_link,
        "genres": format_genres(venue.genres),
        "address": venue.address.name,
        "city": venue.address.city.name,
        "state": venue.address.city.state.name,
        "seeking_talent": True if venue.seeking_talent else False,
        "seeking_description": venue.seeking_talent.description if venue.seeking_talent else None,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
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
    # COMPLETED: insert form data as a new Venue record in the db, instead
    # COMPLETED: modify data to be the data object returned from db insertion
    address = request.form.get('address', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    genres = request.form.getlist('genres')

    venue = Venue(
        name=request.form.get('name', ''),
        phone=request.form.get('phone', ''),
        image_link=request.form.get('image_link', ''),
        website=request.form.get('website', ''),
        facebook_link=request.form.get('facebook_link', ''),
        genres=find_genres_or_create(genres, False),
        address=find_address_or_create(address, city, state, False)
    )
    try:
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except SQLAlchemyError as e:
        db.session.rollback()
        # COMPLETED: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
    # COMPLETED: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()

        # on successful db insert, flash success
        flash('Venue ' + venue_id + ' was successfully deleted!')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('An error occurred. Venue ' + venue_id + ' could not be deleted.')
    return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # COMPLETED: replace with real data returned from querying the database
    artists = Artist.query.all()
    data = format_artists(artists)
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # COMPLETED: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    search = "%{}%".format(search_term)
    artists = Artist.query.filter(Artist.name.ilike(search)).all()
    response = {
        "count": len(artists),
        "data": format_artists(artists)
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # COMPLETED: replace with real venue data from the venues table, using venue_id

    artist = Artist.query.get(artist_id)
    if not artist:
        return abort(404)

    filtered_shows = filter_shows(artist.shows)
    past_shows = format_shows(filtered_shows["past_shows"])
    upcoming_shows = format_shows(filtered_shows["past_shows"])

    data = {
        "id": artist.id,
        "name": artist.name,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "image_link": artist.image_link,
        "genres": format_genres(artist.genres),
        "city": artist.city.name,
        "state": artist.city.state.name,
        "seeking_venue": True if artist.seeking_venue else False,
        "seeking_description": artist.seeking_venue.description if artist.seeking_venue else None,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    artist = Artist.query.get(artist_id)

    if not artist:
        return abort(404)

    form.genres.default = format_genres(artist.genres)
    form.process()

    artist = {
        "id": artist.id,
        "name": artist.name,
        "phone": artist.phone,
        "website": artist.website if artist.website else '',
        "facebook_link": artist.facebook_link if artist.facebook_link else '',
        "image_link": artist.image_link if artist.image_link else '',
        "genres": format_genres(artist.genres),
        "city": artist.city.name,
        "state": artist.city.state.name,
        "seeking_venue": True if artist.seeking_venue else False,
        "seeking_description": artist.seeking_venue.description if artist.seeking_venue else None,
    }
    # COMPETED: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # COMPLETED: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    genres = request.form.getlist('genres')

    try:
        artist = Artist.query.get(artist_id)
        artist.name = request.form.get('name', '')
        artist.phone = request.form.get('phone', '')
        artist.website = request.form.get('website', '')
        artist.facebook_link = request.form.get('facebook_link', '')
        artist.image_link = request.form.get('image_link', '')

        artist.genres = find_genres_or_create(genres, False)
        artist.city = find_city_or_create(city, state, False)

        # artist.seeking_venue = request.form.get('image_link', '')
        db.session.add(artist)
        db.session.commit()

        # on successful db insert, flash success
        flash('Artist ' + str(artist_id) + ' was successfully edited!')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('An error occurred. Artist ' + str(artist_id) + ' could not be edited.')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    venue_instance = Venue.query.get(venue_id)

    if not venue_instance:
        return abort(404)

    form.genres.default = format_genres(venue_instance.genres)
    form.process()

    venue = {
        "id": venue_instance.id,
        "name": venue_instance.name,
        "phone": venue_instance.phone,
        "website": venue_instance.website if venue_instance.website else '',
        "facebook_link": venue_instance.facebook_link if venue_instance.facebook_link else '',
        "image_link": venue_instance.image_link if venue_instance.image_link else '',
        "genres": format_genres(venue_instance.genres),
        "address": venue_instance.address.name,
        "city": venue_instance.address.city.name,
        "state": venue_instance.address.city.state.name,
        "seeking_venue": True if venue_instance.seeking_talent else False,
        "seeking_description": venue_instance.seeking_talent.description if venue_instance.seeking_talent else None,
    }

    # COMPLETED: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # COMPLETED: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    city = request.form.get('city', '')
    state = request.form.get('state', '')
    genres = request.form.getlist('genres')

    try:
        venue = Venue.query.get(venue_id)
        venue.name = request.form.get('name', '')
        venue.phone = request.form.get('phone', '')
        venue.website = request.form.get('website', '')
        venue.facebook_link = request.form.get('facebook_link', '')
        # venue.image_link = request.form.get('image_link', '') # View not implemented

        venue.genres = find_genres_or_create(genres, False)
        venue.city = find_city_or_create(city, state, False)

        # artist.seeking_venue = request.form.get('image_link', '') # View not implemented
        db.session.add(venue)
        db.session.commit()

        # on successful db insert, flash success
        flash('Venue ' + str(venue_id) + ' was successfully edited!')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('An error occurred. Venue ' + str(venue_id) + ' could not be edited.')

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
    # COMPLETED: insert form data as a new Venue record in the db, instead
    # COMPLETED: modify data to be the data object returned from db insertion
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    genres = request.form.getlist('genres')

    try:
        artist = Artist()
        artist.name = request.form.get('name', '')
        artist.phone = request.form.get('phone', '')
        artist.website = request.form.get('website', '')
        artist.facebook_link = request.form.get('facebook_link', '')
        artist.image_link = request.form.get('image_link', '')

        artist.city = find_city_or_create(city, state, False)
        artist.genres = find_genres_or_create(genres, False)

        # artist.seeking_venue = request.form.get('image_link', '')
        db.session.add(artist)
        db.session.commit()

        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except SQLAlchemyError as e:
        db.session.rollback()
        # COMPLETED: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # COMPLETED: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    shows = Show.query.all()
    data = format_shows(shows)

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        show = Show()
        show.venue_id = request.form.get('venue_id', None)
        show.artist_id = request.form.get('artist_id', None)
        show.start_time = dateutil.parser.isoparse(request.form.get('start_time', None))
        # called to create new shows in the db, upon submitting new show listing form
        # COMPLETED: insert form data as a new Show record in the db, instead
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except SQLAlchemyError as e:
        db.session.rollback()
        # COMPLETED: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

    return render_template('pages/home.html')


@app.route('/shows/search', methods=['POST'])
def search_shows():
    search_term = request.form.get('search_term', '')
    search = search_term
    shows = Show.query.all()
    response = {
        "count": len(shows),
        "data": format_shows(shows)
    }
    return render_template('pages/show.html', results=response,
                           search_term=search_term)


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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
