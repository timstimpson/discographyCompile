import copy
import io
import pandas as pd
from operator import attrgetter
from datetime import datetime
from discogsApp.functions.globals import discography_location, non_active_roles, md_headers, author_credits_roles


# A number of functions to add business rules which reduce and enrich Credit Object dataset container


# convert_to_tracks_index:
# Retrieve a string of track numbers in format x1,x2,x3,x4
# Business logic to handle some user specific formating ie. 1-4 or 1 to 4
# return a list of strings of all track numbers


def convert_to_tracks_index(tracks):

    tracks = tracks.replace(' ', '').replace('to', ' - ')
    tracks = tracks.split(',')

    try:

        for track in tracks:

            if ' - ' in track:
                to_track = track.split('-')
                start_point = int(to_track[0])
                end_point = int(to_track[1]) + 1
                additional_tracks = [str(x) for x in range(start_point, end_point)]
                tracks = tracks + additional_tracks
            else:

                pass
    except:

        pass

    return tracks


# get_credits_from_db:
# Retrieve a dataset of track and release objects from database using db.py orm module and user data from main.py module


def get_credits_from_db(database, artists, main_artist_name, artists_dict):

    credits_list = []

    start_time = datetime.now()

    for credit in database.get_track_credits(artist_id=artists):
        c = Credit.without_master(credit, main_artist_name, artists_dict)
        c.release_type = False
        c.exception_type = False
        credits_list.append(c)

    end_time = datetime.now()

    print('{0}:\t complete: secs: {1}'.format('database_tracks', (end_time-start_time).seconds))

    start_time = datetime.now()

    for credit in database.get_release_credits(artist_id=artists):

        c = Credit.without_master(credit, main_artist_name, artists_dict)
        c.release_type = True
        c.exception_type = False
        credits_list.append(c)

    end_time = datetime.now()

    print('{0}:\t complete: secs: {1}'.format('database_release', (end_time-start_time).seconds))

    return credits_list


# add_masters_from_db:
# Enrich credits list with a dataset of masters data from database using db.py orm module and user data from main.py module


def add_masters_from_db(database, credits_list):

    return_credits = []

    masters_list = database.get_masters_details(set([credit.master_id for credit in credits_list]))
    masters_dict = dict(zip([str(master[0]) for master in masters_list], [master[1:] for master in masters_list]))

    for release in credits_list:

        if release.master_id and release.master_id in masters_dict.keys():
            release.has_master = True
            release.year_first_published = masters_dict[release.master_id][1]

            if masters_dict[release.master_id][0] == release.release_id:
                release.main_release = True
            else:
                release.main_release = False

            return_credits.append(release)

        else:
            release.has_master = False
            release.main_release = True
            return_credits.append(release)

    return return_credits


# check_tracks_credits:
# Reduce Credit objects dataset based on specific tracks ranges


def check_tracks_credits(credits_list):

    return_credits = []

    for credit in credits_list:

        if credit.artist_tracks:
            if credit.track_position in convert_to_tracks_index(credit.artist_tracks):
                credit.track_exceptions = None
                credit.track_number = None
                return_credits.append(credit)

            else:
                credit.track_exceptions = credit.artist_tracks
                credit.track_number = credit.track_position
                return_credits.append(credit)

        else:
            credit.track_exceptions = None
            credit.track_number = None
            return_credits.append(credit)

    return return_credits


# expand_credit_roles:
# expand credits dataset to ensure 1 credit role per credit


def expand_credit_roles(credits_list):

    return_credits = []

    for credit in credits_list:
        try:
            roles = credit.track_credit_role.split(',')

        except:
            roles = ['exception', ]

        for role in roles:

            new_credit = copy.deepcopy(credit)
            new_role = role.strip()
            new_credit.role = new_role
            return_credits.append(new_credit)

    return return_credits


# filter_performer_credits:
# filter credits dataset based on credit role names in global.py non_active_roles


