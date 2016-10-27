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
        xmlfile = os.path.join(
            settings.XMLTV,
            '{0}_{1}'.format(service_id, day)
            )
        with open(xmlfile+'.xml', 'w') as f:
            f.write(xmltodict.unparse(xml))
    cmd = "python /usr/local/share/dvb/nemo/manage.py collectstatic --noinput"
    subprocess.call(shlex.split(cmd))


@login_required
def index(request):
    """displays home page of the app"""
    context = {
        'view': 'index',
        'all_channels': CHANNELS,
        'all_towns': TOWNS,
        'cluster': dvbboxes.CLUSTER,
        }
    return render(request, 'dvbboxes.html', context)


@login_required
def media(request, **kwargs):
    """view for managing media files throughout the cluster"""
    filename = kwargs.get('filename', '')
    context = {
        'view': 'media',
        'all_towns': TOWNS,
        'method': request.method,
        'filename': filename,
        'actions': [
            'media_search',
            'media_display',
            ],
        }
    if 'media/delete' in request.path:
        if request.method == 'GET':
            return redirect('django_dvbboxes:index')
        elif request.method == 'POST':
            if filename:
                for _, servers in dvbboxes.CLUSTER.items():
                    for server in servers:
                        cmd = ("ssh {server} dvbbox media {name} "
                               "--delete").format(
                                   server=server,
                                   name=filename)
                        subprocess.Popen(shlex.split(cmd))
                return redirect('django_dvbboxes:media_infos',
                                filename=filename)
            else:
                form = forms.DeleteBatchMediaForm(request.POST)
                if form.is_valid():
                    filepath = handle_uploaded_file(request.FILES['file'])
                    towns = form.cleaned_data['towns']
                    if not towns:
                        towns = TOWNS
                    towns.sort()
                    with open(filepath) as infile:
                        for line in infile:
                            line = line.replace('\n', '')
                            if line:
                                for town in towns:
                                    for server in dvbboxes.CLUSTER[town]:
                                        cmd = ("ssh {server} dvbbox media "
                                               "{name} --delete").format(
                                                   server=server,
                                                   name=line)
                                        subprocess.Popen(shlex.split(cmd))
                    return redirect('django_dvbboxes:index')
                else:
                    context['errors'] = form.errors
                    return render(request, 'dvbboxes.html', context)
    elif 'media/rename' in request.path:
        if request.method == 'GET':
            return redirect('django_dvbboxes:index')
        elif request.method == 'POST':
            form = forms.RenameMediaForm(request.POST)
            if form.is_valid():
                new_name = form.cleaned_data['name']
                new_name = new_name.lower().replace(' ', '_')
                if not new_name.endswith('.ts'):
                    new_name += '.ts'
                for _, servers in dvbboxes.CLUSTER.items():
                    for server in servers:
                        cmd = ("ssh {server} dvbbox media {name} "
                               "--rename {new_name}").format(
                                   server=server,
                                   name=filename,
                                   new_name=new_name
                                   )
                        subprocess.Popen(shlex.split(cmd))
                return redirect('django_dvbboxes:media_infos',
                                filename=new_name.rstrip('.ts'))
            else:
                context['errors'] = form.errors
                return render(request, 'dvbboxes.html', context)
    elif 'media/search' in request.path:
        if request.method == 'GET':
            return redirect('django_dvbboxes:index')
        elif request.method == 'POST':
            form = forms.SearchMediaForm(request.POST)
            if form.is_valid():
                context['action'] = 'media_search'
                expression = form.cleaned_data['expression']
                expression = expression.lower().replace(' ', '_')
                expression = expression.rstrip('.ts')
                towns = request.POST.getlist('towns')
                towns.sort()
                if not towns:
                    towns = TOWNS
                context['towns'] = towns
                answer = dvbboxes.Media.search(expression, towns)
                for filename in answer:
                    try:
                        models.Media.objects.get(filename=filename)
                    except models.Media.DoesNotExist:
                        # the file exists in the cluster but not in db
                        mediaobject = models.Media(
                            name=createtitle(filename),
                            filename=filename,
                            desc=''
                            )
                        mediaobject.save()
                context['answer'] = sorted(
                    [i.rstrip('.ts') for i in answer]
                    )
                return render(request, 'dvbboxes.html', context)
            else:
                context['errors'] = form.errors
                return render(request, 'dvbboxes.html', context)
    else:
        filename += '.ts'
        # display filename informations
        answer = {}
        try:
            mediaobject = models.Media.objects.get(filename=filename)
        except models.Media.DoesNotExist:
            mediaobject = models.Media(
                name=createtitle(filename),
                filename=filename,
                desc=''
                )
            mediaobject.save()
        if request.method == 'POST':
            form = forms.MediaInfosForm(request.POST)
            if form.is_valid():
                context['action'] = 'media_display'
                name = form.cleaned_data['name']
                desc = form.cleaned_data['desc']
                sem = False
                if name != mediaobject.name:
                    mediaobject.name = name
                    sem = True
                if desc != mediaobject.desc:
                    mediaobject.desc = desc
                    sem = True
                if sem:
                    mediaobject.save()
                return redirect('django_dvbboxes:media_infos_',
                                filename=filename)
            else:
                context['errors'] = form.errors
                return render(request, 'dvbboxes.html', context)
        else:
            context['db'] = mediaobject
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
        return redirect('django_dvbboxes:index')
    elif request.method == 'POST':
        if 'listing/apply' in request.path:
            form = forms.ApplyListingForm(request.POST)
            if form.is_valid():
                context['action'] = 'listing_apply'
                parsed_data = json.loads(form.cleaned_data['parsed_data'])
                service_id = form.cleaned_data['service_id']
                towns = request.POST.getlist('towns')
                towns.sort()
                # apply listing to servers in towns
                dvbboxes.Listing.apply(parsed_data, service_id, towns)
                # create xml files
                buildxml(parsed_data, service_id)
                return redirect('django_dvbboxes:index')
            else:
                context['errors'] = form.errors
                return render(request, 'dvbboxes.html', context)
        else:
            context['action'] = 'listing_parse'
            form = forms.UploadListingForm(request.POST)
            if form.is_valid():
                filepath = handle_uploaded_file(request.FILES['filename'])
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
            # else:
            #     context['errors'] = form.errors
            #     return render(request, 'dvbboxes.html', context)


