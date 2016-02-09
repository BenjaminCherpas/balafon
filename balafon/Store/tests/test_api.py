# -*- coding: utf-8 -*-
"""unit testing"""

import logging

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from balafon.Store import models


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


class StoreItemApiTest(BaseTestCase):
    """Test that we are getting store items"""

    def test_view_store_items(self):
        """It should return all"""

        store_item1 = mommy.make(models.StoreItem)
        store_item2 = mommy.make(models.StoreItem)

        url = reverse('store_store-items-list')

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)

        data = sorted(response.data, key=lambda item_: item_['id'])
        item1 = data[0]
        item2 = data[1]

        self.assertEqual(item1['id'], store_item1.id)
        self.assertEqual(item1['name'], store_item1.name)
        self.assertEqual(item2['id'], store_item2.id)
        self.assertEqual(item2['name'], store_item2.name)

    def test_view_store_items_category(self):
        """It should return only items of category"""

        category1 = mommy.make(models.StoreItemCategory)
        category2 = mommy.make(models.StoreItemCategory)

        store_item1 = mommy.make(models.StoreItem, category=category1)
        mommy.make(models.StoreItem, category=category2)
        mommy.make(models.StoreItem)

        url = reverse('store_store-items-list') + "?category={0}".format(category1.id)

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)

        item1 = response.data[0]

        self.assertEqual(item1['id'], store_item1.id)
        self.assertEqual(item1['name'], store_item1.name)

    def test_view_store_items_tag(self):
        """It should return only items of tag"""

        tag1 = mommy.make(models.StoreItemTag)
        tag2 = mommy.make(models.StoreItemTag)

        store_item1 = mommy.make(models.StoreItem)
        store_item1.tags.add(tag1)
        store_item1.save()
        store_item2 = mommy.make(models.StoreItem)
        store_item2.tags.add(tag2)
        store_item2.save()
        mommy.make(models.StoreItem)

        url = reverse('store_store-items-list') + "?tag={0}".format(tag1.id)

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)

        item1 = response.data[0]

        self.assertEqual(item1['id'], store_item1.id)
        self.assertEqual(item1['name'], store_item1.name)

    def test_view_store_items_ids(self):
        """It should return only items of ids"""

        store_item1 = mommy.make(models.StoreItem)
        store_item2 = mommy.make(models.StoreItem)
        mommy.make(models.StoreItem)
        mommy.make(models.StoreItem)

        url = reverse('store_store-items-list') + "?ids={0}".format(
            u','.join([str(id_) for id_ in (store_item1.id, store_item2.id)])
        )

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)

        data = sorted(response.data, key=lambda item_: item_['id'])

        item1 = data[0]
        item2 = data[1]

        self.assertEqual(item1['id'], store_item1.id)
        self.assertEqual(item1['name'], store_item1.name)

        self.assertEqual(item2['id'], store_item2.id)
        self.assertEqual(item2['name'], store_item2.name)

    def test_view_store_items_id(self):
        """It should return only items of id"""

        store_item1 = mommy.make(models.StoreItem)
        mommy.make(models.StoreItem)
        mommy.make(models.StoreItem)

        url = reverse('store_store-items-list') + "?ids={0}".format(store_item1.id)

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)
        data = sorted(response.data, key=lambda item_: item_['id'])

        item1 = data[0]

        self.assertEqual(item1['id'], store_item1.id)
        self.assertEqual(item1['name'], store_item1.name)

    def test_view_store_items_missing(self):
        """It should return only items of ids"""

        store_item1 = mommy.make(models.StoreItem)

        url = reverse('store_store-items-list') + "?ids={0}".format(
            u','.join([str(id_) for id_ in (store_item1.id, store_item1.id + 1)])
        )

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)
        data = sorted(response.data, key=lambda item_: item_['id'])

        item1 = data[0]

        self.assertEqual(item1['id'], store_item1.id)
        self.assertEqual(item1['name'], store_item1.name)

    def test_view_store_items_none(self):
        """It should return only items of ids"""

        store_item1 = mommy.make(models.StoreItem)
        mommy.make(models.StoreItem)
        mommy.make(models.StoreItem)

        url = reverse('store_store-items-list') + "?ids="
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 0)

    def test_view_store_items_invalid(self):
        """It should return only items of ids"""

        store_item1 = mommy.make(models.StoreItem)
        mommy.make(models.StoreItem)
        mommy.make(models.StoreItem)

        url = reverse('store_store-items-list') + "?ids={0}".format(
            u','.join([str(id_) for id_ in (store_item1.id, "hjhkhz")])
        )

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)
        data = sorted(response.data, key=lambda item_: item_['id'])

        item1 = data[0]

        self.assertEqual(item1['id'], store_item1.id)
        self.assertEqual(item1['name'], store_item1.name)

    def test_view_store_items_invalid2(self):
        """It should return only items of ids"""

        mommy.make(models.StoreItem)
        mommy.make(models.StoreItem)

        url = reverse('store_store-items-list') + "?ids=dejek"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 0)

    def test_view_store_items_by_name(self):
        """It should return only items of name"""

        store_item1 = mommy.make(models.StoreItem, name="Abcd")
        store_item2 = mommy.make(models.StoreItem, name="Bcd")
        mommy.make(models.StoreItem, name="Xyz")

        url = reverse('store_store-items-list') + "?name=bcd"

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)

        data = sorted(response.data, key=lambda item_: item_['id'])

        item1 = data[0]
        item2 = data[1]

        self.assertEqual(item1['id'], store_item1.id)
        self.assertEqual(item1['name'], store_item1.name)

        self.assertEqual(item2['id'], store_item2.id)
        self.assertEqual(item2['name'], store_item2.name)

    def test_view_store_items_by_name2(self):
        """It should return only items of name"""

        for i in xrange(25):
            mommy.make(models.StoreItem, name="Abc{0}".format(i))

        url = reverse('store_store-items-list') + "?name=Abc"

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 20)

    def test_view_store_items_by_fullname(self):
        """It should return only items of name"""

        store_item1 = mommy.make(models.StoreItem, name="Abcd")
        store_item2 = mommy.make(models.StoreItem, name="Bcd")
        mommy.make(models.StoreItem, name="Xyz")

        url = reverse('store_store-items-list') + "?fullname=bcd"

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)

        data = sorted(response.data, key=lambda item_: item_['id'])
        item1 = data[0]
        item2 = data[1]

        self.assertEqual(item1['id'], store_item1.id)
        self.assertEqual(item1['name'], store_item1.name)

        self.assertEqual(item2['id'], store_item2.id)
        self.assertEqual(item2['name'], store_item2.name)

    def test_view_store_items_public_properties(self):
        """It should return only public properties"""

        size_property = mommy.make(models.StoreItemProperty, name="size", is_public=True)
        weight_property = mommy.make(models.StoreItemProperty, name="weight", is_public=False)

        store_item1 = mommy.make(models.StoreItem)
        store_item1.set_property("size", "179cm")
        store_item1.set_property("weight", "too much")

        url = reverse('store_store-items-list')

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)

        item1 = response.data[0]

        self.assertEqual(item1['id'], store_item1.id)
        self.assertEqual(item1['name'], store_item1.name)
        self.assertEqual(len(item1['public_properties']), 1)
        self.assertEqual(item1['public_properties']['size'], "179cm")


