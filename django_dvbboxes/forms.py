import dvbboxes
from django import forms

TOWNS = ()
for town in dvbboxes.TOWNS:
    TOWNS += ((town, town), )

CHANNELS = ()
for i in sorted(dvbboxes.CHANNELS):
    CHANNELS += ((i, dvbboxes.CHANNELS[i]),)


class SearchMediaForm(forms.Form):
    """search for media name in towns"""
    expression = forms.CharField(max_length=100, required=True)
    towns = forms.MultipleChoiceField(choices=TOWNS, required=False)


class MediaInfosForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    desc = forms.CharField(max_length=1000000, required=False)


class RenameMediaForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)


class DeleteMediaForm(forms.Form):
    file = forms.FileField(required=True)
    towns = forms.MultipleChoiceField(choices=TOWNS, required=False)


class UploadListingForm(forms.Form):
    """uploading a listing"""
    file = forms.FileField(required=True)


class ApplyListingForm(forms.Form):
    parsed_data = forms.CharField(max_length=1024000, required=True)
    towns = forms.MultipleChoiceField(choices=TOWNS, required=False)
    service_id = forms.ChoiceField(choices=CHANNELS, required=True)


class ProgramForm(forms.Form):
    towns = forms.MultipleChoiceField(choices=TOWNS, required=False)
    date = forms.CharField(required=True)
    service_id = forms.ChoiceField(choices=CHANNELS, required=True)


class StandardForm(forms.Form):
    """given text, apply proper action throughout cluster"""
    expression = forms.CharField(max_length=100, required=True)
    town = forms.MultipleChoiceField(choices=TOWNS, required=False)


class UploadFileForm(forms.Form):
    """uploading a file"""
    file = forms.FileField(required=True)
    town = forms.ChoiceField(choices=TOWNS, required=False)


class ChooseTownForm(forms.Form):
    """simply choose towns"""
    town = forms.MultipleChoiceField(choices=TOWNS, required=True)


class UploadForm(forms.Form):
    """uploading a file"""
    file = forms.FileField(required=True)
