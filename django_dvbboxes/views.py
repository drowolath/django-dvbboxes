# encoding: utf-8

import collections
import dvbboxes
import json
import os
import shlex
import string
import subprocess
import xmltodict
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from . import forms, models

TOWNS = dvbboxes.TOWNS
TOWNS.sort()

CHANNELS = collections.OrderedDict()
for i in sorted(dvbboxes.CHANNELS):
    CHANNELS[int(i)] = dvbboxes.CHANNELS[i]


def handle_uploaded_file(f):
    path = os.path.join('', f.name)
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return path


def build_tmira_datetime(dt):
    u"""le format d'entrée est %d-%m-%Y %H:%M:%S"""
    date, hour = dt.split()
    day, month, year = date.split('-')
    result = '{year}-{month}-{day}T{hour}+03:00'.format(
        hour=hour, year=year, month=month, day=day)
    return result


def createtitle(name):
    """create title out of filename"""
    name = name
    if name.endswith('.ts'):
        name = name[:-3]
    header = name
    name = header.replace('_', ' ').title()
    letters = [
        i for i in string.letters[26:]
        if i not in ['A', 'E', 'I', 'O']
        ]
    for letter in letters:
        if ' '+letter+' ' in name:
            name = name.replace(letter+' ', letter+"'")
    bar = [i for i in name.split("'")[:-1] if len(i) > 1]
    for j in bar:
        name = name.replace(j+"'", j+" ")
    if name.startswith('Ba '):
        name = name.replace('Ba ', 'Bande Annonce ')
    else:
        name = name.replace(' Ctv4', '')
        name = name.replace(' Ctv3', '')
        name = name.replace(' Ctv2', '')
        name = name.replace(' Ctv', '')
    return name


def buildxml(parsed_data, service_id):
    """create xml files for epg"""
    for data in parsed_data:
        day = data['day']
        del data['day']
        keys = sorted(data, key=lambda x: int(x.split('_')[1]))
        xml = {
            'BroadcastData': {
                'ProviderInfo': {
                    'ProviderId': '',
                    'ProviderName': '',
                    },
                'ScheduleData': {
                    'ChannelPeriod': {
                        'ChannelId': service_id,
                        'Event': [],
                        },
                    },
                },
            }
        channelperiod = xml['BroadcastData']['ScheduleData']
        channelperiod = channelperiod['ChannelPeriod']
        for key in keys:
            timestamp, index = key.split('_')
            info = data[key]
            filename = info['filename']
            if not filename.endswith('.ts'):
                filename += '.ts'
            if not filename.startswith('ba_'):
                media = models.Media.objects.filter(
                    filename__startswith=filename)
                if media:
                    media = media.first()
                    name = media.name
                    desc = media.desc
                else:
                    desc = ''
                    name = createtitle(filename)
                if '@beginTime' not in channelperiod:
                    channelperiod['@beginTime'] = build_tmira_datetime(
                        datetime.fromtimestamp(
                            float(timestamp)).strftime('%d-%m-%Y %H:%M:%S'))
                event = {
                    '@duration': str(info['duration']),
                    '@beginTime': build_tmira_datetime(
                        datetime.fromtimestamp(
                            float(timestamp)).strftime('%d-%m-%Y %H:%M:%S')),
                    'EventType': 'S',
                    'FreeAccess': '1',
                    'Unscrambled': '1',
                    'EpgProduction': {
                        'ParentalRating': {
                            '@countryCode': "MDG",
                            '#text': '0',
                            },
                        'DvbContent': {
                            'Content': {
                                '@nibble2': '0',
                                '@nibble1': '0',
                                },
                            },
                        'EpgText': {
                            '@language': 'fre',
                            'ShortDescription': '',
                            'Description': desc,
                            'Name': name,
                            },
                        },
                    }
                channelperiod['Event'].append(event)
        else:
            channelperiod['@endTime'] = build_tmira_datetime(
                datetime.fromtimestamp(
                    float(timestamp)).strftime('%d-%m-%Y %H:%M:%S'))
        folder = [
            i[-1] for i in settings.STATICFILES_DIRS if i[0] == 'xml'
            ]
        folder = folder.pop()
        xmlfile = os.path.join(folder, '{0}_{1}'.format(service_id, day))
        with open(xmlfile+'.xml', 'w') as f:
            f.write(xmltodict.unparse(xml))
    cmd = ("python /usr/local/share/dvb/nemo/manage.py "
           "collectstatic --noinput")
    subprocess.call(shlex.split(cmd))


@login_required
def index(request):
    """displays home page of the app"""
    context = {
        'view': 'index',
        'all_channels': CHANNELS,
        'all_towns': TOWNS,
        }
    return render(request, 'dvbboxes.html', context)


