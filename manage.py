from flask_script import Manager

from app import *

manager = Manager(app)


@manager.command
def seed():
    add_venues_seed()
    db.session.commit()


def add_venues_seed():
    state1 = State(name='CA')
    state2 = State(name='NY')

    city1 = City(name='San Francisco')
    city2 = City(name='New York')

    address1 = Address(name='1015 Folsom Street')
    address2 = Address(name='335 Delancey Street')
    address3 = Address(name='34 Whiskey Moore Ave')

    city1.addresses = [address1, address3]
    city2.addresses = [address2]
    state1.cities = [city1]
    state2.cities = [city2]

    genre1 = Genre(name='Jazz')
    genre2 = Genre(name="Reggae")
    genre3 = Genre(name="Swing")
    genre4 = Genre(name="Classical")
    genre5 = Genre(name="Folk")
    genre6 = Genre(name="R&B")
    genre7 = Genre(name="Hip-Hop")
    genre8 = Genre(name="Rock n Roll")

    genres_list1 = [genre1, genre2, genre3, genre4, genre5]
    genres_list2 = [genre4, genre6, genre7]
    genres_list3 = [genre8, genre1, genre4, genre5]

    show1 = Show(
        start_time=format_datetime("2019-05-21T21:30:00.000Z")
    )
    show2 = Show(
        start_time=format_datetime("2019-06-15T23:00:00.000Z")
    )
    show3 = Show(
        start_time=format_datetime("2035-04-01T20:00:00.000Z")
    )
    show4 = Show(
        start_time=format_datetime("2035-04-01T20:00:00.000Z")
    )
    show5 = Show(
        start_time=format_datetime("2035-04-15T20:00:00.000Z")
    )

    seeking_talent1 = Talent_Seeking(
        description="We are on the lookout for a local artist to play every two weeks. Please call us."
    )

    venue1 = Venue(
        name="The Musical Hop",
        phone="123-123-1234",
        image_link="https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
        website="https://www.themusicalhop.com",
        facebook_link="https://www.facebook.com/TheMusicalHop",
        genres=genres_list1,
        shows=[show1],
        address=address1,
        seeking_talent=seeking_talent1,
    )
    venue2 = Venue(
        name="The Dueling Pianos Bar",
        phone="914-003-1132",
        image_link="https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
        website="https://www.theduelingpianos.com",
        facebook_link="https://www.facebook.com/theduelingpianos",
        genres=genres_list2,
        address=address2,
        seeking_talent=None,
    )
    venue3 = Venue(
        name="Park Square Live Music & Coffee",
        phone="415-000-1234",
        image_link="https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        website="https://www.parksquarelivemusicandcoffee.com",
        facebook_link="https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
        genres=genres_list3,
        address=address3,
        shows=[show2, show3, show4, show5],
        seeking_talent=None,
    )
    venues = [venue1, venue2, venue3]
    db.session.add_all(venues)

    seeking_venue1 = Venue_Seeking(
        description='Looking for shows to perform at in the San Francisco Bay Area!'
    )

    artist1 = Artist(
        name="Guns N Petals",
        phone="326-123-5000",
        facebook_link="https://www.facebook.com/GunsNPetals",
        image_link="https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        genres=[genre8],
        city=city2,
        shows=[show1],
        seeking_venue=seeking_venue1
    )
    artist2 = Artist(
        name="Matt Quevedo",
        phone="300-400-5000",
        facebook_link="https://www.facebook.com/mattquevedo923251523",
        image_link="https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        genres=[genre1],
        city=city2,
        shows=[show2],
        seeking_venue=None
    )
    artist3 = Artist(
        name="The Wild Sax Band",
        phone="300-400-5000",
        facebook_link=None,
        image_link="https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        genres=[genre1, genre4],
        city=city1,
        shows=[show3, show4, show5],
        seeking_venue=None
    )

    artists = [artist1, artist2, artist3]
    db.session.add_all(artists)


if __name__ == "__main__":
    manager.run()
