# -*- coding: utf-8 -*-

from datetime import datetime
import uuid

from django.db import models
from django.db.models import signals

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericRelation
from django.core.urlresolvers import reverse
from django.utils.dateformat import DateFormat
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, ugettext_lazy as _

from coop_cms.models import Newsletter
from django_extensions.db.models import TimeStampedModel

from sanza.Crm.models import Contact, Action, SubscriptionType
from sanza.Users.models import UserPreferences, Favorite


class Emailing(TimeStampedModel):
    
    STATUS_EDITING = 1
    STATUS_SCHEDULED = 2
    STATUS_SENDING = 3
    STATUS_SENT = 4
    
    STATUS_CHOICES = (
        (STATUS_EDITING, _(u'Edition in progress')),
        (STATUS_SCHEDULED, _(u'Sending is scheduled')),
        (STATUS_SENDING, _(u'Sending in progress')),
        (STATUS_SENT, _(u'Sent')),
    )

    subscription_type = models.ForeignKey(SubscriptionType)
    newsletter = models.ForeignKey(Newsletter) 
    send_to = models.ManyToManyField(Contact, blank=True, related_name="emailing_to_be_received")
    sent_to = models.ManyToManyField(Contact, blank=True, related_name="emailing_received")
    opened_emails = models.ManyToManyField(Contact, blank=True, related_name="emailing_opened")
    status = models.IntegerField(default=STATUS_EDITING, choices=STATUS_CHOICES)
    
    scheduling_dt = models.DateTimeField(_(u"scheduling date"), blank=True, default=None, null=True)
    sending_dt = models.DateTimeField(_(u"sending date"), blank=True, default=None, null=True)

    favorites = GenericRelation(Favorite)

    def __unicode__(self):
        return self.newsletter.subject

    class Meta:
        verbose_name = _(u'emailing')
        verbose_name_plural = _(u'emailings')
        
    def get_info(self):
        text = self.get_status_display()
        if self.status == Emailing.STATUS_SCHEDULED:
            return _("{0} on {1}").format(text, DateFormat(self.scheduling_dt).format(" d F Y H:i"))
        elif self.status == Emailing.STATUS_SENT:
            return _("{0} on {1}").format(text, DateFormat(self.sending_dt).format(" d F Y H:i"))
        return text
        
    def next_action(self):
        action = ""
        if self.status == Emailing.STATUS_EDITING:
            action = '<a class="colorbox-form action-button" href="{1}">{0}</a>'.format(
                ugettext(u'Send'), reverse("emailing_confirm_send_mail", args=[self.id])
            )
        if self.status == Emailing.STATUS_SCHEDULED:
            action = '<a class="colorbox-form action-button" href="{1}">{0}</a>'.format(
                ugettext(u'Cancel'), reverse("emailing_cancel_send_mail", args=[self.id])
            )
        return mark_safe(action)
    
    def get_contacts(self):
        return list(self.send_to.all()) + list(self.sent_to.all())
        
    def save(self, *args, **kwargs):
        if self.status == Emailing.STATUS_SENT and self.sending_dt == None:
            self.sending_dt = datetime.now()
        return super(Emailing, self).save(*args, **kwargs)


class MagicLink(models.Model):
    emailing = models.ForeignKey(Emailing)
    url = models.URLField()
    visitors = models.ManyToManyField(Contact, blank=True)
    uuid = models.CharField(max_length=100, blank=True, default='', db_index=True)
    
    def __unicode__(self):
        return self.url
    
    def save(self, *args, **kwargs):
        super(MagicLink, self).save(*args, **kwargs)
        if not self.uuid:
            name = '{0}-magic-link-{1}-{2}'.format(settings.SECRET_KEY, self.id, self.url)
            self.uuid = uuid.uuid5(uuid.NAMESPACE_URL, name)
            return super(MagicLink, self).save()


def force_message_in_favorites(sender, instance, signal, created, **kwargs):
    action = instance
    if created and action.type and action.type.name == ugettext(u"Message"):
        for user_pref in UserPreferences.objects.filter(message_in_favorites=True):
            content_type = ContentType.objects.get_for_model(action.__class__)
            Favorite.objects.get_or_create(
                user=user_pref.user,
                content_type=content_type,
                object_id=action.id
            )
            
signals.post_save.connect(force_message_in_favorites, sender=Action)

if 'djrill' in settings.INSTALLED_APPS:
    import sanza.Emailing.backends.mandrill