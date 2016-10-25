# encoding: utf-8

import collections
import dvbboxes
import json
import os
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from . import forms

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
        'actions': ['listing_parse', 'listing_apply', 'listing_showresult'],
        }
    if request.method == 'GET':
        return redirect('index')
    elif request.method == 'POST':
        if 'listing/apply' in request.path:
            return render(request, 'dvbboxes.html', context)
        else:
            context['action'] = 'listing_parse'
            form = forms.UploadListingForm(request.POST)
            form.is_valid()
            filepath = handle_uploaded_file(request.FILES['file'])
            listing = dvbboxes.Listing(filepath)
            days = sorted(
                listing.days,
                key=lambda x: datetime.strptime(x, '%d%m%Y')
                )
            missing_files = [
                i for i, j in listing.filenames.items() if not j
                ]
            result = collections.OrderedDict()
            for day in days:
                result[day] = {}
            parsed_listing = listing.parse()
            for data in parsed_listing:
                data = json.loads(data)
                day = data['day']
                del data['day']
                starts = sorted(data)
                for start in starts:
                    result[day][data[start]['filename']] = [
                        datetime.fromtimestamp(
                            float(start)).strftime('%H:%M:%S'),
                        datetime.fromtimestamp(
                            float(start)+data[start]['duration']).strftime(
                                '%H:%M:%S'),
                        not data[start]['duration']
                        ]
            context['days'] = days
            context['missing_files'] = missing_files
            context['result'] = result
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