def filter_performer_credits(credits_list):

    return_credits = []

    for credit in credits_list:

        non_active_role = False

        for check_role in non_active_roles:

            if credit.role.upper().find(check_role) != -1 and credit.role.upper().find('REMIX') == -1:
                non_active_role = True

            else:
                pass

        if not non_active_role:
            return_credits.append(credit)

    return return_credits


# filter_author_credits:
# filter credits dataset based on credit role names in global.py author_credits_roles


def filter_author_credits(credits_list):

    return_credits = []

    for credit in credits_list:

        rights_credit = False

        for check_role in author_credits_roles:

            if credit.role.upper().find(check_role) != -1:
                rights_credit = True

            else:
                pass

        if rights_credit:
            return_credits.append(credit)

    return return_credits


# filter_non_year_credits:
# filter credits dataset based on active years in group based on user input from main.py


def filter_non_year_credits(credits_list, artists_dict):

    return_credits = []

    for credit in credits_list:

        if artists_dict[credit.artist_id]['from_date'] == '0':
            date_from = 0

        else:
            date_from = int(artists_dict[credit.artist_id]['from_date']) + 1899

        if artists_dict[credit.artist_id]['to_date'] == '0':
            date_to = 9999

        else:
            date_to = int(artists_dict[credit.artist_id]['to_date']) + 1899

        if not credit.year_first_published:
            return_credits.append(credit)

        elif int(credit.year_first_published) >= date_from and int(credit.year_first_published) <= date_to:
            return_credits.append(credit)

        else:
            pass

    return return_credits


# setExceptionCredit:
# business rule to create credit role exception based on generic database data for non featured artist release credit


def setExceptionCredit(credits_list):

    return_credits = []

    for credit in credits_list:

        if credit.release_type and not credit.artist_tracks and not credit.main_artist:
            credit.exception_role = credit.role

        else:
            credit.exception_role = None

        return_credits.append(credit)

    return return_credits


# set_featured_artist_flag:
# Set integer flag 2 or 1 based on main_artist credit object attribute for sorting dataset


def set_featured_artist_flag(credits_list):

    return_credits = []

    for credit in credits_list:

        if credit.main_artist:
            credit.featured_artist_flag = 1
            credit.Featuring_as_a_session_musician = 'N'

        else:
            credit.featured_artist_flag = 2
            credit.Featuring_as_a_session_musician = 'Y'

        return_credits.append(credit)

    return return_credits


# set_mainrelease_flag:
# Set integer flag 2 or 1 based on main_release credit object attribute for sorting dataset


def set_mainrelease_flag(credits_list):

    return_credits = []

    for credit in credits_list:

        if credit.main_release:
            credit.main_release_flag = 1

        else:
            credit.main_release_flag = 2

        return_credits.append(credit)

    return return_credits


# set_masters_flag:
# Set integer flag 2 or 1 based on has_master credit object attribute for sorting dataset


def set_masters_flag(credits_list):

    return_credits = []

    for credit in credits_list:

        if credit.has_master:
            credit.master_flag = 1

        else:
            credit.master_flag = 2

        return_credits.append(credit)

    return return_credits


# set_territory_flag:
# Set integer flag range based on country_code credit object attribute for sorting dataset


def set_territory_flag(credits_list):

    def code(country):

        country_code = 4

        if country:
            if 'UK' in country.upper() != -1 and 'EUROPE' in country.upper() != -1:
                country_code = 1

            if country.upper() == 'EUROPE':
                country_code = 2

            if country.upper() == 'UK':
                country_code = 3

            if country.upper() == 'US':
                country_code = 5

        else:
            country_code = 5

        return country_code

    return_credits = []

    for credit in credits_list:

        credit.territory_flag = code(credit.country_recording)

        return_credits.append(credit)

    return return_credits


# set_release_id_flag:
# Set integer flag range based on release_id credit object attribute for sorting dataset


def set_release_id_flag(credits_list):

    return_credits = []

    for credit in credits_list:

        if credit.release_id:
            credit.release_id_flag = int(credit.release_id)

        else:
            credit.release_id_flag = 0

        return_credits.append(credit)

    return return_credits


