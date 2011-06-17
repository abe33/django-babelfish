# -*- coding: utf-8 -*-
from django.conf import settings

ALLOW_AUTO_TRANSLATE = getattr( settings, "ALLOW_AUTO_TRANSLATE", False )
ADMIN_URLS_PATTERN = getattr( settings, "ADMIN_URLS_PATTERN", "^/admin/" )
