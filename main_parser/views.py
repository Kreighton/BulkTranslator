import re
import itertools
import tldextract
from googletrans import Translator
import pydeepl
import requests
import lxml
from bs4 import BeautifulSoup as bs
import validators

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

from requests.exceptions import ConnectionError as ReqConnectionError

from rest_framework import generics

from . import models, serializers, forms

from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions, Chrome
from selenium.common.exceptions import InvalidArgumentException, InvalidSelectorException


class SelectorsList(generics.ListCreateAPIView):
    queryset = models.UserDomainSelectors.objects.all()
    serializer_class = serializers.SelectorsSerializer


class SelectorsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.UserDomainSelectors.objects.all()
    serializer_class = serializers.SelectorsSerializer


@login_required
def account(request):
    context = {
        'user_data': request.user
    }
    return render(request, 'main_parser/account.html', context)


@login_required
def add_selector(request):
    if request.method == 'POST':
        form = forms.AddSelectorForm(request.POST, username=request.user)
        if form.is_valid():
            new_selector = models.UserDomainSelectors(
                user=request.user,
                domain_for_selector=form.cleaned_data['domain_for_selector'],
                selector_type=form.cleaned_data['selector_type'],
                user_selector=form.cleaned_data['selector'],
            )
            new_selector.save()
            return redirect('main')
        else:
            context = {
                'form': form
            }
            return render(request, 'main_parser/add_selector.html', context)
    form = forms.AddSelectorForm(username=request.user)
    context = {
        'form': form
    }
    return render(request, 'main_parser/add_selector.html', context)


@login_required
def edit_selector(request, slug):
    current_selector = models.UserDomainSelectors.objects.get(domain_for_selector=slug)
    if request.method == 'POST':
        form = forms.EditSelectorForm(
            request.POST,
            instance=current_selector,
            domain_for_selector=current_selector.domain_for_selector,
            selector_type=current_selector.selector_type,
            user_selector=current_selector.user_selector,
        )
        if form.is_valid():
            form.save()
            return redirect('user_selectors')

    form = forms.EditSelectorForm(
        instance=current_selector,
        domain_for_selector=current_selector.domain_for_selector,
        selector_type=current_selector.selector_type,
        user_selector=current_selector.user_selector,
    )
    context = {
        'form': form
    }
    return render(request, 'main_parser/edit_selector.html', context)


@login_required
def user_selectors(request):
    user_selectors_list = models.UserDomainSelectors.objects.filter(user=request.user)
    context = {
        'user_selectors_list': user_selectors_list
    }
    return render(request, 'main_parser/review_user_selectors.html', context)


