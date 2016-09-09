# -*- coding: utf-8 -*-
"""opportunities : certainly a bad name :-) this is a group of actions"""

from datetime import datetime
import json

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.text import slugify
from django.utils.translation import ugettext as _

from colorbox.decorators import popup_redirect
from coop_cms.utils import paginate

from balafon.Crm import models, forms
from balafon.Crm.utils import get_actions_by_set
from balafon.generic import XlsExportView
from balafon.permissions import can_access
from balafon.utils import log_error


@user_passes_test(can_access)
@log_error
def get_opportunity_name(request, opp_id):
    """view"""
    try:
        opp = models.Opportunity.objects.get(id=opp_id)
        return HttpResponse(json.dumps({'name': opp.name}), 'application/json')
    except (models.Opportunity.DoesNotExist, ValueError):
        return HttpResponse(json.dumps({'name': opp_id}), 'application/json')


@user_passes_test(can_access)
@log_error
def get_opportunities(request):
    """view"""
    term = request.GET.get('term')
    queryset = models.Opportunity.objects.filter(ended=False, name__icontains=term)
    opportunities = [{'id': opportunity.id, 'name': u'{0}'.format(opportunity.name)} for opportunity in queryset]
    return HttpResponse(json.dumps(opportunities), 'application/json')


@user_passes_test(can_access)
@log_error
def get_opportunity_id(request):
    """view"""
    name = request.GET.get('name')
    opportunity = get_object_or_404(models.Opportunity, name=name)
    return HttpResponse(json.dumps({'id': opportunity.id}), 'application/json')


@user_passes_test(can_access)
def view_all_opportunities(request, ordering=None):
    """view"""
    opportunities = models.Opportunity.objects.all()
    if not ordering:
        ordering = 'date'
    if ordering == 'name':
        opportunities = opportunities.order_by(['ended', 'name'])
    elif ordering == 'date':
        opportunities = list(opportunities)
        opportunities.sort(key=lambda opp: (not opp.ended, opp.get_start_date() or datetime(1970, 1, 1)))
        opportunities.reverse()

    request.session["redirect_url"] = reverse('crm_all_opportunities')
    page_obj = paginate(request, opportunities, 50)

    return render(
        request,
        'Crm/all_opportunities.html',
        {
            "opportunities": list(page_obj),
            'page_obj': page_obj,
            "ordering": ordering,
            "all_opportunities": True,
        }
    )


@user_passes_test(can_access)
@popup_redirect
def edit_opportunity(request, opportunity_id):
    """view"""
    opportunity = get_object_or_404(models.Opportunity, id=opportunity_id)

    if request.method == 'POST':
        form = forms.OpportunityForm(request.POST, instance=opportunity)
        if form.is_valid():
            opportunity = form.save()
            next_url = request.session.get('redirect_url') or reverse('crm_view_opportunity', args=[opportunity.id])
            return HttpResponseRedirect(next_url)
    else:
        form = forms.OpportunityForm(instance=opportunity)

    return render(
        request,
        'Crm/edit_opportunity.html',
        {'opportunity': opportunity, 'form': form}
    )


@user_passes_test(can_access)
def view_opportunity(request, opportunity_id):
    """view"""
    opportunity = get_object_or_404(models.Opportunity, id=opportunity_id)
    actions = opportunity.action_set.filter(archived=False)
    actions_by_set = get_actions_by_set(actions)

    contacts = []
    for action in actions:
        contacts += [contact for contact in action.contacts.all()]
        for entity in action.entities.all():
            contacts += [contact for contact in entity.contact_set.filter(has_left=False)]
    contacts = list(set(contacts))
    contacts.sort(key=lambda contact_elt: contact_elt.lastname.lower())

    request.session["redirect_url"] = reverse('crm_view_opportunity', args=[opportunity.id])

    context = {
        'opportunity': opportunity,
        'actions_by_set': actions_by_set,
        'contacts': contacts,
    }

    return render(
        request,
        'Crm/view_opportunity.html',
        context
    )


@user_passes_test(can_access)
@popup_redirect
def delete_opportunity(request, opportunity_id):
    """view"""
    opportunity = get_object_or_404(models.Opportunity, id=opportunity_id)

    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                for action in opportunity.action_set.all():
                    action.opportunity = None
                    action.save()
                opportunity.delete()
                next_url = reverse('crm_board_panel')
                return HttpResponseRedirect(next_url)
        else:
            return HttpResponseRedirect(reverse('crm_view_opportunity', args=[opportunity.id]))
    else:
        form = forms.ConfirmForm()

    return render(
        request,
        'balafon/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Are you sure to delete the opportunity "{0}"?').format(opportunity),
            'action_url': reverse("crm_delete_opportunity", args=[opportunity_id]),
        }
    )


