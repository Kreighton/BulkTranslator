from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from urllib.parse import urlparse

from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import Row, Column, Submit, HTML


from . import models


class CustomParserForm(forms.Form):
    urls_field = forms.CharField(widget=forms.Textarea, max_length=99999999999999999)

    def __init__(self, *args, **kwargs):
        super(CustomParserForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


SELECTOR_TYPE_CHOICES = (
    ('Default', 'Default'),
    ('CSS', 'CSS'),
    ('XPath', 'Xpath'),
)

SELECTOR_TYPES = (
    ('CSS', 'CSS'),
    ('XPath', 'Xpath'),
)


class ChooseSelectorsForm(forms.Form):
    custom_selector = forms.CharField(max_length=200, required=False, label=False)
    type_of_selector = forms.ChoiceField(choices=SELECTOR_TYPE_CHOICES, label=False)

    class Meta:
        model = models.UserDomainSelectors
        fields = ['custom_selector', 'type_of_selector']

    def __init__(self, *args, **kwargs):
        super(ChooseSelectorsForm, self).__init__(*args, **kwargs)


class AddSelectorForm(forms.Form):
    domain_for_selector = forms.CharField(max_length=300, label='Enter domain:')
    selector_type = forms.ChoiceField(choices=SELECTOR_TYPES, label='Type of selector:')
    selector = forms.CharField(max_length=300, label='Enter selector:')

    class Meta:
        model = models.UserDomainSelectors
        fields = ['domain_for_selector', 'selector_type', 'selector']

    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username')
        super(AddSelectorForm, self).__init__(*args, **kwargs)

    def clean_domain_for_selector(self):
        domain = self.cleaned_data['domain_for_selector']
        new = models.UserDomainSelectors.objects.filter(domain_for_selector=domain, user=self.username)
        if new.count():
            raise ValidationError('This user already use this domain selector!')
        else:
            return domain


class EditSelectorForm(forms.ModelForm):
    domain_for_selector = forms.CharField(max_length=300, label=False, widget=forms.TextInput(attrs={
        'readonly': 'readonly',
        'class': 'article-item-readonly',
    }))
    selector_type = forms.ChoiceField(choices=SELECTOR_TYPES, label='Type of selector:')
    user_selector = forms.CharField(max_length=300, label='Enter selector:')

    def __init__(self, *args, **kwargs):
        domain_for_selector_initial = kwargs.pop('domain_for_selector')
        selector_type_initial = kwargs.pop('selector_type')
        user_selector_initial = kwargs.pop('user_selector')
        super(EditSelectorForm, self).__init__(*args, **kwargs)
        self.fields['domain_for_selector'].initial = domain_for_selector_initial
        self.fields['selector_type'].initial = selector_type_initial
        self.fields['user_selector'].initial = user_selector_initial

    class Meta:
        model = models.UserDomainSelectors
        fields = ['domain_for_selector', 'selector_type', 'user_selector']

DEEPL_LANGUAGES = (

)

GOOGLE_LANGUAGES = (
    ('en', 'English'),
    ('af', 'Afrikaans'),
    ('sq', 'Albanian'),
    ('am', 'Amharic'),
    ('ar', 'Arabic'),
    ('hy', 'Armenian'),
    ('az', 'Azerbaijani'),
    ('eu', 'Basque'),
    ('be', 'Belarusian'),
    ('bn', 'Bengali'),
    ('bs', 'Bosnian'),
    ('bg', 'Bulgarian'),
    ('ca', 'Catalan'),
    ('ceb', 'Cebuano'),
    ('zh', 'Chinese (Simplified)'),
    ('zh-TW', 'Chinese (Traditional)'),
    ('co', 'Corsican'),
    ('hr', 'Croatian'),
    ('cs', 'Czech'),
    ('da', 'Danish'),
    ('nl', 'Dutch'),
    ('eo', 'Esperanto'),
    ('et', 'Estonian'),
    ('fi', 'Finnish'),
    ('fr', 'French'),
    ('fy', 'Frisian'),
    ('gl', 'Galician'),
    ('ka', 'Georgian'),
    ('de', 'German'),
    ('el', 'Greek'),
    ('gu', 'Gujarati'),
    ('ht', 'Haitian Creole'),
    ('ha', 'Hausa'),
    ('haw', 'Hawaiian'),
    ('he or iw', 'Hebrew'),
    ('hi', 'Hindi'),
    ('hmn)', 'Hmong'),
    ('hu', 'Hungarian'),
    ('is', 'Icelandic'),
    ('ig', 'Igbo'),
    ('id', 'Indonesian'),
    ('ga', 'Irish'),
    ('it', 'Italian'),
    ('ja', 'Japanese'),
    ('jv', 'Javanese'),
    ('kn', 'Kannada'),
    ('kk', 'Kazakh'),
    ('km', 'Khmer'),
    ('rw', 'Kinyarwanda'),
    ('ko', 'Korean'),
    ('ku', 'Kurdish'),
    ('ky', 'Kyrgyz'),
    ('lo', 'Lao'),
    ('la', 'Latin'),
    ('lv', 'Latvian'),
    ('lt', 'Lithuanian'),
    ('lb', 'Luxembourgish'),
    ('mk', 'Macedonian'),
    ('mg', 'Malagasy'),
    ('ms', 'Malay'),
    ('ml', 'Malayalam'),
    ('mt', 'Maltese'),
    ('mi', 'Maori'),
    ('mr', 'Marathi'),
    ('mn', 'Mongolian'),
    ('my', 'Myanmar (Burmese)'),
    ('ne', 'Nepali'),
    ('no', 'Norwegian'),
    ('ny', 'Nyanja (Chichewa)'),
    ('or', 'Odia (Oriya)'),
    ('ps', 'Pashto'),
    ('fa', 'Persian'),
    ('pl', 'Polish'),
    ('pt', 'Portuguese (Portugal, Brazil)'),
    ('pa', 'Punjabi'),
    ('ro', 'Romanian'),
    ('ru', 'Russian'),
    ('sm', 'Samoan'),
    ('gd', 'Scots Gaelic'),
    ('sr', 'Serbian'),
    ('st', 'Sesotho'),
    ('sn', 'Shona'),
    ('sd', 'Sindhi'),
    ('si', 'Sinhala (Sinhalese)'),
    ('sk', 'Slovak'),
    ('sl', 'Slovenian'),
    ('so', 'Somali'),
    ('es', 'Spanish'),
    ('su', 'Sundanese'),
    ('sw', 'Swahili'),
    ('sv', 'Swedish'),
    ('tl', 'Tagalog (Filipino)'),
    ('tg', 'Tajik'),
    ('ta', 'Tamil'),
    ('tt', 'Tatar'),
    ('te', 'Telugu'),
    ('th', 'Thai'),
    ('tr', 'Turkish'),
    ('tk', 'Turkmen'),
    ('uk', 'Ukrainian'),
    ('ur', 'Urdu'),
    ('ug', 'Uyghur'),
    ('uz', 'Uzbek'),
    ('vi', 'Vietnamese'),
    ('cy', 'Welsh'),
    ('xh', 'Xhosa'),
    ('yi', 'Yiddish'),
    ('yo', 'Yoruba'),
    ('zu', 'Zulu'),
)


class TranslationForm(forms.Form):
    lang_from = forms.ChoiceField(label=False)
    lang_to = forms.ChoiceField(label=False)

    class Meta:
        fields = ['lang_from', 'lang_to']

    def __init__(self, *args, **kwargs):
        translation_service = kwargs.pop('translation_service')
        super(TranslationForm, self).__init__(*args, **kwargs)
        if translation_service == '':
            self.fields['lang_from'].choices = DEEPL_LANGUAGES
            self.fields['lang_to'].choices = DEEPL_LANGUAGES
        else:
            self.fields['lang_from'].choices = GOOGLE_LANGUAGES
            self.fields['lang_to'].choices = GOOGLE_LANGUAGES
