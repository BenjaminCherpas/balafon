# -*- coding: utf-8 -*-

from __future__ import print_function

import codecs
import difflib
import os.path

from balafon.Crm.models import City
from balafon.Crm.models import Zone
from balafon.Crm.models import Contact
from balafon.Crm.models import Entity
from balafon.Crm.models import SpecialCaseCity

from django.core.management.base import BaseCommand


def remove_accents(text):
    chars_with_accent = "àâçéèêëîïôùûüÿ-".decode("utf8")
    corresponding_chars_without_accents = "aaceeeeiiouuuy "
    new_string = ""
    for char in text:
        i = chars_with_accent.find(char)
        if i >= 0:
            new_string += corresponding_chars_without_accents[i]
        else:
            new_string += char
    return new_string


def special_cases(departement_code, city, txt):
    special_case = SpecialCaseCity.objects.create(
        departement_code=departement_code, city=city, oldname=city.name, possibilities=txt, change_validated="no"
    )


def manage_spe_cases():
    """Change the name of the special cases cities"""

    spe_cases = SpecialCaseCity.objects.filter(change_validated="no")
    for spe_case in spe_cases:
        try:
            if spe_case.possibilities == "":
                pass

            print(spe_case.city.name.encode('utf8'), spe_case.departement_code)
            print("\t[0] : No match")
            temp = spe_case.possibilities.split("|")
            count = 0
            if len(temp) == 1:
                print("\t[1] : " + spe_case.possibilities)
                count = 1
            else:
                for i in range(1, len(temp)):
                    count += 1
                    print("\t[" + str(i) + "] : " + temp[i])
            choice = -1
            while choice > count or choice < 0:
                try:
                    choice = int(raw_input("\nWrite the value of the corresponding name : "))
                except ValueError:
                    pass
            if choice > 0:
                if len(temp) == 1:
                    spe_case.city.name = temp[choice-1]
                    spe_case.city.save()
                    print("\nName changed to : " + temp[choice-1] + "\n\n")
                    spe_case.change_validated = "yes"
                    spe_case.save()
                else:
                    spe_case.city.name = temp[choice]
                    spe_case.city.save()
                    print("\nName changed to : " + temp[choice] + "\n\n")
                    spe_case.change_validated = "yes"
                    spe_case.save()
            else:
                print("No modification\n\n")
                spe_case.delete()
        except UnicodeEncodeError:
            print("Error unknown character - try changing name in admin")
            pass


def fill_db():
    dict_dept = {}

    # Add all the cities from GeoNames in the database
    app_dir_name = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    geonames_file_name = os.path.join(app_dir_name, 'geonames/FR.csv')

    with open(geonames_file_name, "r") as file2:
        lines_count = 0
        for line in file2:
            lines_count += 1
            
    with codecs.open(geonames_file_name, "r", "latin-1") as file1:
        count = 0
        for l in file1:
            words = l.split("\t")
            city_name = words[2]
            dept = words[5]
            if dept not in dict_dept:
                dict_dept[dept] = [city_name]
            else:
                tab = dict_dept.get(dept)
                tab.append(city_name)
            zone = Zone.objects.get(name=dept)

            try:
                city = City.objects.get(name=city_name, parent=zone)

            except City.DoesNotExist:
                city = City.objects.create(name=city_name, parent=zone)

            except City.MultipleObjectsReturned:
                cities = City.objects.filter(name=city_name, parent=zone)
                city = cities[0]
                for duplicated_city in cities.exclude(id=city.id):

                    for contact in duplicated_city.contact_set.all():
                        contact.city = city
                        contact.save()

                    for contact in duplicated_city.contact_billing_set.all():
                        contact.billing_city = city
                        contact.save()

                    for entity in duplicated_city.entity_set.all():
                        entity.city = city
                        entity.save()

                    for entity in duplicated_city.entity_billing_set.all():
                        entity.billing_city = city
                        entity.save()

                    duplicated_city.delete()

            city.district_id = words[8]
            city.latitude = float(words[9])
            city.longitude = float(words[10])
            city.geonames_valid = True
            city.country = u'France'
            city.zip_code = words[1]
            city.save()

            count += 1
            if count % 500 == 0:
                print(str(count) + "/" + str(lines_count))

    # Modify city names (already in the database) to correspond to GeoNames ones
    existing_cities = list(City.objects.filter(parent__parent__parent__name='France', geonames_valid=False))

    dept_code = ''
    for existing_city in existing_cities:
        try:
            if existing_city.parent.type.type != 'country':
                # Detect if the city name has already changed (0 if not / 1 if it changed)
                name_changed = 0
                city_name = remove_accents(existing_city.name.lower())
                cities_of_dept = dict_dept.get(existing_city.parent.name)
                dept_code = existing_city.parent.code
                if cities_of_dept:
                    matches = difflib.get_close_matches(city_name, cities_of_dept, cutoff=0.5)
                else:
                    matches = []
                if matches:
                    for match in matches:
                        if remove_accents(match.lower()) == city_name:
                            print("[saved] " + existing_city.name + " ---> " + match)
                            existing_city.name = match
                            existing_city.save()
                            name_changed = 1

                    if name_changed == 0:
                        if len(matches) == 0:
                            print("No result found")

                        elif len(matches) == 1:
                            special_cases(dept_code, existing_city, matches[0])
                            print("[Special Cases] " + existing_city.name)

                        elif len(matches) > 1:
                            possibilities = ""
                            for match in matches:
                                possibilities = possibilities + "|" + match
                            if possibilities != "":
                                special_cases(dept_code, existing_city, possibilities)
                            print("[Special Cases] " + existing_city.name)

        except TypeError as err:
            print('>>> TypeError', err)
            raise

        except UnicodeEncodeError:
            special_cases(dept_code, existing_city, "")
            pass
        except AttributeError:
            pass    
        
        