# set_published_date_flag:
# Set integer flag range based on year_first_published credit object attribute for sorting dataset
# if data is None set to 9999 to ensure error is treated defensively


def set_published_date_flag(credits_list):

    return_credits = []

    for credit in credits_list:

        if credit.year_first_published:
            try:
                credit.published_date_flag = int(credit.year_first_published)

            except:
                try:
                    credit.published_date_flag = int(credit.year_first_published.split('-')[0])

                except:
                    credit.published_date_flag = 9999

        else:
            credit.published_date_flag = 9999

        return_credits.append(credit)

    return return_credits


# sort_credits:
# sort credits based on previously set business rule flags


def sort_credits(credits_list):

    sorted_data = sorted(credits_list, key=attrgetter(
        'featured_artist_flag', 'main_release_flag',
        'master_flag', 'published_date_flag',
        'territory_flag', 'release_id_flag'
        )
    )

    return sorted_data

# get_clean_trackNames:
# Clean track names of trailing and leading white spaces


def get_clean_trackNames(credits_list):

    return_credits = []

    for credit in credits_list:

        credit.track_title = str(credit.track_title).strip()
        return_credits.append(credit)

    return return_credits


# get_unique_tracks:
# Ensure Credit dataset is has no duplicates based on track name, credit role and credit name


def get_unique_tracks(credits_list):

    return_credits = []
    combined_keys = []

    for credit in credits_list:

        combined_key = str(credit.track_title) + str(credit.role) + str(credit.credit_name)

        if combined_key in combined_keys:

            pass

        else:

            combined_keys.append(combined_key)
            return_credits.append(credit)

    return return_credits


# remove_featured_track_check:
# Ensure Credit dataset is has no credits other than those based on the artist names from main.py


def remove_featured_track_check(credits_list, artists_dict):

    return_credits = []
    artists_list = [artist['artist_name'] for artist in artists_dict.values()]

    for credit in credits_list:

        artist_check = False

        if not credit.main_artist:
            artist_check = True

        else:
            pass

        try:
            for artist in credit.artists.split(','):

                if artist.strip() in artists_list:
                    artist_check = True

                else:
                    pass

        except:
            artist_check = True

        if artist_check:
            return_credits.append(credit)

        else:
            pass

    return return_credits


# update_format_type:
# Standardize credit format_type field in credit dataset based on user business rules


def update_format_type(credits_list):

    return_credits = []

    for credit in credits_list:

        if credit.format_type:
            format_type = credit.format_type.upper()

        else:
            format_type = 'Unknown'

        if format_type.find('ALB') != -1:
            credit.format_type = 'Album'

        elif format_type.find('LP') != -1:
            credit.format_type = 'Album'

        elif format_type.find('12') != -1:
            credit.format_type = 'Single'

        elif format_type.find('7') != -1:
            credit.format_type = 'Single'

        elif format_type.find('SING') != -1:
            credit.format_type = 'Single'

        elif format_type.find('EP') != -1:
            credit.format_type = 'Single'

        elif format_type.find('COMP') != -1:
            credit.format_type = 'Compilation'

        elif format_type.find('MIX') != -1:
            credit.format_type = 'Compilation'

        elif format_type.find('') != -1:
            credit.format_type = 'Digital'

        elif format_type.find('AAC') != -1:
            credit.format_type = 'Digital'

        else:
            credit.format_type = 'Unknown'

        return_credits.append(credit)

    return return_credits


# update_media_type:
# Standardize credit format_media field in credit dataset based on user business rules


def update_media_type(credits_list):

    return_credits = []

    for credit in credits_list:

        if credit.format_media:
            format_media = credit.format_media.upper()

        else:
            format_media = 'Unknown'

        if format_media.find('VIN') != -1:
            credit.format_media = 'Vinyl'

        elif format_media.find('CD') != -1:
            credit.format_media = 'CD'

        elif format_media.find('FILE') != -1:
            credit.format_media = 'File'

        elif format_media.find('CAS') != -1:
            credit.format_media = 'Cassette'

        elif format_media.find('DVD') != -1:
            credit.format_media = 'DVD'

        else:
            credit.format_media = 'Unknown'

        return_credits.append(credit)

    return return_credits


