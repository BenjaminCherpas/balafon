# -*- coding: utf-8 -*-
"""admin"""

from django import forms
from django.db.models import CharField
from django.contrib import admin
from django.contrib.messages import success, error
from django.utils.translation import ugettext_lazy as _, ugettext

from sanza.Store import models
from sanza.Store.forms import StoreManagementActionTypeAdminForm


admin.site.register(models.Unit)
admin.site.register(models.DeliveryPoint)


class StoreItemInline(admin.TabularInline):
    """display property on the store item"""
    model = models.StoreItem
    fields = (
        'name', 'get_admin_link', 'category', 'purchase_price', 'price_policy', 'pre_tax_price',
        'vat_rate', 'available', 'stock_count', 'stock_threshold_alert'
    )
    readonly_fields = ['get_admin_link', 'stock_threshold_alert']


class StoreItemCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'active', 'get_all_articles_count')
    list_editable = ('active', )
    readonly_fields = ('get_all_articles_count',)
    inlines = (StoreItemInline, )


admin.site.register(models.StoreItemCategory, StoreItemCategoryAdmin)


class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = (StoreItemInline, )

admin.site.register(models.Brand, BrandAdmin)


class StoreItemTagAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'name', 'order_index', 'icon', 'active')
    list_editable = ('name', 'order_index', 'icon', 'active')

admin.site.register(models.StoreItemTag, StoreItemTagAdmin)


class SaleItemInline(admin.TabularInline):
    """display property on the store item"""
    model = models.SaleItem
    fields = ('text', 'item', 'quantity', 'pre_tax_price', 'vat_rate', 'order_index', 'is_blank')


class SaleAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'action')
    inlines = (SaleItemInline, )

admin.site.register(models.Sale, SaleAdmin)


class StoreManagementActionTypeAdmin(admin.ModelAdmin):
    """StoreManagementActionTypeAdmin"""
    form = StoreManagementActionTypeAdminForm

admin.site.register(models.StoreManagementActionType, StoreManagementActionTypeAdmin)


class StockThresholdFilter(admin.SimpleListFilter):
    """filter items which are below their stock threshold"""
    title = _(u'Stock level')
    parameter_name = 'stock_threshold_warning'

    THRESHOLD_ALERT = 1
    THRESHOLD_OK = 2
    THRESHOLD_NONE = 3

    def lookups(self, request, model_admin):
        return [
            (StockThresholdFilter.THRESHOLD_ALERT, ugettext("Threshold alert")),
            (StockThresholdFilter.THRESHOLD_OK, ugettext("Threshold ok")),
            (StockThresholdFilter.THRESHOLD_NONE, ugettext("Threshold missing")),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == StockThresholdFilter.THRESHOLD_NONE:
            return queryset.filter(stock_threshold__isnull=True)
        elif value in (StockThresholdFilter.THRESHOLD_ALERT, StockThresholdFilter.THRESHOLD_OK):
            warning_ids = []
            for item in queryset.filter(stock_threshold__isnull=False):
                if item.has_stock_threshold_alert():
                    warning_ids.append(item.id)
            if value == StockThresholdFilter.THRESHOLD_ALERT:
                return queryset.filter(id__in=warning_ids)
            else:
                return queryset.filter(stock_threshold__isnull=False).exclude(id__in=warning_ids)
        else:
            return queryset


class StoreCategoryFilter(admin.SimpleListFilter):
    """filter items which are below their stock threshold"""
    title = _(u'Store category')
    parameter_name = 'store_category'

    def lookups(self, request, model_admin):
        store_category = request.GET.get(self.parameter_name, None)

        if not store_category:
            # returns letters
            letters = sorted(set([category.name[0].upper() for category in models.StoreItemCategory.objects.all()]))
            return [('_'+letter, letter) for letter in letters]
        else:
            try:
                category = models.StoreItemCategory.objects.get(id=int(store_category))
                letter = category.name[0].upper()
            except ValueError:
                letter = store_category[1:]

            return [
                (category.id, category.name)
                for category in models.StoreItemCategory.objects.filter(
                    name__istartswith=letter
                ).extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
            ]

    def queryset(self, request, queryset):
        category = self.value()
        if category:
            try:
                return queryset.filter(category__id=int(category))
            except ValueError:
                return queryset.filter(category__name__istartswith=category[1:])
        return queryset


class StoreItemPropertyValueInline(admin.TabularInline):
    """display property on the store item"""
    model = models.StoreItemPropertyValue
    fields = ('property', 'value')


class StoreItemAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = [
        'fullname', 'brand', 'category', 'vat_rate', 'purchase_price', 'price_policy', 'pre_tax_price',
        'vat_incl_price', 'stock_count', 'stock_threshold_alert', 'available'
    ]
    ordering = ['name']
    list_filter = ['available', StockThresholdFilter, 'supplier', 'tags', StoreCategoryFilter]
    list_editable = ['available']
    search_fields = ['name', 'brand__name']
    readonly_fields = ['vat_incl_price', 'stock_threshold_alert']
    inlines = [StoreItemPropertyValueInline]
    list_per_page = 500
    save_as = True


admin.site.register(models.StoreItem, StoreItemAdmin)


class VatRateAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = [
        'name', 'is_default',
    ]
    readonly_fields = ['name']

admin.site.register(models.VatRate, VatRateAdmin)


def import_data(modeladmin, request, queryset):
    for import_file in queryset:
        import_file.import_data()
        if import_file.is_successful:
            success(
                request,
                _(u'The file {0} has been properly imported : {1} items have been created').format(
                    import_file, import_file.storeitem_set.count()
                )
            )
        else:
            error(
                request,
                _(u'Error while importing the file {0}: {1}').format(
                    import_file, import_file.error_message
                )
            )
import_data.short_description = _(u"Import")


class StoreItemImportAdmin(admin.ModelAdmin):
    """custom admin"""
    actions = [import_data]
    formfield_overrides = {
        CharField: {'widget': forms.TextInput(attrs={'size': 150})},
    }

admin.site.register(models.StoreItemImport, StoreItemImportAdmin)


admin.site.register(models.StoreItemProperty)

admin.site.register(models.Supplier)

admin.site.register(models.PricePolicy)
