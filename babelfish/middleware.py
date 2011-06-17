# -*- coding: utf-8 -*-
import re

from django.contrib.auth.models import User, AnonymousUser
from django.utils import translation

from babelfish import settings as babelfish_settings

class UserAgentLangMiddleware():

    def process_request( self, request):
        if re.match( babelfish_settings.ADMIN_URLS_PATTERN, request.META["PATH_INFO"] ) is not None : 
            babelfish_settings.ALLOW_AUTO_TRANSLATE = False
        else:
            babelfish_settings.ALLOW_AUTO_TRANSLATE = True
        
        language = translation.get_language_from_request(request)
        translation.activate(language)

class DefaultLangMiddleware():

    def process_request( self, request):
        session = request.session
        
        if re.match( babelfish_settings.ADMIN_URLS_PATTERN, request.META["PATH_INFO"] ) is not None : 
            babelfish_settings.ALLOW_AUTO_TRANSLATE = False
        else:
            babelfish_settings.ALLOW_AUTO_TRANSLATE = True
        
        if request.GET.has_key("lang"):
            language = request.GET["lang"]
            session["language"] = language
        elif "language" in session : 
            language = session["language"]
        else :
            language = translation.get_language_from_request(request)
            session["language"] = language
        
        translation.activate(language)
