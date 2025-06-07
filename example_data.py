# Example data for Django models
# You can use this in a Django management command or in the Django shell

from django.contrib.auth import get_user_model
from albums.models import Genre, Album, Track, AlbumActivity, Plaque, PlaquePurchase
from datetime import date, timedelta, time
from decimal import Decimal

User = get_user_model()

# Create example users (artists)
def create_example_users():
    # Create artists
    artist1 = User.objects.create_user(
        username='baba_harare',
        email='baba@uzinduzi.com',
        first_name='Rodney',
        last_name='Harare',
        is_artist=True,
        stage_name='Baba Harare'
    )
    
    artist2 = User.objects.create_user(
        username='winky_d',
        email='winky@uzinduzi.com',
        first_name='Wallace',
        last_name='Chirumiko',
        is_artist=True,
        stage_name='Winky D'
    )
    
    artist3 = User.objects.create_user(
        username='jah_prayzah',
        email='jah@uzinduzi.com',
        first_name='Mukudzeyi',
        last_name='Mukombe',
        is_artist=True,
        stage_name='Jah Prayzah'
    )
    
    # Create fans
    fan1 = User.objects.create_user(
        username='fan_one',
        email='fan1@uzinduzi.com',
        first_name='John',
        last_name='Doe',
        is_artist=False
    )
    
    fan2 = User.objects.create_user(
        username='fan_two',
        email='fan2@uzinduzi.com',
        first_name='Jane',
        last_name='Smith',
        is_artist=False
    )
    
    return artist1, artist2, artist3, fan1, fan2

# Create example genres
def create_example_genres():
    genres = []
    genre_choices = ['jiti', 'sungura', 'jazz', 'hip_hop', 'gospel', 'reggae', 'zimdancehall', 'mbira', 'dancehall', 'trap']
    
    for genre_name in genre_choices:
        genre, created = Genre.objects.get_or_create(name=genre_name)
        genres.append(genre)
    
    return genres

# Create example albums
def create_example_albums(artists, genres):
    albums = []
    
    # Album 1 - Baba Harare
    album1 = Album.objects.create(
        artist=artists[0],  # Baba Harare
        title="Heavenly Grace",
        release_date=date.today() + timedelta(days=30),  # 30 days from now
        genre=genres[0],  # jiti
        cover_art="albums/covers/heavenly_grace.jpg",
        description="A journey through divine mercy, each song reflects the boundless grace and love bestowed upon us. Melodious harmonies guide listeners toward spiritual rejuvenation and faith.",
        track_count=12,
        copyright_info="© 2024 Baba Harare Music",
        publisher="Uzinduzi Records",
        credits="Produced by Steve The Magician, Mixed by DJ Tamuka",
        affiliation="Chipaz Productions",
        duration="00:45:30",
        is_published=True,
        is_featured=True
    )
    albums.append(album1)
    
    # Album 2 - Winky D
    album2 = Album.objects.create(
        artist=artists[1],  # Winky D
        title="Gombwe",
        release_date=date.today() + timedelta(days=15),  # 15 days from now
        genre=genres[6],  # zimdancehall
        cover_art="albums/covers/gombwe.jpg",
        description="The Gafa returns with another masterpiece that speaks to the heart of Zimbabwe. Raw, authentic, and revolutionary.",
        track_count=10,
        copyright_info="© 2024 Winky D Entertainment",
        publisher="Vigilance Records",
        credits="Produced by Oskid, Mixed by Cymplex Music",
        affiliation="Vigilance Productions",
        duration="00:38:45",
        is_published=True,
        is_featured=True
    )
    albums.append(album2)
    
    # Album 3 - Jah Prayzah
    album3 = Album.objects.create(
        artist=artists[2],  # Jah Prayzah
        title="Gwara",
        release_date=date.today() + timedelta(days=45),  # 45 days from now
        genre=genres[1],  # sungura
        cover_art="albums/covers/gwara.jpg",
        description="Contemporary Sungura with a modern twist. Jah Prayzah delivers another classic that bridges traditional and modern Zimbabwean music.",
        track_count=8,
        copyright_info="© 2024 Military Touch Movement",
        publisher="Jah Prayzah Music",
        credits="Produced by Rodney Beatz, Mixed by Andy Cutta",
        affiliation="Military Touch Movement",
        duration="00:32:20",
        is_published=True,
        is_featured=False
    )
    albums.append(album3)
    
    # Album 4 - Already Released
    album4 = Album.objects.create(
        artist=artists[0],  # Baba Harare
        title="The Reason",
        release_date=date.today() - timedelta(days=10),  # Released 10 days ago
        genre=genres[4],  # gospel
        cover_art="albums/covers/the_reason.jpg",
        description="An uplifting gospel album that celebrates faith, hope, and love through powerful melodies and inspiring lyrics.",
        track_count=6,
        copyright_info="© 2024 Baba Harare Music",
        publisher="Uzinduzi Records",
        credits="Produced by Steve The Magician",
        affiliation="Chipaz Productions",
        duration="00:28:15",
        is_published=True,
        is_featured=False
    )
    albums.append(album4)
    
    return albums