@login_required
def media(request, **kwargs):
    """view for managing media files throughout the cluster"""
    filename = kwargs.get('filename', '')
    town = kwargs.get('town', '')
    context = {
        'view': 'media',
        'all_towns': TOWNS,
        'method': request.method,
        'filename': filename,
        'town': town,
        'actions': [
            'media_search',
            'media_display',
            'media_rename',
            'media_delete'
            ],
        }
    if 'delete' in request.path:
        context['action'] = 'media_delete'
        if request.method == 'GET':
            # If no filename's provided nor towns,
            # the form will be an UploadFileForm (POST media_delete).
            # If no town is provided, it will ask to choose a town
            # (POST media_delete filename=x)
            # If both filename and town are provided it'll ask confirmation.
            # Confirmation issues a POST.
            if not filename and not town:
                context['upload'] = True
            return render(request, 'dvbboxes.html', context)
        elif request.method == 'POST':
            if not filename and not town:
                form = forms.UploadFileForm(request.POST)
                if form.is_valid():
                    filepath = handle_uploaded_file(request.FILES['file'])
                    towns = form.cleaned_data['towns']
                    if towns.sort() == TOWNS:
                        towns = None
                    context['towns'] = towns
                    answer = {}
                    # for each entry in the file, issue a delete to each town
                    with open(filepath) as infile:
                        for line in infile:
                            line = line.replace('\n', '')
                            answer[line] = {}
                            if not towns:
                                result = dvbboxes._media(
                                    line, town=None, delete=True
                                    )
                                for info in result:
                                    server, response = info
                                    response = response.json()['result']
                                    answer[line][server.fqdn] = response
                            else:
                                for town in towns:
                                    result = dvbboxes._media(
                                        line, town=town, delete=True
                                        )
                                    for info in result:
                                        server, response = info
                                        response = response.json()['result']
                                        answer[line][server.fqdn] = response
                    context['answer'] = answer
                    return render(request, 'dvbboxes.html', context)
            elif filename and town:
                if town not in TOWNS:
                    raise Http404(
                        "There is no dvbbox instance in {}".format(town)
                        )
                else:
                    answer = {filename: {}}
                    result = dvbboxes._media(
                        filename, town=town, delete=True
                        )
                    for info in result:
                        server, response = info
                        response = response.json()
                        answer[filename][server.fqdn] = response['result']
                    context['answer'] = answer
                    return render(request, 'dvbboxes.html', context)
            elif filename and not town:
                form = forms.ChooseTownForm(request.POST)
                if form.is_valid():
                    towns = form.cleaned_data['towns']
                    if towns.sort() == TOWNS:
                        towns = None
                    context['towns'] = towns
                    answer = {filename: {}}
                    if not towns:
                        result = dvbboxes._media(
                            line, town=None, delete=True
                            )
                        for info in result:
                            server, response = info
                            response = response.json()
                            answer[filename][server.fqdn] = response['result']
                    else:
                        for town in towns:
                            result = dvbboxes._media(
                                line, town=town, delete=True
                                )
                            for info in result:
                                server, response = info
                                response = response.json()['result']
                                answer[filename][server.fqdn] = response
                    context['answer'] = answer
                    return render(request, 'dvbboxes.html', context)
            else:
                raise Http404("this ressource does not exist")
    elif 'media/rename' in request.path:
        context['action'] = 'media_rename'
        if request.method == 'GET':
            if not filename:
                raise Http404("this ressource does not exist")
            else:
                return render(request, 'dvbboxes.html', context)
        elif request.method == 'POST':
            form = forms.StandardForm(request.POST)
            if form.is_valid():
                expression = form.cleaned_data['expression']
                expression = expression.lower().replace(' ', '_')
                if not town:
                    towns = form.cleaned_data['towns']
                    if towns.sort() == TOWNS:
                        towns = None
                    context['towns'] = towns
                    if not towns:
                        result = dvbboxes._media(
                            filename,
                            town=None,
                            rename=expression)
                    else:
                        for town in towns:
                            result = dvbboxes._media(
                                filename,
                                town=town,
                                rename=expression
                                )
                else:
                    result = dvbboxes._media(
                        filename,
                        town=town,
                        rename=expression
                        )
                return redirect('media', filename=expression)
    elif 'media/search' in request.path:
        context['action'] = 'media_search'
        if request.method == 'GET':
            return redirect('index')
        elif request.method == 'POST':
            form = forms.SearchMediaForm(request.POST)
            if form.is_valid():
                expression = form.cleaned_data['expression']
                expression = expression.lower().replace(' ', '_')
                towns = request.POST.getlist('towns')
                towns.sort()
                if not towns:
                    towns = TOWNS
                context['towns'] = towns
                answer = dvbboxes.Media.search(expression, towns)
                context['answer'] = sorted(
                    [i.rstrip('.ts') for i in answer]
                    )
                return render(request, 'dvbboxes.html', context)
    else:
        context['action'] = 'media_display'
        # display filename informations
        town = kwargs.get('town', '')
        context['town'] = town
        answer = {}
        result = dvbboxes.Media(filename)
        duration = result.duration
        towns = list(result.towns)
        towns.sort()
        answer['towns'] = towns or context['all_towns']
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        duration = "%02d:%02d:%02d\n" % (hours, minutes, seconds)
        answer['duration'] = duration
        schedule = {}
        for service_id, timestamps in result.schedule.items():
            timestamps = sorted(list(timestamps))
            timestamps.sort()
            schedule[service_id] = [
                datetime.fromtimestamp(timestamp).strftime(
                    dvbboxes.CONFIG.get('LOG', 'datefmt'))
                for timestamp in timestamps
                ]
        answer['schedule'] = schedule
        context['answer'] = answer
        return render(request, 'dvbboxes.html', context)