# update_featured_flag:
# Standardize credit featured_artist field in credit dataset based on user business rules


def update_featured_flag(credits_list):

    return_credits = []

    for credit in credits_list:

        if credit.main_artist:
            credit.featured_artist = 'featured'

        else:
            credit.featured_artist = 'non_featured'

        return_credits.append(credit)

    return return_credits


# set_static:
# Standardize credit isrc_code and country_recording field in credit dataset based on user business rules


def set_static(credits_list):

    return_credits = []

    for credit in credits_list:

        credit.isrc_code = '-add-manually-'
        credit.country_recording = '-add-manually-'

        return_credits.append(credit)

    return return_credits


# get_combine_credits:
# Combine credit roles based on each individual track in the Credits dataset
# The prior sorting of the dataset ensure the user business rules prioritize credit fields when the dataset is reduced


def get_combine_credits(credits_list):

    unique_credits = []

    unique_keys = list(set([str(credit.track_title).upper() for credit in credits_list]))

    for key in unique_keys:

        key_check = False

        for credit in credits_list:

            if str(credit.track_title).upper() == key:
                if not key_check:
                    unique_credit = copy.deepcopy(credit)
                    unique_credit.roles = []
                    unique_credit.exception_roles = []

                    if credit.exception_role:
                        unique_credit.exception_roles.append(credit.exception_role)

                    else:
                        pass

                    unique_credit.roles.append(credit.role)
                    key_check = True

                else:
                    if credit.role not in unique_credit.roles:
                        unique_credit.roles.append(credit.role)

                    else:
                        pass

                    if credit.exception_role:
                        if credit.exception_role not in unique_credit.exception_roles:
                            unique_credit.exception_roles.append(credit.exception_role)

                        else:
                            pass

                    else:
                        pass

        unique_credit.roles = ', '.join(unique_credit.roles)
        unique_credit.exception_roles = ', '.join(unique_credit.exception_roles)

        if unique_credit.roles:
            if unique_credit.roles[0].strip() == ',':
                unique_credit.roles = unique_credit.roles[1:].strip()

            else:
                unique_credit.roles = unique_credit.roles.strip()

        else:
            pass

        unique_credits.append(unique_credit)

    return unique_credits


# create_excel:
# Create and return an excel spreadsheet IO object based on the Credit dataset to the main.py module
# The md_headers variable in globals.py determines the Credit object fields to be applied to the spreadsheet IO object


def create_excel(credits_list, main_artist_name):

    return_data = []

    headers = md_headers

    for credit in credits_list:

        return_line = [credit.__dict__[header] for header in headers]
        return_data.append(return_line)

    dataframe = pd.DataFrame(return_data, columns=headers)
    output_file = '{0}{1}_discography.xlsx'.format(discography_location, main_artist_name)
    output_file = io.BytesIO()

    writer = pd.ExcelWriter(output_file)
    excel = dataframe.to_excel(writer, 'Sheet1')
    writer.save()

    xlsx_data = output_file.getvalue()

    return xlsx_data


# Credit class:
# Required to standardize the performer credit fields attained from the db.py module
# Simple string overide for texting perposes
# Class method added for creating credit object based on current database retreival data and for extending when required
# Class method includes business rules for standardizing data based on current database field


