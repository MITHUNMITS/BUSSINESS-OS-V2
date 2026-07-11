from django.contrib import admin

from business_os.apps.catalogue.models import (
    Category,
    Collection,
    CollectionItem,
    Offering,
    OfferingImage,
    OfferingVariant,
    OptionDefinition,
    OptionValue,
)

admin.site.register(Category)
admin.site.register(Collection)
admin.site.register(CollectionItem)
admin.site.register(Offering)
admin.site.register(OfferingVariant)
admin.site.register(OfferingImage)
admin.site.register(OptionDefinition)
admin.site.register(OptionValue)
