# -*- coding: utf-8 -*-
from django.conf import settings

ALLOW_AUTO_TRANSLATE = getattr( settings, "ALLOW_AUTO_TRANSLATE", False )
ADMIN_URLS_PATTERN = getattr( settings, "ADMIN_URLS_PATTERN", "^/admin/" )

BABELFISH_ADMIN_CSS = getattr( settings, 
                          "BABELFISH_ADMIN_CSS",
                          ( "%scss/babelfish.css" % settings.MEDIA_URL, ) )

BABELFISH_ADMIN_JS = getattr( settings, 
                         "BABELFISH_ADMIN_JS",
                         ( "%sjs/jquery-1.4.2.min.js" % settings.MEDIA_URL,
                           "%sjs/babelfish.js" % settings.MEDIA_URL, ) )
