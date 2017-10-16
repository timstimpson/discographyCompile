from django import forms

datesRange = [(0,'all')] + [(x, str(1899+x)) for x in range(1,121)]

class artist_search(forms.Form): 
    artist_name = forms.CharField(label='')
    media = forms.ChoiceField(choices=(('1', 'author'), ('2','performer'),('3','master discography')),widget=forms.RadioSelect,label='', initial = '1')



class alias_form(forms.Form): 
    name = forms.CharField(label='', widget=forms.TextInput(attrs={'readonly':'readonly'}))
    alias_id = forms.IntegerField(label='', required = False, widget=forms.TextInput(attrs={'readonly':'readonly'}))
    members = forms.IntegerField(label='',)
    from_date = forms.ChoiceField(choices = datesRange,label='')
    to_date = forms.ChoiceField(choices = datesRange,label='')
    roles = forms.CharField(label='')
    include = forms.BooleanField(label='', widget=forms.CheckboxInput(attrs={'class':'alias_includeInput'}), initial = True)
    group = forms.BooleanField(label='', initial = True)
    main_artist = forms.BooleanField(label='', initial = False)


class email_form(forms.Form):

    email_address = forms.EmailField(label='', initial = 'enteryour@emailaddress')

