from django.shortcuts import render

# Create your views here.
#

from django.urls import reverse ##gmo make sure this doesnt break anything. not sure where it came from
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import HttpRequest
from django.template import RequestContext, loader
from datetime import datetime
from forms import CarSelectForm, EdmundsCarSelectForm, GetCarForm
import scripts.sent_analysis as sa
import scripts.edmunds_ranking as er
import scripts.edmunds_reviews as ereviews
from django.forms.formsets import formset_factory
from models import CarMake, CarModel, CarYear
import scripts.show_reviews as sr
from django.shortcuts import get_object_or_404, render, render_to_response

import json as simplejson

def home(request):
    """Renders the home page """
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'rankcars/index.html',
        {
             'title':'Home Page',
             'year':datetime.now().year,
        }
    )


#def contact(request):
    #"""Renders the contact page. """
    #assert isinstance(request, HttpRequest)
    #return render(
        #request,
        #'app/contact.html',
        #{
             #'title':'Contact',
             #'message':'Your contact page',
             #'year':datetime.now().year,
        #}
    #)

#def about(request):
     #"""Renders the about page."""
     #assert isinstance(request, HttpRequest)
     #return render(
         #request,
         #'rankcars/about.html',
         #{
               #'title':'About',
               #'message':'Your application description page.',
               #'year':datetime.now().year,
         #}
     #)

def carselect(request):
    carformset = formset_factory(GetCarForm, extra=3)
    

    if request.method == 'POST':
        formset = carformset(request.POST)
        
        #print(formset.is_valid())
        requested_cars = []
        if(formset.is_valid()):
            for form in formset:
                if len(form.cleaned_data) > 0:
                    carmake = str(form.cleaned_data['carmake'])
                    carmodel = str(form.cleaned_data['carmodel'])
                    caryear = str(form.cleaned_data['caryear'])
                    requested_cars.append(str(carmake + '|' + carmodel + '|' + caryear))
            print(requested_cars)
            a,c = sa.hbase_connect(requested_cars)

            return render(
                request,
                'rankcars/componentresults.html',
                {
                     'a': a,
                     'c': c,
                }
            )
            #return HttpResponseRedirect('/runanalysis')
            #print(CarMake.objects.get(pk = request.POST.get("form-0-carmake")))
        else:
            massage = "something went wrong?!"

        #return render(request, 'rankcars/carselect.html', {'massage':massage})
        print('uh oh')
        return HttpResponse(formset)
    else:
        return render(request, 'rankcars/carselect.html', {'formset': carformset()})


def runanalysis(request):
    myMake1 = request.GET.get("form-0-carmake")
    return HttpResponse(myMake1)

def selectcarsedmundsratings(request):
    
    carformset = formset_factory(GetCarForm, extra=3)
    

    if request.method == 'POST':
        formset = carformset(request.POST)
        
        #print(formset.is_valid())
        requested_cars = []
        if(formset.is_valid()):
            for form in formset:
                if len(form.cleaned_data) > 0:
                    carmake = str(form.cleaned_data['carmake'])
                    carmodel = str(form.cleaned_data['carmodel'])
                    caryear = str(form.cleaned_data['caryear'])
                    requested_cars.append(str(carmake + '|' + carmodel + '|' + caryear))
            print(requested_cars)
            b, c = er.get_ratings(requested_cars)

            return render(
                request,
                'rankcars/edmundsratings.html',
                {
                     'b': b,
                     'c': c,
                }
            )
            #print(CarMake.objects.get(pk = request.POST.get("form-0-carmake")))
        else:
            massage = "something went wrong?!"

        print('uh oh')
        return HttpResponse(formset)
    else:
        return render(request, 'rankcars/selectcarsedmundsratings.html', {'formset': carformset()})


def byedmundsratings(request):
    myMake1 = request.GET.get("form1-make")
    myModel1 = request.GET.get("form1-model")
    myYear1 = request.GET.get("form1-year")

    myMake2 = request.GET.get("form2-make")
    myModel2 = request.GET.get("form2-model")
    myYear2 = request.GET.get("form2-year")
    
    myMake3 = request.GET.get("form3-make")
    myModel3 = request.GET.get("form3-model")
    myYear3 = request.GET.get("form3-year")

    requested_cars = []
    requested_cars.append(str(myMake1 + '|' + myModel1 + '|' + myYear1))
    requested_cars.append(str(myMake2 + '|' + myModel2 + '|' + myYear2))
    requested_cars.append(str(myMake3 + '|' + myModel3 + '|' + myYear3))

    b, c = er.get_ratings(requested_cars)

    return render(
        request,
        'rankcars/edmundsratings.html',
        {
            'b': b,
            'c': c,
        }
    )




#def weights(request):
    #assert isinstance(request, HttpRequest)
    #return render(
        #request,
        #'rankcars/weights.html',
        #{

        #}
    #)

def componentresults(request):
    assert isinstance(request, HttpRequest)
    return render(
         request,
         'rankcars/componentresults.html',
         {

         }
    )

#def customweights(request):
    #assert isinstance(request, HttpRequest)
    #return render(
        #request,
        #'rankcars/customweights.html',
        #{

        #}
    #)

def edmundsratings(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'rankcars/edmundsratings.html',
        {

        }
    )

def get_carmodels(request, carmake_id):
    carmake = CarMake.objects.get(pk = carmake_id)
    carmodels = CarModel.objects.filter(carmake = carmake)
    carmodel_dict = {}
    carmodel_dict[0] = '------------'
    for carmodel in carmodels:
        carmodel_dict[carmodel.id] = carmodel.name
    return HttpResponse(simplejson.dumps(carmodel_dict), content_type="application/json")

def get_caryears(request, carmodel_id):
    carmodel = CarModel.objects.get(pk = carmodel_id)
    caryears = CarYear.objects.filter(carmodel = carmodel)
    caryear_dict = {}
    caryear_dict[0] = '-------------'
    for caryear in caryears:
        caryear_dict[caryear.id] = caryear.name
    return HttpResponse(simplejson.dumps(caryear_dict), content_type="application/json")


def reviews(request):
    d = sr.car_reviews()


    return render(

        request,
        'rankcars/reviews.html',
        {
            'd': d
        }

    )



def graph(request):
    return render(
	request,
        'rankcars/graph.html'

    )