# Create example tracks
def create_example_tracks(albums):
    tracks = []
    
    # Tracks for Album 1 - Heavenly Grace
    heavenly_grace_tracks = [
        {
            "title": "Divine Mercy",
            "duration": "00:03:45",
            "track_number": 1,
            "producer": "Steve The Magician",
            "writer": "Baba Harare",
            "mastering_engineer": "DJ Tamuka",
            "featured_artists": "Darcus Moyo",
            "backing_vocals": "Mathias Memhere, Dike Mahoko",
            "instrumentation": "Trust Nemerai (Guitar), Mono Mukundu (Bass)",
            "track_credits": "A powerful opening track about divine intervention"
        },
        {
            "title": "Grace Abounds",
            "duration": "00:04:12",
            "track_number": 2,
            "producer": "Steve The Magician",
            "writer": "Baba Harare",
            "mastering_engineer": "DJ Tamuka",
            "backing_vocals": "Ellard Cherayi",
            "instrumentation": "Trust Nemerai (Guitar)",
            "track_credits": "Celebrating the abundance of grace in our lives"
        },
        {
            "title": "Faithful Heart",
            "duration": "00:03:58",
            "track_number": 3,
            "producer": "Steve The Magician",
            "writer": "Baba Harare, Darcus Moyo",
            "mastering_engineer": "DJ Tamuka",
            "featured_artists": "Mathias Memhere",
            "instrumentation": "Mono Mukundu (Bass), Trust Nemerai (Guitar)",
            "track_credits": "A heartfelt ballad about maintaining faith through trials"
        },
        {
            "title": "Blessed Assurance",
            "duration": "00:04:05",
            "track_number": 4,
            "producer": "Steve The Magician",
            "writer": "Baba Harare",
            "mastering_engineer": "DJ Tamuka",
            "backing_vocals": "Dike Mahoko, Ellard Cherayi",
            "track_credits": "Finding peace in God's promises"
        }
    ]
    
    for track_data in heavenly_grace_tracks:
        track = Track.objects.create(
            album=albums[0],
            **track_data,
            audio_file=f"albums/tracks/heavenly_grace_{track_data['track_number']}.mp3",
            track_art=f"albums/tracks/art/heavenly_grace_{track_data['track_number']}.jpg",
            release_date=albums[0].release_date,
            is_published=True
        )
        tracks.append(track)
    
    # Tracks for Album 2 - Gombwe
    gombwe_tracks = [
        {
            "title": "Intro (Gombwe)",
            "duration": "00:02:30",
            "track_number": 1,
            "producer": "Oskid",
            "writer": "Winky D",
            "mastering_engineer": "Cymplex Music",
            "track_credits": "Setting the tone for the album"
        },
        {
            "title": "Disappear",
            "duration": "00:04:15",
            "track_number": 2,
            "producer": "Oskid",
            "writer": "Winky D",
            "mastering_engineer": "Cymplex Music",
            "featured_artists": "Gemma Griffiths",
            "track_credits": "A collaboration about overcoming challenges"
        },
        {
            "title": "Kasong Kejecha",
            "duration": "00:03:52",
            "track_number": 3,
            "producer": "Oskid",
            "writer": "Winky D",
            "mastering_engineer": "Cymplex Music",
            "track_credits": "Traditional Shona wisdom meets modern beats"
        },
        {
            "title": "Ngirozi",
            "duration": "00:04:28",
            "track_number": 4,
            "producer": "Oskid",
            "writer": "Winky D",
            "mastering_engineer": "Cymplex Music",
            "backing_vocals": "Vigilance Crew",
            "track_credits": "Spiritual guidance through music"
        }
    ]
    
    for track_data in gombwe_tracks:
        track = Track.objects.create(
            album=albums[1],
            **track_data,
            audio_file=f"albums/tracks/gombwe_{track_data['track_number']}.mp3",
            track_art=f"albums/tracks/art/gombwe_{track_data['track_number']}.jpg",
            release_date=albums[1].release_date,
            is_published=True
        )
        tracks.append(track)
    
    # Tracks for Album 3 - Gwara
    gwara_tracks = [
        {
            "title": "Gwara",
            "duration": "00:04:20",
            "track_number": 1,
            "producer": "Rodney Beatz",
            "writer": "Jah Prayzah",
            "mastering_engineer": "Andy Cutta",
            "track_credits": "Title track showcasing modern Sungura"
        },
        {
            "title": "Mukadzi Wangu",
            "duration": "00:03:45",
            "track_number": 2,
            "producer": "Rodney Beatz",
            "writer": "Jah Prayzah",
            "mastering_engineer": "Andy Cutta",
            "featured_artists": "Ammara Brown",
            "track_credits": "A love song dedicated to his wife"
        },
        {
            "title": "Hokoyo",
            "duration": "00:04:10",
            "track_number": 3,
            "producer": "Rodney Beatz",
            "writer": "Jah Prayzah",
            "mastering_engineer": "Andy Cutta",
            "backing_vocals": "Third Generation Band",
            "track_credits": "Warning against life's temptations"
        }
    ]
    
    for track_data in gwara_tracks:
        track = Track.objects.create(
            album=albums[2],
            **track_data,
            audio_file=f"albums/tracks/gwara_{track_data['track_number']}.mp3",
            track_art=f"albums/tracks/art/gwara_{track_data['track_number']}.jpg",
            release_date=albums[2].release_date,
            is_published=True
        )
        tracks.append(track)
    
    return tracks

