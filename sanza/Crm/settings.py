# -*- coding: utf-8 -*-

from django.conf import settings as project_settings

ENTITY_LOGO_DIR = getattr(project_settings, 'ENTITY_LOGO_DIR', 'entities/logos')
CONTACT_PHOTO_DIR = getattr(project_settings, 'CONTACT_PHOTO_DIR', 'contacts/photos')
CONTACTS_IMPORT_DIR = getattr(project_settings, 'CSV_IMPORT_DIR', 'imports')
OPPORTUNITY_DISPLAY_ON_BOARD_DEFAULT = getattr(project_settings, 'OPPORTUNITY_DISPLAY_ON_BOARD_DEFAULT', True)

def get_default_country():
    return getattr(project_settings, 'SANZA_DEFAULT_COUNTRY', 'France')

ALLOW_COUPLE_GENDER = getattr(project_settings, 'SANZA_ALLOW_COUPLE_GENDER', False)