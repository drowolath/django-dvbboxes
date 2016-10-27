import dvbboxes
from datetime import datetime
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
    filename = forms.FileField()


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
            datetime.strptime(date, '%d%m%Y')
            return date
        except (ValueError, AssertionError):
            msg = "Please, make sure the date follows ddmmyyyy format"
            raise forms.ValidationError(msg)
