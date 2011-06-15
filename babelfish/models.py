# -*- coding: utf-8 -*-
import re

from django.db import models
from django.utils.translation import ugettext as _
from django.forms.widgets import Widget
from django.utils import simplejson
from django.conf import settings
from django.utils.safestring import mark_safe
from django import forms

class BabelFishWidget( Widget ):  
    """I'm an hidden field which a script node that contains
    data for the javascript enhancer.'""" 
    translate_fields = ()
 
    def __init__(self):
        super(BabelFishWidget,self).__init__()
        
    def render(self, name, value, attrs=None):
        return mark_safe(u'''<script text="text/javascript">
                                translations = %s
                                languages = %s;
                                fields = %s;
                            </script>
                          ''' % ( 
                                  simplejson.dumps(value) if value is not None else "",
                                  simplejson.dumps( settings.LANGUAGES ),
                                  simplejson.dumps( self.translate_fields ) ) )
    
    def value_from_datadict(self, data, files, name):
        translations = {}
        langs = [ o[0] for o in settings.LANGUAGES ]
        fields = self.translate_fields
        has_translations = False
        
        for lang in langs : 
            for field in fields : 
                field_name = "%s_%s" % ( field, lang )
                value = data.get( field_name, "" )
                
                if value != "" : 
                    has_translations = True
                    
                    if not translations.has_key( lang ):
                        translations[ lang ] = {}
                    
                    translations[lang][ field ] = value
             
        if has_translations : 
            return translations
        else :
            return None

class BabelFishFormField ( forms.CharField ):

    widget = BabelFishWidget()
    
    def __init__ (self, *args, **kwargs):
        for k in kwargs :
            self.__dict__[k]=kwargs[k]
        super( BabelFishFormField, self ).__init__()
    
    def clean ( self, value ):
        return value

class BabelFishField ( models.Field ):
    """I store the translations data for all languages and all translatable fields.
    
    I also store in a property the translatable fields names and pass it to the form field widget.
    """
    __metaclass__ = models.SubfieldBase
    
    description = "A JSON dict which hold all the translations"
    translate_fields = ()
    
    def get_internal_type(self):
        return 'CharField'
    
    def formfield(self, **kwargs):
        kwargs["form_class"] = BabelFishFormField
        f = super(BabelFishField, self).formfield(**kwargs)
        f.widget.translate_fields = self.translate_fields
        return f
    
    def to_python(self, value):
        if value is None or value == "":
            return None
        elif isinstance(value, dict):
            return value
        elif isinstance(value, unicode) or isinstance(value, str):
            return simplejson.loads( value )
        else:
            return None
    
    def get_prep_value(self, value):
        if value is None : 
            return "" 
        else:
            return simplejson.dumps( value )   

class BabelFishModel( models.Model ):
    """I provide the stuff needed to convert a Model into
    a translatable model.
    
    Setup my translate_fields attribute to defines which properties
    I can handle while managing the model's field.
    
    I'll use the languages defined in settings.LANGUAGES to check
    which translations are allowed.
    """
    bf_current_lang = None
    bf_safe_defaults = {}
    bf_translations = BabelFishField(_(u"Translations"), 
                                        null=True,
                                        blank=True,
                                        help_text=_(u"Contains serialized translations for each language") )
    
    translate_fields = ()  
    
    def __init__(self, *args, **kwargs):
        super( BabelFishModel, self ).__init__(*args, **kwargs)
        
        for k in self.translate_fields : 
            self.bf_safe_defaults[ k ] = self.__dict__[ k ]
            
        # need to pass the translatable fields to the bf_translations fields to setup the widget
        self._meta.get_field('bf_translations').translate_fields = self.translate_fields
     
    def __getattr__(self, name):
        "I allow to access translatable properties with the lang suffix."
        
        try:
            super(BabelFishModel, self).__getattr__(name)
        except:
            if self.is_query_property_name( name ):
                return self.get_query_property_value( name )
            else:
                raise
    
    def __setattr__(self, name, value ):
        "I allow to set translatable properties with the lang suffix."
        if self.is_query_property_name( name ):
            return self.set_query_property_value( name, value )
        else:
            super(BabelFishModel, self).__setattr__(name,value)
            # calling _set_property for translatable fields when current lang is not None
            if name in self.translate_fields and self.bf_current_lang is not None : 
                self._set_property( name, self.bf_current_lang, value )
    
    def is_query_property_name( self, name ):
        "I verify that the property name query is valid."
        
        return self.get_query_property_re().match( name ) is not None 
    
    def get_query_property_value( self, name ):
        "I return the value of the property according to the lang."
        
        match = self.get_query_property_re().match( name )
        name = match.group(1)
        lang = match.group(2)
        return self._get_property( name, lang )
    
    def set_query_property_value( self, name, value ):
        "I set the value of the property according to the lang."
        
        match = self.get_query_property_re().match( name )
        name = match.group(1)
        lang = match.group(2)
        return self._set_property( name, lang, value )
    
    def get_query_property_re( self ):
        "I return the regular expression which match a valid property query."
        
        re_properties = "|".join( self.translate_fields )
        re_languages = "|".join([ o[0][:2] for o in settings.LANGUAGES ])
        test = re.compile( "(%s)_(%s)" % ( re_properties, re_languages ) )
        return test
    
    def _get_property( self, name, lang ):
        "I return the value of the translatable field."
        
        if name not in self.translate_fields : 
            raise
        
        if lang is None : 
            return self.bf_safe_defaults[ name ]     
          
        elif self.bf_translations is not None and lang in self.bf_translations :
            trans = self.bf_translations[ lang ]
            if name in trans : 
                return trans[ name ]
            elif name in self.bf_safe_defaults :
                return self.bf_safe_defaults[ name ]
            else:
                raise
    
        elif name in self.bf_safe_defaults :
            return self.bf_safe_defaults[ name ]
            
        else:
            raise

    def _set_property( self, name, lang, value ):
        """I set the value of a translatable field for the corresponding
        language.
        
        If the language translations don't exist, the dict is created.'"""
        if name not in self.translate_fields : 
            raise
        
        # no lang, we set the default
        if lang is None :
            self.bf_safe_defaults[ name ] = value 
            return self.bf_safe_defaults[ name ] 
        
        # no translations, we create it
        if self.bf_translations is None:
            self.bf_translations = {}
        if lang not in self.bf_translations: 
            self.bf_translations[lang] = {}
        
        self.bf_translations[lang][name] = value
        
        return self.bf_translations[lang][name]
    
    def translate( self, lang = None ):
        """I swap the language for this instance.
        
        All translatable properties values are replaced by those of the
        selected language."""
        if lang == self.bf_current_lang :
            return

        self.bf_current_lang = lang
        
        if self.bf_current_lang is None :
            for k in self.translate_fields :
                self.__dict__[ k ] = self.bf_safe_defaults[ k ] 
        else:
            for k in self.translate_fields :
                self.__dict__[ k ] = self._get_property( k, self.bf_current_lang )


class BabelFishDemoModel ( BabelFishModel ):
    "A simple demo class with an admin and translatable and not-translatable fields"
    translate_fields = ('name','description')
    
    name = models.CharField( "Name", max_length=50, null=True, blank=True )
    slug = models.CharField( "Slug", max_length=50, null=True, blank=True )
    description = models.TextField( "Description", null=True, blank=True )
    
    
    
