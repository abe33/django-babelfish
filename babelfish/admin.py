# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext as _
from django.conf import settings

from babelfish.models import *

class BabelFishAdmin( admin.ModelAdmin ):
    """I setup the admin medias required by the javascript enhancer.
    
    Extend me to create your own admin class for your translatable models.
    """
    def __init__(self, *args, **kwargs):
        super( BabelFishAdmin, self ).__init__( *args, **kwargs )
        
    class Media:
        css = {"all": ("%scss/babelfish.css" % settings.MEDIA_URL,)}
        js = (
                    "%sjs/jquery-1.4.2.min.js" % settings.MEDIA_URL,
                    "%sjs/babelfish.js" % settings.MEDIA_URL,
             )

class BabelFishDemoModelAdmin( BabelFishAdmin ):
    list_display=("name","slug",)
    fieldsets = [
        ( _(u'BabelFish'),  {'fields': ['bf_translations',] }),
        ( _(u'Content'),       {'fields': ['name','slug','description'] }),
    ]
    class Media:
        css = {"all": ("%scss/admin_enhancements.css" % settings.MEDIA_URL,)}
        js = (
                    "%sjs/jquery-1.4.2.min.js" % settings.MEDIA_URL,
                    "%sjs/ckeditor/ckeditor.js" % settings.MEDIA_URL,
                    "%sjs/admin_enhancements.js" % settings.MEDIA_URL,
                )

admin.site.register( BabelFishDemoModel, BabelFishDemoModelAdmin )