class FavoriteApiTest(BaseTestCase):
    """Test that we are getting user favorites"""

    def test_view_empty_list(self):
        """It should return none"""

        store_item1 = mommy.make(models.StoreItem)
        store_item2 = mommy.make(models.StoreItem)

        url = reverse('store_favorites_api')

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        favorites = response.data['favorites']
        self.assertEqual(len(favorites), 0)

    def test_view_anonymous(self):
        """It should return error"""
        self.client.logout()

        url = reverse('store_favorites_api')

        response = self.client.get(url, format='json')
        self.assertTrue(response.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED))

    def test_view_favorites(self):
        """It should return favorites"""
        other_user = mommy.make(models.User)

        store_item1 = mommy.make(models.StoreItem)
        store_item2 = mommy.make(models.StoreItem)
        store_item3 = mommy.make(models.StoreItem)

        mommy.make(models.Favorite, user=self.user, item=store_item1)
        mommy.make(models.Favorite, user=self.user, item=store_item2)
        mommy.make(models.Favorite, user=other_user, item=store_item3)
        mommy.make(models.Favorite, user=other_user, item=store_item1)

        url = reverse('store_favorites_api')

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        favorites = response.data['favorites']
        self.assertEqual(len(favorites), 2)

        data = sorted(favorites, key=lambda item_: item_['id'])
        item1 = data[0]
        item2 = data[1]

        self.assertEqual(item1['id'], store_item1.id)
        self.assertEqual(item2['id'], store_item2.id)

    def test_add_favorites(self):
        """It should add a favorite"""
        store_item1 = mommy.make(models.StoreItem)
        store_item2 = mommy.make(models.StoreItem)
        store_item3 = mommy.make(models.StoreItem)

        url = reverse('store_favorites_api')

        data = {
            'items': [{'id': store_item1.id}],
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['ok'], True)

        self.assertEqual(1, models.Favorite.objects.count())
        self.assertEqual(1, models.Favorite.objects.filter(user=self.user, item=store_item1).count())

    def test_change_favorites(self):
        """It should update favorites"""
        store_item1 = mommy.make(models.StoreItem)
        store_item2 = mommy.make(models.StoreItem)
        store_item3 = mommy.make(models.StoreItem)

        url = reverse('store_favorites_api')

        mommy.make(models.Favorite, user=self.user, item=store_item1)
        mommy.make(models.Favorite, user=self.user, item=store_item2)

        data = {
            'items': [{'id': store_item1.id}, {'id': store_item3.id}],
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['ok'], True)

        self.assertEqual(2, models.Favorite.objects.count())
        self.assertEqual(1, models.Favorite.objects.filter(user=self.user, item=store_item1).count())
        self.assertEqual(0, models.Favorite.objects.filter(user=self.user, item=store_item2).count())
        self.assertEqual(1, models.Favorite.objects.filter(user=self.user, item=store_item3).count())

        self.assertEqual(1, models.StoreItem.objects.filter(id=store_item2.id).count())

    def test_delete_favorites(self):
        """It should delete all favorites"""
        store_item1 = mommy.make(models.StoreItem)
        store_item2 = mommy.make(models.StoreItem)

        url = reverse('store_favorites_api')

        mommy.make(models.Favorite, user=self.user, item=store_item1)
        mommy.make(models.Favorite, user=self.user, item=store_item2)

        data = {
            'items': [],
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['ok'], True)

        self.assertEqual(0, models.Favorite.objects.count())

        self.assertEqual(1, models.StoreItem.objects.filter(id=store_item1.id).count())
        self.assertEqual(1, models.StoreItem.objects.filter(id=store_item2.id).count())

    def test_add_favorites_anonymous(self):
        """It should not add a favorite"""
        self.client.logout()

        store_item1 = mommy.make(models.StoreItem)
        store_item2 = mommy.make(models.StoreItem)
        store_item3 = mommy.make(models.StoreItem)

        url = reverse('store_favorites_api')

        mommy.make(models.Favorite, user=self.user, item=store_item1)
        mommy.make(models.Favorite, user=self.user, item=store_item2)

        data = {
            'items': [{'id': store_item1.id}, {'id': store_item3.id}],
        }

        response = self.client.post(url, data=data, format='json')
        self.assertTrue(response.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED))

        self.assertEqual(2, models.Favorite.objects.count())
        self.assertEqual(1, models.Favorite.objects.filter(user=self.user, item=store_item1).count())
        self.assertEqual(1, models.Favorite.objects.filter(user=self.user, item=store_item2).count())
        self.assertEqual(0, models.Favorite.objects.filter(user=self.user, item=store_item3).count())