def update_doubles():
    """Update contacts and entities and remove the cities appearing twice or more"""
    # TODO : Est-ce qu'on est obligé de passer par cette suppression?
    cities = City.objects.filter(parent__parent__parent__name='France').order_by("name", "parent")
    prec = City(name="", parent=None)
    for c in cities:
        try:
            if c.district_id == "999":
                if len(c.parent.code) == 2:
                    c.district_id = c.parent.code + "0"
                elif len(c.parent.code) == 3:
                    c.dsitrict_id = c.parent.code
                c.save()
            if remove_accents(c.name.lower()) == remove_accents(prec.name.lower()) and c.parent==prec.parent:
                if c.geonames_valid and not prec.geonames_valid:
                    rightcity = c
                    wrongcity = prec
                else:
                    rightcity = prec
                    wrongcity = c
                contacts = Contact.objects.filter(city=wrongcity)
                for o in contacts:
                    o.city = rightcity
                    o.save()
                entities = Entity.objects.filter(city=wrongcity)
                for e in entities:
                    e.city = rightcity
                    e.save()
                wrongcity.delete()
                print("[deleted]  " + wrongcity.name)
                prec = rightcity
            else:
                prec = c
        except ValueError:
            pass
        except AssertionError:
            pass
        
        
def update_zip_code():
    """Give a zip code to cities that don't have one"""
    cities = City.objects.filter(zip_code="00000")
    for c in cities:
        try:
            haschanged = 0
            contacts = Contact.objects.filter(city=c)
            if contacts:
                contacts[0].city.zip_code = contacts[0].zip_code
                contacts[0].city.save()
                print("[saved] " + contacts[0].zip_code + "  " + contacts[0].city.name)
                haschanged = 1
            if haschanged == 0:
                entities = Entity.objects.filter(city=c)
                if entities:
                    entities[0].city.zip_code = entities[0].zip_code
                    entities[0].city.save()
                    print("[saved] " + entities[0].zip_code + "  " + entities[0].city.name)
        except UnicodeEncodeError:
            print("Unicode Error")
            pass


class Command(BaseCommand):
    """Command class"""

    def handle(self, *args, **options):
        """called when command is executed"""
        
        print("\n\nUpdating database, please wait ...\n\n")
        for m in City.objects.filter(country=None):
            if m.parent.type.name == 'Pays':
                m.country = m.parent.name
                m.save()
            elif m.parent.parent.type.name == 'Pays':
                m.country = m.parent.parent.name
                m.save()
            elif m.parent.parent.parent.type.name == 'Pays':
                m.country = m.parent.parent.parent.name
                m.save()
        
        choose = -1
        while choose != 0:        

            print("Choose the action :")
            print("\t[0] Quit")
            print("\t[1] Fill the database from \'geonames/FR.csv\'")
            print("\t[2] Manage special cases")
            print("\t[3] Update contacts and entities and delete cities appearing twice or more")
            print("\t[4] Update the zip code of all cities")
            print("\t[5] Run all\n\n")
            
            choose = int(raw_input("Enter the value of action : "))

            if choose == 1:
                fill_db()

            elif choose == 2:
                manage_spe_cases()

            elif choose == 3:
                update_doubles()

            elif choose == 4:
                update_zip_code()

            elif choose == 5:
                fill_db()
                manage_spe_cases()
                update_zip_code()
                update_doubles()
                return
