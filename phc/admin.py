from django.contrib import admin
from .models import *

# Register the Partners model without customizing list_display
admin.site.register(Partners)
admin.site.register(Subcounty)