@user_passes_test(can_access)
@popup_redirect
def add_action_to_opportunity(request, action_id):
    """view"""
    action = get_object_or_404(models.Action, id=action_id)

    if request.method == "POST":
        form = forms.SelectOpportunityForm(request.POST)
        if form.is_valid():
            opportunity = form.cleaned_data["opportunity"]
            action.opportunity = opportunity
            action.save()
            next_url = request.session.get('redirect_url')
            next_url = next_url or reverse('crm_view_opportunity', args=[opportunity.id])
            return HttpResponseRedirect(next_url)
    else:
        form = forms.SelectOpportunityForm()

    return render(
        request,
        'Crm/add_action_to_opportunity.html',
        {'action': action, 'form': form}
    )


@user_passes_test(can_access)
@popup_redirect
def remove_action_from_opportunity(request, action_id, opportunity_id):
    """view"""
    action = get_object_or_404(models.Action, id=action_id)
    opportunity = get_object_or_404(models.Opportunity, id=opportunity_id)

    if request.method == "POST":
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                if action.opportunity == opportunity:
                    action.opportunity = None
                    action.save()
            next_url = request.session.get('redirect_url')
            next_url = next_url or reverse('crm_view_opportunity', args=[opportunity.id])
            return HttpResponseRedirect(next_url)
    else:
        form = forms.ConfirmForm()

    return render(
        request,
        'balafon/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Do you want to remove the action {0} from opportunity {1}?').format(
                action.subject, opportunity.name
            ),
            'action_url': reverse("crm_remove_action_from_opportunity", args=[action.id, opportunity.id]),
        }
    )


@user_passes_test(can_access)
@popup_redirect
def add_opportunity(request):
    """view"""
    next_url = request.session.get('redirect_url')
    if request.method == 'POST':
        opportunity = models.Opportunity()
        form = forms.OpportunityForm(request.POST, instance=opportunity)
        if form.is_valid():
            opportunity = form.save()
            next_url = next_url or reverse('crm_view_opportunity', args=[opportunity.id])
            return HttpResponseRedirect(next_url)
    else:
        form = forms.OpportunityForm()

    next_url = next_url or reverse('crm_board_panel')
    return render(
        request,
        'Crm/edit_opportunity.html',
        {'next_url': next_url, 'form': form}
    )


class ActionsOfOpportunityXlsView(XlsExportView):
    opportunity = None

    def get_opportunity(self):
        if not self.opportunity:
            opportunity_id = self.kwargs.get('opportunity_id', 0)
            self.opportunity = get_object_or_404(models.Opportunity, id=opportunity_id)
        return self.opportunity

    def get_doc_name(self):
        opportunity = self.get_opportunity()
        return slugify(opportunity.name or _(u'opportunity')) + u".xls"

    def do_fill_workbook(self, workbook):
        """export to excel all actions of the given opportunity"""
        opportunity = self.get_opportunity()

        actions = opportunity.action_set.filter(archived=False)
        actions_by_set = get_actions_by_set(actions)

        headers = (
            _(u'Subject'), _(u'Start date'), _(u'End date'), _(u'Duration'), _(u'Creation date'), _(u'Type'),
            _(u'Status'), _(u'Done'), _(u'Number'), _(u'Amount'), _(u'Entities and contacts'), _(u'Detail'),
        )

        for action_set_id, action_set_name, actions, actions_count in actions_by_set:
            sheet = workbook.add_sheet(action_set_name or _(u'Actions'))

            for index, header in enumerate(headers):
                self.write_cell(sheet, 0, index, header)

            for index, item in enumerate(actions):
                line = index + 1
                self.write_cell(sheet, line, 0, item.subject)
                self.write_cell(sheet, line, 1, item.planned_date)
                self.write_cell(sheet, line, 2, item.end_datetime)
                self.write_cell(sheet, line, 3, item.duration() if item.show_duration() else '')
                self.write_cell(sheet, line, 4, item.created)
                self.write_cell(sheet, line, 5, item.type.name if item.type else u'')
                self.write_cell(sheet, line, 6, item.status.name if item.status else u'')
                self.write_cell(sheet, line, 7, _(u'Yes') if item.done else _(u'No'))
                self.write_cell(sheet, line, 8, item.number)
                self.write_cell(sheet, line, 9, item.amount)
                self.write_cell(sheet, line, 10, u', '.join(item.get_entities_and_contacts()))
                self.write_cell(sheet, line, 11, item.detail)