class Credit:

    def __init__(
        self, full_name=None, first_name=None, last_name=None, artist_name=None, credit_name=None,
        track_credit_role=None, artists=None, group_member=None, main_artist=None, format_type=None,
        format_media=None, num_main_artists=None, track_title=None, main_release_label=None,
        nationality_producer=None, catno=None, live=None, country_recording=None, year_first_published=None,
        year_new_published=None, isrc_code=None, featured_artist=None, release_title=None, track_ref=None,
        artist_ref=None, artist_id=None, main_release=None, main_release_id=None, release_id=None,
        artist_tracks=None, track_position=None, has_master=None, master_id=None
    ):
        self.full_name = full_name
        self.first_name = first_name
        self.last_name = last_name
        self.artist_name = artist_name
        self.credit_name = credit_name
        self.track_credit_role = track_credit_role
        self.artists = artists
        self.group_member = group_member
        self.main_artist = main_artist
        self.format_type = format_type
        self.format_media = format_media
        self.num_main_artists = num_main_artists
        self.track_title = track_title
        self.main_release_label = main_release_label
        self.nationality_producer = nationality_producer
        self.catno = catno
        self.live = live
        self.country_recording = country_recording
        self.year_first_published = year_first_published
        self.year_new_published = year_new_published
        self.isrc_code = isrc_code
        self.featured_artist = featured_artist
        self.release_title = release_title
        self.track_ref = track_ref
        self.artist_ref = artist_ref
        self.artist_id = artist_id
        self.release_id = release_id
        self.main_release = main_release
        self.main_release_id = main_release_id
        self.artist_tracks = artist_tracks
        self.track_position = track_position
        self.has_master = has_master
        self.master_id = master_id
        self.last_name = last_name
        self.first_name = first_name

    def __str__(self):

        return '{0}'.format(self.track_title)

    @classmethod
    def without_master(cls, db_object, main_artist_name, artists_dict):

        artist_name, credit_name, track_credit_role, track_artists, release_artists, featured_artist, format_type, format_media, track_title, main_release_label, catno, year_published, release_title, track_ref, artist_ref, artist_id, release_id, track_position, artist_tracks, master_id = db_object

        artist_id = str(artist_id)
        master_id = str(master_id)

        main_release = False
        has_master = False

        if featured_artist == 'yes':
            main_artist = True
            num_main_artists = artists_dict[artist_id]['members']
        else:
            main_artist = False
            num_main_artists = '-add-manually-'

        if credit_name and not artists_dict[artist_id]['group']:
            pass

        else:
            credit_name = main_artist_name

        main_artist_list = main_artist_name.strip().split(" ")

        if len(main_artist_list) > 1:
            last_name = main_artist_list[-1]
            first_name = ' '.join(main_artist_list[:-1])

        else:
            first_name = main_artist_list[0]
            last_name = ''

        if featured_artist == 'yes':
            if track_credit_role:
                track_credit_role += + ' ,' + artists_dict[str(artist_id)]['roles']

            else:
                track_credit_role = artists_dict[str(artist_id)]['roles']

        else:
            pass

        live = 'N'

        if release_title:
            if release_title.upper().find('LIVE') != -1:
                live = 'Y'

            else:
                live = 'N'

        if track_title:
            if track_title.upper().find('LIVE') != -1:
                live = 'Y'
            else:
                live = 'N'

        try:
            year = year_published.split('-')
            year_published = year[0]

        except:
            year_published = year_published

        if main_release_label:
            main_release_label = main_release_label.split(',')[0]

        else:
            pass

        if catno:
            catno = catno.split(',')[0]

        else:
            pass

        return Credit(
            artist_name=artist_name, credit_name=credit_name,
            track_credit_role=track_credit_role, artists=track_artists, group_member=main_artist,
            featured_artist=featured_artist, main_artist=main_artist, num_main_artists=num_main_artists,
            format_type=format_type, format_media=format_media, track_title=track_title, live=live,
            main_release_label=main_release_label, catno=catno, year_first_published=year_published,
            year_new_published=year_published, release_title=release_title, track_ref=track_ref,
            artist_ref=artist_ref, artist_id=artist_id, main_release=main_release, release_id=release_id,
            main_release_id=release_id, artist_tracks=artist_tracks, track_position=track_position, has_master=has_master,
            master_id=master_id, first_name=first_name, last_name=last_name
        )