@login_required
def listing(request, **kwargs):
    """view for processing and applying listings"""
    context = {
        'view': 'listing',
        'all_channels': CHANNELS,
        'all_towns': TOWNS,
        'method': request.method,
        'actions': ['listing_parse', 'listing_apply'],
        }
    if request.method == 'GET':
        return redirect('index')
    elif request.method == 'POST':
        if 'listing/apply' in request.path:
            context['action'] = 'listing_apply'
            form = forms.ApplyListingForm(request.POST)
            form.is_valid()
            parsed_data = json.loads(form.cleaned_data['parsed_data'])
            service_id = form.cleaned_data['service_id']
            towns = request.POST.getlist('towns')
            towns.sort()
            # apply listing to servers in towns
            dvbboxes.Listing.apply(parsed_data, service_id, towns)
            # create xml files
            buildxml(parsed_data, service_id)
            return redirect('index')
        else:
            context['action'] = 'listing_parse'
            form = forms.UploadListingForm(request.POST)
            form.is_valid()
            filepath = handle_uploaded_file(request.FILES['file'])
            listing = dvbboxes.Listing(filepath)  # get listing object
            days = sorted(
                listing.days,
                key=lambda x: datetime.strptime(x, '%d%m%Y')
                )  # sort days in the listing
            missing_files = [
                i for i, j in listing.filenames.items() if not j
                ]  # detect missing files in the listing
            result = collections.OrderedDict()  # prepare final result
            for day in days:
                result[day] = []
            parsed_listing = listing.parse()
            json_result = []
            for data in parsed_listing:
                infos = collections.OrderedDict()
                data = json.loads(data)
                json_result.append(data)
                day = data['day']
                del data['day']
                starts = sorted(data, key=lambda x: float(x.split('_')[1]))
                absent_files = 0
                for start in starts:
                    t, i = start.split('_')
                    start_litteral = datetime.fromtimestamp(
                        float(t)).strftime('%H:%M:%S')
                    stop_litteral = datetime.fromtimestamp(
                        float(t)+data[start]['duration']).strftime(
                            '%d-%m-%Y %H:%M:%S')
                    absent = not data[start]['duration']
                    if absent:
                        absent_files += 1
                    filename = data[start]['filename']
                    infos[i] = [
                        start_litteral, filename, absent
                        ]
                # we now define if the parsing is fine
                limit = datetime.strptime(day, '%d%m%Y') + timedelta(1)
                length_ok = (
                    datetime.fromtimestamp(
                        float(t)+data[start]['duration']) >= limit
                    )
                if not absent_files and length_ok:
                    success = 0  # green
                elif absent_files and length_ok:
                    success = 1  # lightblue
                elif not absent_files and not length_ok:
                    success = 2  # orange
                else:
                    success = 3  # red
                result[day] = [infos, success, stop_litteral]
            context['days'] = days
            context['missing_files'] = missing_files
            context['result'] = result
            context['json_result'] = json.dumps(json_result)
            return render(request, 'dvbboxes.html', context)


@login_required
def program(request, **kwargs):
    """view for gettings programs"""
    context = {
        'view': 'program',
        'all_channels': CHANNELS,
        'all_towns': TOWNS,
        'method': request.method,
        'actions': ['program', 'showresult'],
        }
    if request.method == 'GET':
        context['action'] = 'program'
        return render(request, 'dvbboxes.html', context)
    elif request.method == 'POST':
        towns = request.POST.getlist('towns')
        towns.sort()
        date = request.POST['date']
        action = request.POST['action']
        service_id = request.POST['service_id']
        data = {
            'delete': False,
            'check': False,
            'service_id': service_id,
            }
        context['action'] = 'showresult'
        answer = []
        if action in data:
            data[action] = True
        if towns == TOWNS or not towns:
            dvbboxes_program = dvbboxes._program(date, town=None, **data)
            for server, data in dvbboxes_program.items():
                answer.append({
                    'name': server.split('.')[0].replace('-', '_'),
                    'id': server.split('.')[0].replace('-', ''),
                    'server': server,
                    'data': data['data'] or {
                        service_id: "HTTP {}".format(data['status'])
                        }
                    })
        else:
            for town in towns:
                dvbboxes_program = dvbboxes._program(date, town=town, **data)
                for server, data in dvbboxes_program.items():
                    answer.append({
                        'name': server.split('.')[0].replace('-', '_'),
                        'id': server.split('.')[0].replace('-', ''),
                        'server': server,
                        'data': data['data'] or {
                            service_id: "HTTP {}".format(data['status'])
                            }
                        })
        context['answer'] = answer
        return render(request, 'dvbboxes.html', context)