# Create example album activities (fan support)
def create_example_activities(albums, fans):
    activities = []
    
    # Fan 1 supports Album 1
    activity1 = AlbumActivity.objects.create(
        user=fans[0],
        album=albums[0],
        liked=True,
        bid_amount=Decimal('150.00'),
        currency='USD',
        amount_supported=Decimal('150.00'),
        plaque_count=1
    )
    activities.append(activity1)
    
    # Fan 2 supports Album 1
    activity2 = AlbumActivity.objects.create(
        user=fans[1],
        album=albums[0],
        liked=True,
        bid_amount=Decimal('75.00'),
        currency='USD',
        amount_supported=Decimal('75.00'),
        plaque_count=1
    )
    activities.append(activity2)
    
    # Fan 1 supports Album 2
    activity3 = AlbumActivity.objects.create(
        user=fans[0],
        album=albums[1],
        liked=True,
        bid_amount=Decimal('200.00'),
        currency='USD',
        amount_supported=Decimal('200.00'),
        plaque_count=1
    )
    activities.append(activity3)
    
    return activities

# Create example plaque purchases
def create_example_plaques(activities):
    plaques = []
    
    for activity in activities:
        # Create plaque
        plaque = Plaque.objects.create()
        
        # Create plaque purchase
        purchase = PlaquePurchase.objects.create(
            plaque=plaque,
            fan=activity.user,
            album_supported=activity.album,
            hash_key=plaque.hash_key,
            contribution_amount=activity.amount_supported,
            payment_status='completed',
            payment_method='credit_card',
            transaction_id=f'txn_{plaque.hash_key[:8]}'
        )
        plaques.append(purchase)
    
    return plaques

# Main function to create all example data
def create_all_example_data():
    print("Creating example users...")
    artists = create_example_users()
    
    print("Creating example genres...")
    genres = create_example_genres()
    
    print("Creating example albums...")
    albums = create_example_albums(artists[:3], genres)
    
    print("Creating example tracks...")
    tracks = create_example_tracks(albums)
    
    print("Creating example activities...")
    activities = create_example_activities(albums, artists[3:])
    
    print("Creating example plaques...")
    plaques = create_example_plaques(activities)
    
    print("Example data created successfully!")
    print(f"Created {len(artists)} users")
    print(f"Created {len(genres)} genres")
    print(f"Created {len(albums)} albums")
    print(f"Created {len(tracks)} tracks")
    print(f"Created {len(activities)} activities")
    print(f"Created {len(plaques)} plaque purchases")

# To run this, you can use Django shell:
# python manage.py shell
# >>> exec(open('example_data.py').read())
# >>> create_all_example_data()