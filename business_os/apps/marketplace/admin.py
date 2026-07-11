from django.contrib import admin

from business_os.apps.marketplace.models import (
    Bundle,
    BundleItem,
    Capability,
    Module,
    ModuleCapability,
    ModuleDependency,
    ModuleLimit,
    ModulePrice,
)

admin.site.register(Module)
admin.site.register(Capability)
admin.site.register(ModuleCapability)
admin.site.register(ModuleDependency)
admin.site.register(ModulePrice)
admin.site.register(ModuleLimit)
admin.site.register(Bundle)
admin.site.register(BundleItem)

