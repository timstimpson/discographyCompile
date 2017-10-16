database_dev = '/Users/timstimpson/projectApps/discographyCompile/database/discogs_releases_xml20170701.db'
database_old_path = '/Users/timstimpson/Development/database/discogs_releases_masters_xml.db'
database_path_aws = '/home/ubuntu/ds_vol/discogsapp/compile_ds/functions/discogs_releases_xml20170701.db'
database_small_path = '/Users/timstimpson/Development/database/discogs_releases_xml20170701_200000.db'

database_path = database_dev 

non_active_roles = ['MIX', 'WRIT', 'ENGIN', 'MASTER', 'RECORD', 'ART', 'ARRANGE', 'COMPO', 'LYRICS']
author_credits_roles = ['WRIT', 'MUSIC', 'COMPO', 'ARRANGE']

md_headers = [
    'first_name', 'last_name', 'credit_name', 'roles', 'artists', 'group_member', 'main_artist',
    'format_type', 'format_media', 'num_main_artists', 'track_title', 'main_release_label',
    'nationality_producer', 'catno', 'live', 'country_recording', 'year_first_published',
    'year_new_published', 'isrc_code', 'Featuring_as_a_session_musician', 'release_title',
    'exception_roles', 'track_exceptions', 'track_number']

discography_location = '/Users/timstimpson/Desktop/'
