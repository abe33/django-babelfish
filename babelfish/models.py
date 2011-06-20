# -*- coding: utf-8 -*-
import re

from django.db import models
from django.utils.translation import ugettext as _
from django.forms.widgets import Widget
from django.utils import simplejson
from django.conf import settings
from django.utils.safestring import mark_safe
from django import forms
from django.utils import translation
from babelfish import settings as babelfish_settings

models.options.DEFAULT_NAMES += ('auto_translate',)

class BabelFishWidget( Widget ):  
    """I display the translations statistiques for an instance
    in a table and create the script node that contains datas
    for the javascript enhancer.'""" 
 
    def __init__(self, *args, **kwargs ):
        super(BabelFishWidget,self).__init__(*args, **kwargs)
        
    def render(self, name, value, attrs=None):
        return mark_safe(u'''%s
                            <script text="text/javascript">
                                translations = %s;
                                languages = %s;
                                fields = %s;
                            </script>
                          ''' % ( self.get_table(attrs),
                                  simplejson.dumps(value) if value is not None else "null",
                                  simplejson.dumps( settings.LANGUAGES ),
                                  simplejson.dumps( self.translate_fields ) ) )
    
    def get_table(self, attrs):
        """I return the HTML code for the status table display instead of the classic widget."""
        
        th = "".join([ "<th>%s</th>" % o[0] for o in settings.LANGUAGES])
        td = "".join([ "<td id='id_stat_%s'>%s</td>" % ( o[0], o[0] ) for o in settings.LANGUAGES])
                
        s = """<table id='%s'>
                    <tr>%s</tr>
                    <tr>%s</tr>
               </table>""" % ( attrs["id"] ,th, td)
        
        return s
        
    def value_from_datadict(self, data, files, name):
        """I loop through all translatable fields for each lang
        and prepare the returned dict.
        
        When a field value is an empty string, the translations 
        slot is not filled. Then, if all of the translations slots
        are empty, I return None instead of a dict. This way the
        translations dictionary is always as small as possible, and
        it force the use of the defaults for not translated field instead
        of returning an empty string. 
        """
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
    """I currently only setup the widget."""
    widget = BabelFishWidget()
        
    def clean( self, value ):
        return value

class BabelFishField ( models.fields.Field ):
    """I store the translations data for all languages and all translatable fields.
    
    I also store in a property the translatable fields names and pass it to the form field widget.
    """
    __metaclass__ = models.SubfieldBase
    
    description = "A JSON dict which hold all the translations"
    
    def __init__ (self, translate_fields=None, *args, **kwargs ):
        self.translate_fields = translate_fields
        
        kwargs["null"]=True
        kwargs["blank"]=True
        kwargs["verbose_name"] = _(u"BabelFish Status")
        kwargs["help_text"] = _(u"Reminder : An empty translation will be ignored, and the default will be used instead.")
        
        super( BabelFishField, self ).__init__( *args, **kwargs)
    
    def get_internal_type(self):
        return 'TextField'
    
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
    
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)


class BabelFishModel( models.Model ):
    """I provide the stuff needed to convert a Model into
    a translatable model.
    
    Setup my translate_fields attribute to defines which properties
    I can handle while managing the model's field.
    
    I'll use the languages defined in settings.LANGUAGES to check
    which translations are allowed.
    """
    bf_current_lang = None
    bf_safe_defaults = None
    
    def __init__(self, *args, **kwargs):
        self.bf_safe_defaults = {}
    
        super( BabelFishModel, self ).__init__(*args, **kwargs)

        for k in self.translate_fields : 
            self.bf_safe_defaults[ k ] = self.__dict__[ k ]
        # need to pass the translatable fields to the bf_translations fields to setup the widget
        self._meta.get_field('bf_translations').translate_fields = self.translate_fields
        
        if hasattr( self._meta, "auto_translate") and self._meta.auto_translate and babelfish_settings.ALLOW_AUTO_TRANSLATE : 
            self.translate( translation.get_language() )
                
    def __getattr__(self, name):
        try:
            super(BabelFishModel, self).__getattr__(name)
        except:
            if self.is_query_property_name( name ):
                return self.get_query_property_value( name )
            else:
                raise
    
    def __setattr__(self, name, value ):
        # short circuit for the default dict
        if name == "bf_safe_defaults":
            super(BabelFishModel, self).__setattr__(name,value)
        elif self.is_query_property_name( name ):
            return self.set_query_property_value( name, value )
        else:
            try:
                super(BabelFishModel, self).__setattr__(name,value)
                # calling _set_property for translatable fields when current lang is not None
                if name in self.translate_fields and self.bf_current_lang is not None : 
                    self._set_property( name, self.bf_current_lang, value )
                # saving default data in the safe defaults dict
                elif name in self.translate_fields :
                    self.bf_safe_defaults[ name ] = value
            except:
                raise
    
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
        
        Once done, the instance is considered as translated and
        all translatable properties values are replaced by those
        of the selected language.
        
        Call me without any arguments to reset the instance
        with the defaults."""
        if lang == self.bf_current_lang :
            return

        self.bf_current_lang = lang
        
#        map = self._meta.__dict__["_name_map"]
#        for k in map:
#            if isinstance (getattr(self, k ), BabelFishModel):
#                getattr(self, k ).translate( lang )
        
        if self.bf_current_lang is None :
            for k in self.translate_fields :
#                self.__dict__[ k ] = self.bf_safe_defaults[ k ] 
                setattr( self, k, self.bf_safe_defaults[ k ] )
        else:
            for k in self.translate_fields :
#                self.__dict__[ k ] = self._get_property( k, self.bf_current_lang )
                setattr( self, k, self._get_property( k, self.bf_current_lang ) )
        
    
    def save (self):
        # we make sure that we save a not translated instance 
        if self.bf_current_lang is not None :
            self.translate()
        
        super( BabelFishModel, self ).save()
    
    class Meta :
        abstract = True

class BabelFishDemoModel ( BabelFishModel ):
    "A simple demo class with an admin and translatable and not-translatable fields"
    translate_fields = ('name','description')
    bf_translations = BabelFishField( translate_fields )
    
    name = models.CharField( "Name", max_length=50, null=True, blank=True )
    slug = models.CharField( "Slug", max_length=50, null=True, blank=True )
    description = models.TextField( "Description", null=True, blank=True )

    class Meta:
        auto_translate=False
    
    
    
