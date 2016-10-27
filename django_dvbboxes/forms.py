import dvbboxes
import time
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
    filename = forms.FileField(required=True)

    def clean_filename(self):
        filename = self.cleaned_data['filename']
        try:
            service_id, start, stop = filename.name.split('_')
            assert service_id in dvbboxes.CHANNELS
            assert len(start) == 8
            assert len(stop) == 8
            time.mktime(time.strptime(start, '%d%m%Y'))
            time.mktime(time.strptime(stop, '%d%m%Y'))
            return filename
        except (ValueError, AssertionError):
            msg = "'{}' est un nom de fichier invalide".format(
                filename.name)
            raise forms.ValidationError(msg)


class ApplyListingForm(forms.Form):
    parsed_data = forms.CharField(max_length=1024000, required=True)
    towns = forms.MultipleChoiceField(choices=TOWNS, required=False)
    service_id = forms.ChoiceField(choices=CHANNELS, required=True)


class ProgramForm(forms.Form):
    towns = forms.MultipleChoiceField(choices=TOWNS, required=False)
    date = forms.CharField(required=True)
    service_id = forms.ChoiceField(choices=CHANNELS, required=True)

    def clean_date(self):
        date = self.cleaned_data['date']
        try:
            assert len(date) == 8
            time.mktime(time.strptime(date, '%d%m%Y'))
            return date
        except (ValueError, AssertionError):
            msg = "{} est une date invalide".format(date)
            raise forms.ValidationError(msg)
