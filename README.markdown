django-babelfish
================
*So long, and thanks for the fish.*

Warning : As it is, django-babelfish should be considered as a developpment version.

-------

Installation
------------
Download the sources and made it available within your `python path`.

Copy, or symlink, the files in `medias` in your own media directory.
Theses files are used in the admin to build and style the translations fields
in the admin forms.

Configuration
-------------
Defines the supported languages in a `LANGUAGES` setting in your `settings.py`.

    LANGUAGES = (
        ("en", "English"),
        ("fr", "French"),
    )

There's no need to add `babelfish` to your `INSTALLED_APPS`, but 
if you want to quickly try BabelFish you can add it, and then you'll 
make available in the admin the `BabelFishDemoModel` class. This class
demonstrate how a translatable model interact with the admin.

Creating a translatable model
-----------------------------
The class `babelfish.models.BabelFishDemoModel` demonstrate how to setup a class 
to made it available for BabelFish translation. But to save you the time to search in the sources, 
I'll describe the setup below.
    
    from django.db import models
    from babelfish.models import BabelFishModel, BabelFishField
    
    class MyTranslatableModel ( BabelFishModel ):
    
        translate_fields = ('name','description')
        bf_translations = BabelFishField( translate_fields, "BabelFish Translations" )
        
        name = models.CharField( "Name", max_length=100 )
        slug = models.CharField( "Slug", max_length=100 )
        
        description = models.TextField("Description")
        
1. Make your model extend `BabelFishModel`.
2. Define a `translate_fields` tuple in your class with the name of fields to translate.
3. Define a `bf_translations` field of type `BabelFishField` in your class, pass `translate_fields`
   as its first argument. The field need to know which fields are concerned in order to allow the form's
   field and the widget to know the fields as well. That's why this field cannot be defined in `BabelFishModel` since
   Django create form's field for a class before the `__init__` of this class.
4. Sync your database using the `./manage.py syncdb` command to create the corresponding column.

How it works
------------
The `BabelFishField` is a `TextField` which store all the translations for the translatable fields 
in a `dict` serialized using JSON.

This way there's no need to sync the database when adding a new language or when making a new field
in your model available for translation.

In the same way, making a model translatable doesn't break its fixtures, since the column name for the
translatable fields doesn't change. That means that you doesn't have to bother to make a model translatable
unless you need it, and once you need it, the change will not break all your previous content.

API 
---

    >>> m = MyTranslatableModel( name="This is my name", description="This is my description", slug="sample" )
    >>> m.name 
    "This is my name"
    >>> m.description
    "This is my description"
    
    >>> m.name_fr # translations are available with the lang suffix
    "This is my name" # if no translations are defined, the default is returned
    
    >>> m.name_fr = "Ceci est mon nom"
    >>> m.description_fr = "Ceci est ma description"
    
    >>> m.name_fr
    "Ceci est mon nom"
    
    >>> m.translate('fr') # call translate with a language code to swap the instance
    >>> m.name 
    "Ceci est mon nom"
    >>> m.description
    "Ceci est ma description"
    
    >>> m.name = "Mon nom est personne" # setting the field on a translated instance set the translations
    >>> m.name
    "Mon nom est personne"
    >>> m.name_fr 
    "Mon nom est personne"
    
    >>> m.translate() # calling translate without argument reset the instance
    >>> m.name
    "This is my name"
    
    >>> m.name_it # will raise an error if the it language is not defined in LANGUAGES
    >>> m.slug_fr # will raise an since slug is not translatable

Admin integration
-----------------

    from django.contrib import admin
    from babelfish.admin import BabelFishAdmin
    
    class MyTranslatableAdmin ( BabelFishAdmin ):
        list_display=("name","slug",)
        fieldsets = [
            ( _(u'BabelFish'),  {'fields': ['bf_translations',] }),
            ( _(u'Content'),    {'f ields': ['name','slug','description'] }),
        ]

    admin.site.register( MyTranslatableModel, MyTranslatableAdmin )

As you can notice, I explicitely add the `bf_translations` to the fieldsets. It
will allow the `BabelFishWidget` to be rendered and the setup script will have the
required setup.


Actually, the `BabelFishWidget` display, instead of the `TextField` widget, a table
with statistics for translations in the current instance. 

The widgets to edit translations are cloned by the `babelfish.js` script from the
original widget of each translatable fields. 

