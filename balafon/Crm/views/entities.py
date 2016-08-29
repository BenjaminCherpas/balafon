# -*- coding: utf-8 -*-
"""view and edit entities"""

from datetime import date
import hashlib
import json
import os
import re
import urllib
import urllib2

from django.contrib.auth.decorators import user_passes_test
from django.contrib.messages import warning
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django import template
from django.utils.safestring import mark_safe
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _

from coop_cms.utils import paginate
from colorbox.decorators import popup_redirect

from balafon.Crm import models, forms
from balafon.Crm.utils import get_actions_by_set
from balafon.Crm.settings import is_unaccent_filter_supported
from balafon.permissions import can_access
from balafon.utils import log_error


@user_passes_test(can_access)
def get_entity_name(request, entity_id):
    """view"""
    try:
        entity = models.Entity.objects.get(id=entity_id)
        return HttpResponse(json.dumps({'name': entity.name}), 'application/json')
    except models.Entity.DoesNotExist:
        return HttpResponse(json.dumps({'name': entity_id}), 'application/json')


@user_passes_test(can_access)
def get_entities(request):
    """view"""
    term = request.GET.get('term')
    entities = [
        {'id': x.id, 'name': x.name}
        for x in models.Entity.objects.filter(name__icontains=term)
    ]
    return HttpResponse(json.dumps(entities), 'application/json')


@user_passes_test(can_access)
@log_error
def get_entity_id(request):
    """view"""
    name = request.GET.get('name', '')
    if name:
        try:
            entity = get_object_or_404(models.Entity, name=name)
        except models.Entity.MultipleObjectsReturned:
            warning(request, _(u'Duplicate entities {0}').format(name))
            raise Http404
        return HttpResponse(json.dumps({'id': entity.id}), 'application/json')
    raise Http404


@user_passes_test(can_access)
def view_entity(request, entity_id):
    """view"""

    try:
        preview = bool(request.GET.get('preview', False))
    except ValueError:
        preview = False

    entity = get_object_or_404(models.Entity, id=entity_id)
    contacts = entity.contact_set.all().order_by("has_left", "-main_contact", "lastname", "firstname")

    actions = models.Action.objects.filter(
        Q(entities=entity) | Q(contacts__entity=entity), Q(archived=False)
    ).distinct().order_by("planned_date", "priority")

    actions_by_set = get_actions_by_set(actions, 5)

    multi_user = True
    request.session["redirect_url"] = reverse('crm_view_entity', args=[entity_id])

    context = {
        "entity": entity,
        'contacts': contacts,
        'actions_by_set': actions_by_set,
        'multi_user': multi_user,
        'preview': preview,
        'template_base': "balafon/bs_base.html" if not preview else "balafon/bs_base_raw.html"
    }

    return render(
        request,
        'Crm/entity.html',
        context
    )


@user_passes_test(can_access)
def view_entities_list(request):
    """view"""
    letter_filter = request.GET.get("filter", "*")

    queryset = models.Entity.objects.all()
    if re.search(r"\w+", letter_filter):
        if is_unaccent_filter_supported():
            queryset = queryset.extra(
                where=[u"UPPER(unaccent(name)) LIKE UPPER(unaccent(%s))"],
                params=[u"{0}%".format(letter_filter)]
            )
        else:
            queryset = queryset.filter(name__istartswith=letter_filter)
    elif letter_filter == "~":
        queryset = queryset.filter(name__regex=r'^\W|^\d')

    queryset = queryset.extra(select={'lower_name':'lower(name)'}).order_by('lower_name')

    page_obj = paginate(request, queryset, 50)

    entities = list(page_obj)

    return render(
        request,
        'Crm/all_entities.html',
        {
            'entities': entities,
            'letter_filter': letter_filter,
            'page_obj': page_obj,
        }
    )


@user_passes_test(can_access)
@popup_redirect
def change_contact_entity(request, contact_id):
    """view"""
    try:
        contact = get_object_or_404(models.Contact, id=contact_id)

        if request.method == "POST":
            form = forms.ChangeContactEntityForm(contact, request.POST)
            if form.is_valid():
                form.change_entity()
                next_url = reverse('crm_view_contact', args=[contact_id])
                return HttpResponseRedirect(next_url)
        else:
            form = forms.ChangeContactEntityForm(contact)

        context_dict = {
            'contact': contact,
            'form': form,
        }

        return render(
            request,
            'Crm/change_contact_entity.html',
            context_dict
        )
    except Exception as msg:
        print "#ERR", msg
        raise