@login_required
def program(request, **kwargs):
    """view for managing programs"""
    context = {
        'view': 'program',
        'all_channels': CHANNELS,
        'all_towns': TOWNS,
        'method': request.method,
        'actions': ['program_display'],
        }
    if request.method == 'GET':
        return redirect('django_dvbboxes:index')
    elif request.method == 'POST':
        form = forms.ProgramForm(request.POST)
        if form.is_valid():
            towns = form.cleaned_data['towns']
            if not towns:
                towns = TOWNS
            towns.sort()
            date = form.cleaned_data['date']
            service_id = form.cleaned_data['service_id']
            try:
                program = dvbboxes.Program(date, service_id)
            except ValueError:
                context['errors'] = "{} est une date incorrecte".format(date)
                return render(request, 'dvbboxes.html', context)
            context['action'] = 'program_display'
            infos = program.infos(towns)
            result = collections.OrderedDict()
            parsed_data = {'day': date}
            for _, start in infos:
                filename, index = _.split(':')
                media = dvbboxes.Media(filename)
                duration = media.duration
                parsed_data[str(start)+'_'+index] = {
                    'filename': filename,
                    'duration': duration
                    }
                missing_towns = [i for i in towns if i not in media.towns]
                result[index] = [
                    datetime.fromtimestamp(start).strftime('%H:%M:%S'),
                    datetime.fromtimestamp(
                        start+duration).strftime('%H:%M:%S'),
                    filename.rstrip('.ts'),
                    ', '.join(missing_towns),
                    duration
                    ]
            xmlfile = '{0}_{1}'.format(service_id, date)
            if xmlfile+'.xml' not in os.listdir(settings.XMLTV):
                buildxml([parsed_data], service_id)
            context['result'] = result
            context['date'] = date
            context['xmlfile'] = xmlfile
            context['channel'] = CHANNELS[int(service_id)]
            return render(request, 'dvbboxes.html', context)
        else:
            context['errors'] = form.errors
            return render(request, 'dvbboxes.html', context)
