from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from albums.models import Genre, Album, Track, AlbumActivity, Plaque, PlaquePurchase
from datetime import date, timedelta
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with example data'

    def handle(self, *args, **options):
        self.stdout.write('Creating example data...')
        
        # Clear existing data (optional)
        if self.confirm_action('Do you want to clear existing data?'):
            Track.objects.all().delete()
            Album.objects.all().delete()
            AlbumActivity.objects.all().delete()
            PlaquePurchase.objects.all().delete()
            Plaque.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write('Existing data cleared.')
        
        # Create users
        artists = self.create_users()
        
        # Create genres
        genres = self.create_genres()
        
        # Create albums
        albums = self.create_albums(artists[:3], genres)
        
        # Create tracks
        self.create_tracks(albums)
        
        # Create activities
        activities = self.create_activities(albums, artists[3:])
        
        # Create plaques
        self.create_plaques(activities)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with example data!')
        )

    def confirm_action(self, message):
        response = input(f"{message} (y/N): ")
        return response.lower() in ['y', 'yes']

    def create_users(self):
        users = []
        
        # Artists
        artist_data = [
            {
                'email': 'baba@uzinduzi.com',
                'first_name': 'Rodney',
                'last_name': 'Harare',
                'stage_name': 'Baba Harare',
                'phone_number': '+263771234567',
                'whatsapp_number': '+263771234567',
                'country_of_residence': 'Zimbabwe',
                'citizenship': 'Zimbabwean'
            },
            {
                'email': 'winky@uzinduzi.com',
                'first_name': 'Wallace',
                'last_name': 'Chirumiko',
                'stage_name': 'Winky D',
                'phone_number': '+263772345678',
                'whatsapp_number': '+263772345678',
                'country_of_residence': 'Zimbabwe',
                'citizenship': 'Zimbabwean'
            },
            {
                'email': 'jah@uzinduzi.com',
                'first_name': 'Mukudzeyi',
                'last_name': 'Mukombe',
                'stage_name': 'Jah Prayzah',
                'phone_number': '+263773456789',
                'whatsapp_number': '+263773456789',
                'country_of_residence': 'Zimbabwe',
                'citizenship': 'Zimbabwean'
            }
        ]
        
        for data in artist_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    **data,
                    'is_artist': True,
                    'password': 'pbkdf2_sha256$600000$test$test'
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
                self.stdout.write(f'Created artist: {user.first_name} {user.last_name}')
            else:
                self.stdout.write(f'Artist already exists: {user.first_name} {user.last_name}')
            users.append(user)
        
        # Fans
        fan_data = [
            {
                'email': 'fan1@uzinduzi.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone_number': '+263774567890',
                'whatsapp_number': '+263774567890',
                'country_of_residence': 'Zimbabwe',
                'citizenship': 'Zimbabwean'
            },
            {
                'email': 'fan2@uzinduzi.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'phone_number': '+263775678901',
                'whatsapp_number': '+263775678901',
                'country_of_residence': 'Zimbabwe',
                'citizenship': 'Zimbabwean'
            }
        ]
        
        for data in fan_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    **data,
                    'is_artist': False,
                    'password': 'pbkdf2_sha256$600000$test$test'
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
                self.stdout.write(f'Created fan: {user.first_name} {user.last_name}')
            else:
                self.stdout.write(f'Fan already exists: {user.first_name} {user.last_name}')
            users.append(user)
        
        self.stdout.write(f'Total users: {len(users)}')
        return users

    def create_genres(self):
        genre_choices = ['jiti', 'sungura', 'jazz', 'hip_hop', 'gospel', 'reggae', 'zimdancehall', 'mbira', 'dancehall', 'trap']
        genres = []
        
        for genre_name in genre_choices:
            genre, created = Genre.objects.get_or_create(name=genre_name)
            if created:
                self.stdout.write(f'Created genre: {genre_name}')
            genres.append(genre)
        
        self.stdout.write(f'Total genres: {len(genres)}')
        return genres

    def create_albums(self, artists, genres):
        albums_data = [
            {
                'artist': artists[0],
                'title': 'Heavenly Grace',
                'release_date': date.today() + timedelta(days=30),
                'genre': genres[0],  # jiti
                'description': 'A journey through divine mercy, each song reflects the boundless grace and love bestowed upon us. Melodious harmonies guide listeners toward spiritual rejuvenation and faith.',
                'track_count': 4,
                'is_featured': True,
                'copyright_info': '© 2024 Baba Harare Music',
                'publisher': 'Uzinduzi Records',
                'credits': 'Produced by Steve The Magician, Mixed by DJ Tamuka',
                'affiliation': 'Chipaz Productions',
                'duration': timedelta(minutes=45, seconds=30)
            },
            {
                'artist': artists[1],
                'title': 'Gombwe',
                'release_date': date.today() + timedelta(days=15),
                'genre': genres[6],  # zimdancehall
                'description': 'The Gafa returns with another masterpiece that speaks to the heart of Zimbabwe. Raw, authentic, and revolutionary.',
                'track_count': 4,
                'is_featured': True,
                'copyright_info': '© 2024 Winky D Entertainment',
                'publisher': 'Vigilance Records',
                'credits': 'Produced by Oskid, Mixed by Cymplex Music',
                'affiliation': 'Vigilance Productions',
                'duration': timedelta(minutes=38, seconds=45)
            },
            {
                'artist': artists[2],
                'title': 'Gwara',
                'release_date': date.today() + timedelta(days=45),
                'genre': genres[1],  # sungura
                'description': 'Contemporary Sungura with a modern twist. Jah Prayzah delivers another classic that bridges traditional and modern Zimbabwean music.',
                'track_count': 3,
                'is_featured': False,
                'copyright_info': '© 2024 Military Touch Movement',
                'publisher': 'Jah Prayzah Music',
                'credits': 'Produced by Rodney Beatz, Mixed by Andy Cutta',
                'affiliation': 'Military Touch Movement',
                'duration': timedelta(minutes=32, seconds=20)
            },
            {
                'artist': artists[0],
                'title': 'The Reason',
                'release_date': date.today() - timedelta(days=10),  # Already released
                'genre': genres[4],  # gospel
                'description': 'An uplifting gospel album that celebrates faith, hope, and love through powerful melodies and inspiring lyrics.',
                'track_count': 3,
                'is_featured': False,
                'copyright_info': '© 2024 Baba Harare Music',
                'publisher': 'Uzinduzi Records',
                'credits': 'Produced by Steve The Magician',
                'affiliation': 'Chipaz Productions',
                'duration': timedelta(minutes=28, seconds=15)
            }
        ]
        
        albums = []
        for data in albums_data:
            album, created = Album.objects.get_or_create(
                title=data['title'],
                artist=data['artist'],
                defaults={
                    **data,
                    'cover_art': f'albums/covers/{data["title"].lower().replace(" ", "_")}.jpg',
                    'is_published': True
                }
            )
            if created:
                self.stdout.write(f'Created album: {album.title} by {album.artist.stage_name}')
            else:
                self.stdout.write(f'Album already exists: {album.title}')
            albums.append(album)
        
        self.stdout.write(f'Total albums: {len(albums)}')
        return albums

    def create_tracks(self, albums):
        track_count = 0
        
        # Tracks for Heavenly Grace
        heavenly_grace_tracks = [
            {
                'title': 'Divine Mercy',
                'duration': timedelta(minutes=3, seconds=45),
                'track_number': 1,
                'producer': 'Steve The Magician',
                'writer': 'Baba Harare',
                'mastering_engineer': 'DJ Tamuka',
                'featured_artists': 'Darcus Moyo',
                'backing_vocals': 'Mathias Memhere, Dike Mahoko',
                'instrumentation': 'Trust Nemerai (Guitar), Mono Mukundu (Bass)',
                'track_credits': 'A powerful opening track about divine intervention'
            },
            {
                'title': 'Grace Abounds',
                'duration': timedelta(minutes=4, seconds=12),
                'track_number': 2,
                'producer': 'Steve The Magician',
                'writer': 'Baba Harare',
                'mastering_engineer': 'DJ Tamuka',
                'backing_vocals': 'Ellard Cherayi',
                'instrumentation': 'Trust Nemerai (Guitar)',
                'track_credits': 'Celebrating the abundance of grace in our lives'
            },
            {
                'title': 'Faithful Heart',
                'duration': timedelta(minutes=3, seconds=58),
                'track_number': 3,
                'producer': 'Steve The Magician',
                'writer': 'Baba Harare, Darcus Moyo',
                'mastering_engineer': 'DJ Tamuka',
                'featured_artists': 'Mathias Memhere',
                'instrumentation': 'Mono Mukundu (Bass), Trust Nemerai (Guitar)',
                'track_credits': 'A heartfelt ballad about maintaining faith through trials'
            },
            {
                'title': 'Blessed Assurance',
                'duration': timedelta(minutes=4, seconds=5),
                'track_number': 4,
                'producer': 'Steve The Magician',
                'writer': 'Baba Harare',
                'mastering_engineer': 'DJ Tamuka',
                'backing_vocals': 'Dike Mahoko, Ellard Cherayi',
                'track_credits': 'Finding peace in God\'s promises'
            }
        ]
        
        for track_data in heavenly_grace_tracks:
            track, created = Track.objects.get_or_create(
                album=albums[0],
                track_number=track_data['track_number'],
                defaults={
                    'title': track_data['title'],
                    'duration': track_data['duration'],
                    'producer': track_data.get('producer'),
                    'writer': track_data.get('writer'),
                    'mastering_engineer': track_data.get('mastering_engineer'),
                    'featured_artists': track_data.get('featured_artists'),
                    'backing_vocals': track_data.get('backing_vocals'),
                    'instrumentation': track_data.get('instrumentation'),
                    'track_credits': track_data.get('track_credits'),
                    'release_date': albums[0].release_date,
                    'is_published': True
                }
            )
            if created:
                track_count += 1
                self.stdout.write(f'Created track: {track.title}')
        
        # Create simple tracks for other albums
        for album in albums[1:]:
            for i in range(1, album.track_count + 1):
                track, created = Track.objects.get_or_create(
                    album=album,
                    track_number=i,
                    defaults={
                        'title': f'{album.title} Track {i}',
                        'duration': timedelta(minutes=3, seconds=45),
                        'producer': 'Example Producer',
                        'writer': album.artist.stage_name,
                        'is_published': True,
                        'release_date': album.release_date
                    }
                )
                if created:
                    track_count += 1
                    self.stdout.write(f'Created track: {track.title}')
        
        self.stdout.write(f'Total tracks created: {track_count}')

    def create_activities(self, albums, fans):
        activities = []
        activity_data = [
            {'fan': fans[0], 'album': albums[0], 'amount': Decimal('150.00')},
            {'fan': fans[1], 'album': albums[0], 'amount': Decimal('75.00')},
            {'fan': fans[0], 'album': albums[1], 'amount': Decimal('200.00')},
            {'fan': fans[1], 'album': albums[1], 'amount': Decimal('125.00')},
            {'fan': fans[0], 'album': albums[2], 'amount': Decimal('300.00')},
        ]
        
        for data in activity_data:
            activity, created = AlbumActivity.objects.get_or_create(
                user=data['fan'],
                album=data['album'],
                defaults={
                    'liked': True,
                    'bid_amount': data['amount'],
                    'currency': 'USD',
                    'amount_supported': data['amount'],
                    'plaque_count': 1
                }
            )
            if created:
                activities.append(activity)
                self.stdout.write(f'Created activity: {activity.user.first_name} supported {activity.album.title} with ${activity.amount_supported}')
        
        self.stdout.write(f'Total activities created: {len(activities)}')
        return activities

    def create_plaques(self, activities):
        plaque_count = 0
        for activity in activities:
            plaque = Plaque.objects.create()
            purchase, created = PlaquePurchase.objects.get_or_create(
                fan=activity.user,
                album_supported=activity.album,
                defaults={
                    'plaque': plaque,
                    'hash_key': plaque.hash_key,
                    'contribution_amount': activity.amount_supported,
                    'payment_status': 'completed',
                    'payment_method': 'credit_card',
                    'transaction_id': f'txn_{plaque.hash_key[:8]}'
                }
            )
            if created:
                plaque_count += 1
                self.stdout.write(f'Created plaque purchase: {purchase.fan.first_name} - {purchase.plaque.plaque_type}')
        
        self.stdout.write(f'Total plaque purchases created: {plaque_count}')