def custom_parse(request):
    # File different errors
    request.session['errors'] = ''
    if request.method == 'POST':
        form = forms.CustomParserForm(request.POST)
        if form.is_valid():
            valid_urls_list = {}
            r = re.compile(r'^(?:http|ftp)s?://'
                           r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
                           r'localhost|'
                           r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
                           r'(?::\d+)?'
                           r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            start_urls_list = list(filter(r.match, form.cleaned_data['urls_field'].split('\r\n')))
            for every_url in start_urls_list:
                try:
                    temp_url_request = requests.get(every_url)
                except ReqConnectionError:
                    continue
                if temp_url_request.status_code == 200:
                    if every_url not in valid_urls_list.items():
                        if request.user.is_authenticated:
                            try:
                                temp_domain = f'{tldextract.extract(every_url).domain}.{tldextract.extract(every_url).suffix}'
                                if models.UserDomainSelectors.objects.filter(user=request.user).get(domain_for_selector=temp_domain):
                                    valid_urls_list[every_url] = '1'
                                else:
                                    raise ObjectDoesNotExist
                            except ObjectDoesNotExist:
                                valid_urls_list[every_url] = ''
                        else:
                            valid_urls_list[every_url] = ''
            if request.user.is_authenticated:
                request.session['valid_urls_list'] = dict(itertools.islice(valid_urls_list.items(), 100))
            else:
                request.session['valid_urls_list'] = dict(itertools.islice(valid_urls_list.items(), 20))
            return redirect('custom_selectors')
    form = forms.CustomParserForm()
    context = {
        'form': form
    }
    if request.session.get('valid_urls_list'):
        context['valid_urls_list'] = request.session.get('valid_urls_list')
    return render(request, 'main_parser/parse.html', context)


def custom_selectors(request):
    if request.session.get('valid_urls_list'):
        valid_urls_list = request.session.get('valid_urls_list')
        if request.method == 'POST':
            if 'set_with_google' in request.POST:
                request.session['translation_service'] = 'google'
            elif 'set_with_deepl' in request.POST:
                request.session['translation_service'] = 'deepl'

            form = forms.ChooseSelectorsForm(request.POST)
            if form.is_valid():
                urls_list = [(i, request.POST.get(f'whitelist_{i}')) for i in list(valid_urls_list.keys())]
                list_of_articles = parse_selector_custom(
                    request.POST.getlist('type_of_selector'),
                    request.POST.getlist('custom_selector'),
                    urls_list
                )
                request.session['list_of_articles'] = list_of_articles
                return redirect('custom_translate')

        form = forms.ChooseSelectorsForm()
        context = {
            'form': form,
            'valid_urls_list': valid_urls_list,
        }
        return render(request, 'main_parser/selectors.html', context)
    return redirect('main')


def parse_selector_custom(types, selectors, urls_list):
    chrome_profile_path = ''
    PATH = 'main_parser/driver/chromedriver.exe'
    articles_list = []
    default_selector_parsed_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'p']

    options = ChromeOptions()
    options.headless = True
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')
    options.add_argument('--incognito')

    wd = Chrome(options=options, executable_path=PATH)

    for item in range(len(urls_list)):
        article = ''
        url = urls_list[item][0]
        wd.get(url)
        try:
            if urls_list[item][1] == 'on':
                temp_domain = f'{tldextract.extract(url).domain}.{tldextract.extract(url).suffix}'
                whitelist_selector = models.UserDomainSelectors.objects.get(domain_for_selector=temp_domain)
                types[item] = whitelist_selector.selector_type
                selectors[item] = whitelist_selector.user_selector
            if types[item] == 'XPath':
                for data in wd.find_elements(By.XPATH, selectors[item]):
                    article += f'{data.text}\n'
            elif types[item] == 'CSS':
                for data in wd.find_elements(By.CSS_SELECTOR, selectors[item]):
                    article += f'{data.text}\n'
            elif types[item] == 'Default':
                soup = bs(requests.get(url).text, 'lxml')
                for data in soup.find_all(default_selector_parsed_tags):
                    article += f'{data.text}\n'
            print(article)
        except InvalidArgumentException:
            # request.session['errors']
            print('bad selector')
        except InvalidSelectorException:
            # request.session['errors']
            print('bad selector')
        articles_list.append(article)
    return articles_list


def custom_translate(request):
    if request.session.get('translation_service'):
        translation_service = request.session.get('translation_service')
        if request.method == 'POST':
            form = forms.TranslationForm(request.POST, translation_service=translation_service)
            # if Google
            if form.is_valid():
                if translation_service == 'google':
                    src = form.cleaned_data['lang_from']
                    dest = form.cleaned_data['lang_to']
                    list_of_articles = request.session['list_of_articles']
                    translator = Translator()
                    for item in list_of_articles:
                        for chunk in item.split('\n'):
                            if not chunk:
                                continue
                            a = translator.translate(chunk, src=src, dest=dest)
                            print(a.text)
                # if Deepl
                else:
                    pass

        form = forms.TranslationForm(translation_service=translation_service)
        context = {
            'form': form
        }
        return render(request, 'main_parser/translate.html', context)
    return redirect('main')


def result(request):
    if request.session.get('list_of_articles'):
        context = {
            'list_of_articles': request.session.get('list_of_articles'),
        }
        return render(request, 'main_parser/result.html', context)
    return redirect('main')