@user_passes_test(can_access)
@popup_redirect
def edit_entity(request, entity_id):
    """view"""
    entity = get_object_or_404(models.Entity, id=entity_id)
    #update last access
    entity.save()
    if request.method == "POST":
        form = forms.EntityForm(request.POST, request.FILES, instance=entity)
        if form.is_valid():
            entity = form.save()
            return HttpResponseRedirect(reverse('crm_view_entity', args=[entity.id]))
    else:
        form = forms.EntityForm(instance=entity)

    return render(
        request,
        'Crm/edit_entity.html',
        locals()
    )


@user_passes_test(can_access)
@popup_redirect
def create_entity(request, entity_type_id):
    """view"""
    try:
        entity_type_id = int(entity_type_id)
    except ValueError:
        raise Http404
    if entity_type_id:
        entity_type = get_object_or_404(models.EntityType, id=entity_type_id)
        entity = models.Entity(type=entity_type)
    else:
        entity = models.Entity()

    if request.method == "POST":
        form = forms.EntityForm(request.POST, request.FILES, instance=entity)
        if form.is_valid():
            entity = form.save()
            return HttpResponseRedirect(reverse('crm_view_entity', args=[entity.id]))
    else:
        form = forms.EntityForm(instance=entity, initial={'relationship_date': date.today()})

    return render(
        request,
        'Crm/edit_entity.html',
        {
            'entity': entity,
            'form': form,
            'create_entity': True,
            'entity_type_id': entity_type_id,
        }
    )


@user_passes_test(can_access)
@popup_redirect
def delete_entity(request, entity_id):
    """view"""
    entity = get_object_or_404(models.Entity, id=entity_id)
    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                entity.delete()
                return HttpResponseRedirect(reverse('balafon_homepage'))
            else:
                return HttpResponseRedirect(reverse('crm_edit_entity', args=[entity.id]))
    else:
        form = forms.ConfirmForm()
    return render(
        request,
        'balafon/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Are you sure to delete {0.name}?').format(entity),
            'action_url': reverse("crm_delete_entity", args=[entity_id]),
        }
    )


@user_passes_test(can_access)
def select_entity_and_redirect(request, view_name, template_name):
    """view"""
    if request.method == 'POST':
        form = forms.SelectEntityForm(request.POST)
        if form.is_valid():
            entity = form.cleaned_data["entity"]
            args = [entity.id]
            url = reverse(view_name, args=args)
            return HttpResponseRedirect(url)
    else:
        form = forms.SelectEntityForm()

    return render(
        request,
        template_name,
        {'form': form}
    )


@user_passes_test(can_access)
@popup_redirect
def display_map(request, entity_id):
    entity_type = request.GET.get('type')
    return render(request, 'Crm/display_map.html', {'entity': entity_id, 'type': entity_type})


@user_passes_test(can_access)
def get_addr(request):
    street_type = ["route", "rue", "chemin", "allée".decode('utf8'), "boulevard", "avenue", "place", "impasse", "montée".decode('utf8'), "coursière".decode('utf8'), "lotissement"]
    identity = request.GET.get('term')
    type_ent = request.GET.get('type')
    if type_ent == "e":
        entity = models.Entity.objects.get(id=identity)
    else:
        entity = models.Contact.objects.get(id=identity)
    address = ""
    if entity.city != None:
        latitude = entity.city.latitude
        longitude = entity.city.longitude
        lat = entity.latitude
        lon = entity.longitude
        for stype in street_type:
            if stype in entity.address.lower():
                address = entity.address
            elif stype in entity.address2.lower():
                address = entity.address2
            elif stype in entity.address3.lower():
                address = entity.address3
        if address == "":
            address = entity.address
        city = entity.city.name

    else:
        latitude = entity.entity.city.latitude
        longitude = entity.entity.city.longitude
        lat = entity.entity.latitude
        lon = entity.entity.longitude
        for stype in street_type:
            if stype in entity.entity.address.lower():
                address = entity.entity.address
            elif stype in entity.entity.address2.lower():
                address = entity.entity.address2
            elif stype in entity.entity.address3.lower():
                address = entity.entity.address3
        if address == "":
            address = entity.entity.address
        city = entity.entity.city.name
        
    if type_ent == "e":
        name = entity.name
    else:
        name = entity.lastname + " " + entity.firstname
    
    return HttpResponse(json.dumps({'address': address, 'city': city, 'latitude': latitude, 'longitude': longitude, 'lat': lat, 'lon': lon, 'name': name}), 'application/json')


@user_passes_test(can_access)
def put_coords(request):
    entity_id = request.GET.get('ent')
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    type_ent = request.GET.get('type')
    if type_ent == "e":
        entity = models.Entity.objects.get(id=entity_id)
    else:
        entity = models.Contact.objects.get(id=entity_id)
    entity.latitude = lat
    entity.longitude = lon
    entity.save()
    return HttpResponse(json.dumps({'latitude': lat, 'longitude': lon}), 'application/json')