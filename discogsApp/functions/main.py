from datetime import datetime
from django.core.mail import EmailMessage
from discogsApp.functions.db import Database_project
from discogsApp.functions.ds_objects import add_masters_from_db, create_excel, check_tracks_credits, expand_credit_roles
from discogsApp.functions.ds_objects import filter_performer_credits, filter_author_credits, filter_non_year_credits
from discogsApp.functions.ds_objects import get_unique_tracks, get_combine_credits, get_credits_from_db, get_clean_trackNames
from discogsApp.functions.ds_objects import remove_featured_track_check, set_featured_artist_flag, set_static
from discogsApp.functions.ds_objects import set_mainrelease_flag, set_masters_flag, set_territory_flag, set_release_id_flag
from discogsApp.functions.ds_objects import set_published_date_flag, setExceptionCredit, sort_credits
from discogsApp.functions.ds_objects import update_featured_flag, update_format_type, update_media_type


# main function to:
# Retrieve tracks and releases credits from database based on user data from view.py module and database orm in db.py module
# Convert to a credit object and add to list container
#Reduce data and enrich data based on business rules from ds_objects.py
#Create Excel spreadsheet for data for reporting
#Send email based on user data from view.py module
#This function will either send data to user or if fail send blank spreadsheet


def run_report_discogs(artists, main_artist_name, artists_dict, email, reportType):

    try:

        database = Database_project()  # set database object

        start_time = datetime.now()  # set startime for testing compiliation duration

        credits_list = get_credits_from_db(database, artists, main_artist_name, artists_dict)  # get set of credits from database
        credits_list = add_masters_from_db(database, credits_list)  # enrich credits data with masters data from database
        credits_list = check_tracks_credits(credits_list)  # ensure track specific data for artist is filtered
        credits_list = expand_credit_roles(credits_list)  # expand credits data to ensure 1 credit role per credit

        if reportType == 'master' or reportType == 'performer':  # confirm request report type for filtering
            credits_list = filter_performer_credits(credits_list)  # filter performer only credits in list
        else:
            credits_list = filter_author_credits(credits_list)  # filter author only credits in list

        credits_list = filter_non_year_credits(credits_list, artists_dict)  # filter credits in the years selected
        credits_list = setExceptionCredit(credits_list)  # as per business rules create exception field for credit roles
        credits_list = set_featured_artist_flag(credits_list)   # set featured artist field 1 or 0 to sort credit in list
        credits_list = set_mainrelease_flag(credits_list)  # set main release flag field 1 or to 0 sort credit in list
        credits_list = set_masters_flag(credits_list)  # set masters flag field 1 or 0 to sort credit in list
        credits_list = set_territory_flag(credits_list)   # set territory flag field 1 or 0 to sort credit in list
        credits_list = set_release_id_flag(credits_list)  # set release id field integer to sort credit in list
        credits_list = set_published_date_flag(credits_list)  # set published date field integer to sort credit in list
        credits_list = sort_credits(credits_list)  # sort credits list to prioritize credit
        credits_list = get_clean_trackNames(credits_list)  # remove white spaces in track name for reporting
        credits_list = get_unique_tracks(credits_list)  # reduce dataset based on track name, credit role and credits to remove duplicates
        credits_list = get_combine_credits(credits_list)  # reduce dataset based on track name and combine credits roles by track
        credits_list = remove_featured_track_check(credits_list, artists_dict)  # reduce dataset based on artists selected by user
        credits_list = update_featured_flag(credits_list)  # enrich featured artist field based on main artist
        credits_list = update_format_type(credits_list)  # enrich format field based on database field format type
        credits_list = update_media_type(credits_list)  # enrich media field based on database field media type
        credits_list = set_static(credits_list)  # set isrc and country recording to -- add manually -- as database does not contain this data
        ds_data = create_excel(credits_list, main_artist_name)  # create excel object based on credits list to send to user

        end_time = datetime.now()  # set endtime for testing compiliation duration
        print('complete: secs: {0}'.format((end_time-start_time).seconds))  # print compilations time to server

        send_to = [email, 'whitworth.applications@gmail.com']  # set send email address list  based on user input and my email address for monitoring
        subject = '{0}: Discography'.format(main_artist_name)  # set main artist name as email subject
        message = 'Attached artist discography'  # set email message body

        email = EmailMessage(subject, message, 'whitworth.applications@gmail.com', send_to)  # set Django email object
        email.attach('{0}_{1}discography.xlsx'.format(reportType, main_artist_name), ds_data)  # create spreadsheet to email
        email.send(fail_silently=False)  # send email and do not block if failed
        # email fail notification to be added at a later date

    except:

        send_to = [email, 'whitworth.applications@gmail.com']  # set send email address list  based on user input and my email address for monitoring
        subject = '{0}: Discography'.format(main_artist_name)  # set main artist name as email subject
        message = 'Attached artist discography - failed'  # set email message body as process failed

        email = EmailMessage(subject, message, 'whitworth.applications@gmail.com', send_to)  # create Django email object
        email.send(fail_silently=False)  # send email and do not block if failed
        # email fail notification to be added at a later date

    return ds_data
