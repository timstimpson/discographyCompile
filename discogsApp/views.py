from django.shortcuts import render
from discogsApp.forms import artist_search, alias_form, email_form
import discogs_client
from django import forms
from django.forms import formset_factory
from discogsApp.functions import main
from threading import Thread


#Create discogs_client api object
def discogsClient():

    return discogs_client.Client('Whitworth/1.0,token', user_token='IFQryQxIipaOZxcAKjrnehBdkTzKBzJDKcUDfZyZ')


#Render index page html
def index(request):
    #Create artist search for for input on index page
    artistNameForm = artist_search

    return render(request, 'index.html', {
        'form': artistNameForm,
    })


#Render find artist page html
def find_artist(request):
    #Render find artist page html
    artistNameForm = artist_search(request.POST)

    if artistNameForm.is_valid():  # Confirm artist search form is valid

        artist_name = artistNameForm.cleaned_data['artist_name']  # assign artist name variable based on artist search form
        d = discogsClient()
        #create a list of possible artists based on discogs search with maximum options of 10 fields
        artist_list = [(artist.name, artist.id) for artist in d.search(artist_name, type='artist')][:10]
        #create checkbox form based on list of possible artists
        selectArtistForm = forms.ChoiceField(choices=artist_list)
    else:
        #if form is invalid create an empty search artist form
        artistNameForm = artist_search
        #render the index page as the artist is invalid
        return render(request, 'index.html', {
            'form': artistNameForm,
        })
    #render the find artist page with checkbox selection for correct artist
    return render(request, 'find_artist.html', {
        'artist_select': selectArtistForm,
        'form': artistNameForm,
    })


#Render find artist alias html
def find_alias(request):

    d = discogsClient()
    #Persist the report type through the artist_search_form
    search_type_form = artist_search(request.POST)

    #Get the discogs artist reference as integer based on request POST field 'my_choice_field'
    search_artist_id = int(request.POST.get('my_choice_field'))
    search_artist_name = search_type_form['artist_name'].value()

    aliases = [(search_artist_name, search_artist_id)] + [(x.name, x.id) for x in d.artist(search_artist_id).aliases]

    alias_groups = []

    for alias_name, alias_id in aliases:

        alias_groups = alias_groups + [(x.name, x.id) for x in d.artist(alias_id).groups]

    alias_form_set_data = []

    for name, _id in aliases:

        alias_form_set_data.append({'name': name, 'alias_id': _id, 'group': False, 'main_artist': False, 'members': 1})

    alias_form_set_data[0]['main_artist'] = True

    for name, _id in alias_groups:

        alias_form_set_data.append({'name': name, 'alias_id': _id, 'group': True, 'main_artist': False, 'members': 1})

    alias_form_set = formset_factory(alias_form, extra=0)
    alias_form_set = alias_form_set(initial=alias_form_set_data)
    email_address_form = email_form()

    return render(request, 'find_alias.html', {
        'alias_form': alias_form,
        'alias_form_set': alias_form_set,
        'email_form': email_address_form,
        'type_form': search_type_form,
    })


#Render find confirm alias html
def confirm_alias(request):

    if request.method == 'POST':
        #Get the report type from the artist search form
        discogs_type = int(artist_search(request.POST)['media'].value())
        #Initialize the alias_form_set
        alias_form_set = formset_factory(alias_form, extra=0)
        #add data from request.POST to the alias_form_set
        artists_form = alias_form_set(data=request.POST)
        #initialize and add data from request.POST to the email address form
        email_address_form = email_form(data=request.POST)

        #Confirm main artist name for report structure
        if artists_form:
            main_artist_name = artists_form[0]['name'].value()
        else:
            main_artist_name = None

        #Initialize artists list for database search
        artists = []
        #Initialize artists dict for data attributes
        artists_dict = {}

        #For each artists in active artists form add data to the artists dict and list
        for artist in artists_form:
            #only include active artists
            if artist['include'].value():
                artists.append(artist['alias_id'].value())
                artists_dict[artist['alias_id'].value()] = {}
                artists_dict[artist['alias_id'].value()]['artist_name'] = artist['name'].value()
                artists_dict[artist['alias_id'].value()]['roles'] = artist['roles'].value()
                artists_dict[artist['alias_id'].value()]['group'] = artist['group'].value()
                artists_dict[artist['alias_id'].value()]['members'] = artist['members'].value()
                artists_dict[artist['alias_id'].value()]['from_date'] = artist['from_date'].value()
                artists_dict[artist['alias_id'].value()]['to_date'] = artist['to_date'].value()

        #extract email address from email address form to send report
        email = email_address_form['email_address'].value()

        #set up threads to run the reporting creation algorithym based on the reporting type selected.
        if discogs_type == 1:
            t = Thread(target=main.run_report_discogs, args=(artists, main_artist_name, artists_dict, email, 'author'))
            t.start()
        if discogs_type == 2:
            t = Thread(target=main.run_report_discogs, args=(artists, main_artist_name, artists_dict, email, 'performer'))
            t.start()
        if discogs_type == 3:
            t = Thread(target=main.run_report_discogs, args=(artists, main_artist_name, artists_dict, email, 'master'))
            t.start()
    else:
        pass

    return render(request, 'confirm_alias.html', {
        'to_send_email': email,
    })
