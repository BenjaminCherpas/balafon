# -*- coding: utf-8 -*-
"""test mailto action on search results"""

import xlrd

from django.core.urlresolvers import reverse

from model_mommy import mommy

from balafon.Crm import models

from balafon.Search.tests import BaseTestCase


class ExportContactsToExcelTest(BaseTestCase):
    """Test Export Excel operation from search results"""

    def _create_contact(self, entity_name="My Corp", **kwargs):
        """create a contact"""
        entity = mommy.make(models.Entity, name=entity_name)
        contact = entity.default_contact
        contact.main_contact = True
        contact.has_left = False

        for key, value in kwargs.items():
            setattr(contact, key, value)

        contact.save()
        return entity, contact

    def test_export_one_contact(self):
        """test export one contact"""
        entity, contact = self._create_contact(firstname=u"Tom", lastname=u"Oto", email=u'toto@mailinator.com')

        url = reverse('search_export_contacts_as_excel')
        data = {"gr0-_-entity_name-_-0": entity.name}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        workbook = xlrd.open_workbook(file_contents=response.content)
        self.assertEqual(workbook.nsheets, 1)

        worksheet = workbook.sheet_by_index(0)
        self.assertEqual(worksheet.nrows, 2)
        self.assertEqual(worksheet.ncols, 19)

        # fields = [
        #     'id', 'get_gender_display', 'lastname', 'firstname', 'title', 'get_entity_name', 'job', 'role',
        #     'get_address', 'get_address2', 'get_address3', 'get_zip_code', 'get_cedex', 'get_city',
        #     'get_foreign_country', 'mobile', 'get_phone', 'get_email', 'birth_date'
        # ]

        self.assertEqual(worksheet.cell(1, 0).value, str(contact.id))
        self.assertEqual(worksheet.cell(1, 1).value, "")
        self.assertEqual(worksheet.cell(1, 2).value, contact.lastname)
        self.assertEqual(worksheet.cell(1, 3).value, contact.firstname)
        self.assertEqual(worksheet.cell(1, 4).value, "")
        self.assertEqual(worksheet.cell(1, 5).value, entity.name)
        self.assertEqual(worksheet.cell(1, 17).value, contact.email)

    def test_export_contact_without_group(self):
        """it should export groups to Excel"""
        entity, contact = self._create_contact(firstname=u"Tom", lastname=u"Oto", email=u'toto@mailinator.com')

        group = mommy.make(models.Group, name=u"Group1", export_to=u"")
        group.contacts.add(contact)
        group.save()

        url = reverse('search_export_contacts_as_excel')
        data = {"gr0-_-entity_name-_-0": entity.name}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        workbook = xlrd.open_workbook(file_contents=response.content)
        self.assertEqual(workbook.nsheets, 1)

        worksheet = workbook.sheet_by_index(0)
        self.assertEqual(worksheet.nrows, 2)
        self.assertEqual(worksheet.ncols, 19)

        self.assertEqual(worksheet.cell(1, 0).value, str(contact.id))
        self.assertEqual(worksheet.cell(1, 1).value, "")
        self.assertEqual(worksheet.cell(1, 2).value, contact.lastname)
        self.assertEqual(worksheet.cell(1, 3).value, contact.firstname)
        self.assertEqual(worksheet.cell(1, 4).value, "")
        self.assertEqual(worksheet.cell(1, 5).value, entity.name)
        self.assertEqual(worksheet.cell(1, 17).value, contact.email)

    def test_export_contact_group(self):
        """it should export groups to Excel"""
        entity, contact = self._create_contact(firstname=u"Tom", lastname=u"Oto", email=u'toto@mailinator.com')

        group = mommy.make(models.Group, name=u"Group1", export_to=u"Groups")
        group.contacts.add(contact)
        group.save()

        url = reverse('search_export_contacts_as_excel')
        data = {"gr0-_-entity_name-_-0": entity.name}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        workbook = xlrd.open_workbook(file_contents=response.content)
        self.assertEqual(workbook.nsheets, 1)

        worksheet = workbook.sheet_by_index(0)
        self.assertEqual(worksheet.nrows, 2)
        self.assertEqual(worksheet.ncols, 20)

        self.assertEqual(worksheet.cell(1, 0).value, str(contact.id))
        self.assertEqual(worksheet.cell(1, 1).value, "")
        self.assertEqual(worksheet.cell(1, 2).value, contact.lastname)
        self.assertEqual(worksheet.cell(1, 3).value, contact.firstname)
        self.assertEqual(worksheet.cell(1, 4).value, "")
        self.assertEqual(worksheet.cell(1, 5).value, entity.name)
        self.assertEqual(worksheet.cell(1, 17).value, contact.email)

        self.assertEqual(worksheet.cell(0, 19).value, u"Groups")
        self.assertEqual(worksheet.cell(1, 19).value, group.name)

    def test_export_entity_group(self):
        """it should export groups to Excel"""
        entity, contact = self._create_contact(firstname=u"Tom", lastname=u"Oto", email=u'toto@mailinator.com')

        group = mommy.make(models.Group, name=u"Group1", export_to=u"Groups")
        group.entities.add(entity)
        group.save()

        url = reverse('search_export_contacts_as_excel')
        data = {"gr0-_-entity_name-_-0": entity.name}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        workbook = xlrd.open_workbook(file_contents=response.content)
        self.assertEqual(workbook.nsheets, 1)

        worksheet = workbook.sheet_by_index(0)
        self.assertEqual(worksheet.nrows, 2)
        self.assertEqual(worksheet.ncols, 20)

        self.assertEqual(worksheet.cell(1, 0).value, str(contact.id))
        self.assertEqual(worksheet.cell(1, 1).value, "")
        self.assertEqual(worksheet.cell(1, 2).value, contact.lastname)
        self.assertEqual(worksheet.cell(1, 3).value, contact.firstname)
        self.assertEqual(worksheet.cell(1, 4).value, "")
        self.assertEqual(worksheet.cell(1, 5).value, entity.name)
        self.assertEqual(worksheet.cell(1, 17).value, contact.email)

        self.assertEqual(worksheet.cell(0, 19).value, u"Groups")
        self.assertEqual(worksheet.cell(1, 19).value, group.name)

    def test_export_contact_not_in_group(self):
        """it should export groups to Excel"""
        entity, contact = self._create_contact(firstname=u"Tom", lastname=u"Oto", email=u'toto@mailinator.com')

        mommy.make(models.Group, name=u"Group1", export_to=u"Groups")

        url = reverse('search_export_contacts_as_excel')
        data = {"gr0-_-entity_name-_-0": entity.name}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        workbook = xlrd.open_workbook(file_contents=response.content)
        self.assertEqual(workbook.nsheets, 1)

        worksheet = workbook.sheet_by_index(0)
        self.assertEqual(worksheet.nrows, 2)
        self.assertEqual(worksheet.ncols, 20)

        self.assertEqual(worksheet.cell(1, 0).value, str(contact.id))
        self.assertEqual(worksheet.cell(1, 1).value, "")
        self.assertEqual(worksheet.cell(1, 2).value, contact.lastname)
        self.assertEqual(worksheet.cell(1, 3).value, contact.firstname)
        self.assertEqual(worksheet.cell(1, 4).value, "")
        self.assertEqual(worksheet.cell(1, 5).value, entity.name)
        self.assertEqual(worksheet.cell(1, 17).value, contact.email)

        self.assertEqual(worksheet.cell(0, 19).value, u"Groups")
        self.assertEqual(worksheet.cell(1, 19).value, u"")

    def test_export_contact_several_groups_same_column(self):
        """it should export groups to Excel"""
        entity, contact = self._create_contact(firstname=u"Tom", lastname=u"Oto", email=u'toto@mailinator.com')

        group1 = mommy.make(models.Group, name=u"Group1", export_to=u"Groups")
        group1.contacts.add(contact)
        group1.save()

        group2 = mommy.make(models.Group, name=u"Group2", export_to=u"Groups")
        group2.contacts.add(contact)
        group2.save()

        url = reverse('search_export_contacts_as_excel')
        data = {"gr0-_-entity_name-_-0": entity.name}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        workbook = xlrd.open_workbook(file_contents=response.content)
        self.assertEqual(workbook.nsheets, 1)

        worksheet = workbook.sheet_by_index(0)
        self.assertEqual(worksheet.nrows, 2)
        self.assertEqual(worksheet.ncols, 20)

        self.assertEqual(worksheet.cell(1, 0).value, str(contact.id))
        self.assertEqual(worksheet.cell(1, 1).value, "")
        self.assertEqual(worksheet.cell(1, 2).value, contact.lastname)
        self.assertEqual(worksheet.cell(1, 3).value, contact.firstname)
        self.assertEqual(worksheet.cell(1, 4).value, "")
        self.assertEqual(worksheet.cell(1, 5).value, entity.name)
        self.assertEqual(worksheet.cell(1, 17).value, contact.email)

        self.assertEqual(worksheet.cell(0, 19).value, u"Groups")
        self.assertEqual(worksheet.cell(1, 19).value, u','.join([group1.name, group2.name]))

    def test_export_contact_several_groups_different_columns(self):
        """it should export groups to Excel"""
        entity, contact = self._create_contact(firstname=u"Tom", lastname=u"Oto", email=u'toto@mailinator.com')

        group1 = mommy.make(models.Group, name=u"Group1", export_to=u"Groups")
        group1.contacts.add(contact)
        group1.save()

        group2 = mommy.make(models.Group, name=u"Group2", export_to=u"Categories")
        group2.contacts.add(contact)
        group2.save()

        group3 = mommy.make(models.Group, name=u"Group3")
        group3.contacts.add(contact)
        group3.save()

        url = reverse('search_export_contacts_as_excel')
        data = {"gr0-_-entity_name-_-0": entity.name}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        workbook = xlrd.open_workbook(file_contents=response.content)
        self.assertEqual(workbook.nsheets, 1)

        worksheet = workbook.sheet_by_index(0)
        self.assertEqual(worksheet.nrows, 2)
        self.assertEqual(worksheet.ncols, 21)

        self.assertEqual(worksheet.cell(1, 0).value, str(contact.id))
        self.assertEqual(worksheet.cell(1, 1).value, "")
        self.assertEqual(worksheet.cell(1, 2).value, contact.lastname)
        self.assertEqual(worksheet.cell(1, 3).value, contact.firstname)
        self.assertEqual(worksheet.cell(1, 4).value, "")
        self.assertEqual(worksheet.cell(1, 5).value, entity.name)
        self.assertEqual(worksheet.cell(1, 17).value, contact.email)

        self.assertEqual(worksheet.cell(0, 19).value, u"Categories")
        self.assertEqual(worksheet.cell(1, 19).value, group2.name)

        self.assertEqual(worksheet.cell(0, 20).value, u"Groups")
        self.assertEqual(worksheet.cell(1, 20).value, group1.name)

