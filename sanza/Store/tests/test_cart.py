# -*- coding: utf-8 -*-
"""unit testing"""

from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()

from datetime import datetime
import logging
from unittest import skipIf

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core import mail

from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from sanza.Crm.models import Action, ActionType
from sanza.Profile.utils import create_profile_contact
from sanza.Store import models
from sanza.Store.settings import get_cart_type_name


class BaseTestCase(APITestCase):
    """Base class for test cases"""

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.user = User.objects.create(username="toto", is_active=True, is_staff=False)
        self.user.set_password("abc")
        self.user.save()
        self.client = APIClient()
        self._login()

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def _login(self):
        self.client.login(username="toto", password="abc")


@skipIf(not ("sanza.Profile" in settings.INSTALLED_APPS), "registration not installed")
class CartTest(BaseTestCase):
    """Test that cart is process properly"""

    def test_post_cart(self):
        """It should create a new sale and action"""

        #Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact

        store_item1 = mommy.make(models.StoreItem)
        store_item2 = mommy.make(models.StoreItem)

        delivery_point = mommy.make(models.DeliveryPoint)

        data = {
            'items': [
                {'id': store_item1.id, 'quantity': 2},
                {'id': store_item2.id, 'quantity': 1},
            ],
            'delivery_point': delivery_point.id,
            'notes': ' ',
            'purchase_datetime': datetime(2015, 7, 23, 12, 0)
        }

        url = reverse('store_post_cart')

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['ok'], True)
        self.assertEqual(response.data['deliveryDate'], data['purchase_datetime'])
        self.assertEqual(response.data['deliveryPlace'], delivery_point.name)

        action_type = ActionType.objects.get(name=get_cart_type_name())

        action_queryset = Action.objects.filter(type=action_type)
        self.assertEqual(action_queryset.count(), 1)
        action = action_queryset[0]

        self.assertEqual(list(action.contacts.all()), [contact])
        self.assertEqual(action.subject, '')
        self.assertEqual(action.detail, '')
        self.assertEqual(action.planned_date, data['purchase_datetime'])

        self.assertEqual(action.sale.saleitem_set.count(), 2)
        self.assertEqual(action.sale.saleitem_set.all()[0].item, store_item1)
        self.assertEqual(action.sale.saleitem_set.all()[0].text, store_item1.name)
        self.assertEqual(action.sale.saleitem_set.all()[0].pre_tax_price, store_item1.pre_tax_price)
        self.assertEqual(action.sale.saleitem_set.all()[0].vat_rate, store_item1.vat_rate)
        self.assertEqual(action.sale.saleitem_set.all()[0].quantity, 2)

        self.assertEqual(action.sale.saleitem_set.all()[1].item, store_item2)
        self.assertEqual(action.sale.saleitem_set.all()[1].text, store_item2.name)
        self.assertEqual(action.sale.saleitem_set.all()[1].pre_tax_price, store_item2.pre_tax_price)
        self.assertEqual(action.sale.saleitem_set.all()[1].vat_rate, store_item2.vat_rate)
        self.assertEqual(action.sale.saleitem_set.all()[1].quantity, 1)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, [profile.contact.email])
        self.assertEqual(mail.outbox[1].to, [settings.SANZA_NOTIFICATION_EMAIL])

    def test_post_cart_notes(self):
        """It should create a new sale and action"""

        #Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact

        store_item1 = mommy.make(models.StoreItem)
        store_item2 = mommy.make(models.StoreItem)

        delivery_point = mommy.make(models.DeliveryPoint)

        data = {
            'items': [
                {'id': store_item1.id, 'quantity': 2},
                {'id': store_item2.id, 'quantity': 1},
            ],
            'delivery_point': delivery_point.id,
            'notes': 'This is a text',
            'purchase_datetime': datetime(2015, 7, 23, 12, 0)
        }

        url = reverse('store_post_cart')

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['ok'], True)
        self.assertEqual(response.data['deliveryDate'], data['purchase_datetime'])
        self.assertEqual(response.data['deliveryPlace'], delivery_point.name)

        action_type = ActionType.objects.get(name=get_cart_type_name())

        action_queryset = Action.objects.filter(type=action_type)
        self.assertEqual(action_queryset.count(), 1)
        action = action_queryset[0]

        self.assertEqual(list(action.contacts.all()), [contact])
        self.assertEqual(action.subject, data['notes'])
        self.assertEqual(action.detail, '')
        self.assertEqual(action.planned_date, data['purchase_datetime'])

        self.assertEqual(action.sale.saleitem_set.count(), 2)
        self.assertEqual(action.sale.saleitem_set.all()[0].item, store_item1)
        self.assertEqual(action.sale.saleitem_set.all()[0].text, store_item1.name)
        self.assertEqual(action.sale.saleitem_set.all()[0].pre_tax_price, store_item1.pre_tax_price)
        self.assertEqual(action.sale.saleitem_set.all()[0].vat_rate, store_item1.vat_rate)
        self.assertEqual(action.sale.saleitem_set.all()[0].quantity, 2)

        self.assertEqual(action.sale.saleitem_set.all()[1].item, store_item2)
        self.assertEqual(action.sale.saleitem_set.all()[1].text, store_item2.name)
        self.assertEqual(action.sale.saleitem_set.all()[1].pre_tax_price, store_item2.pre_tax_price)
        self.assertEqual(action.sale.saleitem_set.all()[1].vat_rate, store_item2.vat_rate)
        self.assertEqual(action.sale.saleitem_set.all()[1].quantity, 1)

        self.assertEqual(len(mail.outbox), 2)

    def test_post_cart_notes_several_lines(self):
        """It should create a new sale and action"""

        #Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact

        store_item1 = mommy.make(models.StoreItem)
        store_item2 = mommy.make(models.StoreItem)

        delivery_point = mommy.make(models.DeliveryPoint)

        data = {
            'items': [
                {'id': store_item1.id, 'quantity': 2},
                {'id': store_item2.id, 'quantity': 1},
            ],
            'delivery_point': delivery_point.id,
            'notes': 'a\nB\nc',
            'purchase_datetime': datetime(2015, 7, 23, 12, 0)
        }

        url = reverse('store_post_cart')

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['ok'], True)
        self.assertEqual(response.data['deliveryDate'], data['purchase_datetime'])
        self.assertEqual(response.data['deliveryPlace'], delivery_point.name)

        action_type = ActionType.objects.get(name=get_cart_type_name())

        action_queryset = Action.objects.filter(type=action_type)
        self.assertEqual(action_queryset.count(), 1)
        action = action_queryset[0]

        self.assertEqual(list(action.contacts.all()), [contact])
        self.assertEqual(action.subject, 'a')
        self.assertEqual(action.detail, 'B\nc')
        self.assertEqual(action.planned_date, data['purchase_datetime'])

        self.assertEqual(action.sale.saleitem_set.count(), 2)
        self.assertEqual(action.sale.saleitem_set.all()[0].item, store_item1)
        self.assertEqual(action.sale.saleitem_set.all()[0].text, store_item1.name)
        self.assertEqual(action.sale.saleitem_set.all()[0].pre_tax_price, store_item1.pre_tax_price)
        self.assertEqual(action.sale.saleitem_set.all()[0].vat_rate, store_item1.vat_rate)
        self.assertEqual(action.sale.saleitem_set.all()[0].quantity, 2)

        self.assertEqual(action.sale.saleitem_set.all()[1].item, store_item2)
        self.assertEqual(action.sale.saleitem_set.all()[1].text, store_item2.name)
        self.assertEqual(action.sale.saleitem_set.all()[1].pre_tax_price, store_item2.pre_tax_price)
        self.assertEqual(action.sale.saleitem_set.all()[1].vat_rate, store_item2.vat_rate)
        self.assertEqual(action.sale.saleitem_set.all()[1].quantity, 1)

        self.assertEqual(len(mail.outbox), 2)