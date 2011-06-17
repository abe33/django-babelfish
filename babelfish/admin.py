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
    
    # FIXME: auto translate conflict with admin
#    def get_object(self, request, object_id):
#        o = super( BabelFishAdmin, self ).get_object( request, object_id )
#        o.translate()
#        return o 
#    
#    def save_model(self, request, obj, form, change):
#        """
#        Given a model instance save it to the database.
#        """
#        obj.save()
    
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

admin.site.register( BabelFishDemoModel, BabelFishDemoModelAdmin )
