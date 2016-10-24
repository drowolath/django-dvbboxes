import dvbboxes
from django import forms

TOWNS = ()
for town in dvbboxes.TOWNS
    TOWNS += ((town, town), )


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
