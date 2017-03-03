"""GMCustSent URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
import django.contrib.auth.views

from datetime import datetime
from django.conf.urls import url

import rankcars.forms
import rankcars.views



urlpatterns = [
    url(r'^$', rankcars.views.home, name='home'),
    url(r'^carselect', rankcars.views.carselect, name='carselect'),
    url(r'^selectcarsedmundsratings', rankcars.views.selectcarsedmundsratings, name='selectcarsedmundsratings'),
    #url(r'^weights', rankcars.views.weights, name='weights'),
    url(r'^componentresults', rankcars.views.componentresults, name='componentresults'),
    #url(r'^customweights', rankcars.views.customweights, name='customweights'),
    url(r'^edmundsratings', rankcars.views.edmundsratings, name='edmundsratings'),
    #url(r'contact$', rankcars.views.contact, name='contact'),
    url(r'^reviews', rankcars.views.reviews, name='reviews'),
    url(r'^graph', rankcars.views.graph, name='graph'),
    #url(r'about', rankcars.views.about, name='about'),
    url(r'^get_carmodels/([0-9]{1,4})/$', rankcars.views.get_carmodels, name='get_carmodels'),
    url(r'^get_caryears/([0-9]{1,4})/$', rankcars.views.get_caryears, name='get_caryears'),
    #url(r'login/$',
        #django.contrib.auth.views.login,
        #{
            #'template_name': 'rankcars/login.html',
            #'authentication_form': rankcars.forms.BootstrapAuthenticationForm,
            #'extra_context':
            #{
                 #'title': 'Log in',
                 #'year': datetime.now().year,
            #}
        #},
        #name='login'),
    #url(r'^logout$',
        #django.contrib.auth.views.logout,
        #{
             #'next_page': '/',
        #},
        #name='logout'),
    url(r'^runanalysis', rankcars.views.runanalysis, name='runanalysis'),
    url(r'^byedmundsratings', rankcars.views.byedmundsratings, name='byedmundsratings'),
    #url(r'^reviewcount', rankcars.views.reviewcount, name='reviewcount'),
    url(r'^admin/', admin.site.urls),
]
