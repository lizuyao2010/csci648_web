from django.shortcuts import render
from django.http import HttpResponse
from SPARQLWrapper import SPARQLWrapper, JSON
from django.views.generic.list import ListView
from django.utils import timezone
from events.models import Events

def list(request):
    sparql = SPARQLWrapper("http://localhost:3030/ds/query")
    sparql.setQuery("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix schema: <http://schema.org/>
        SELECT ?s ?name ?description ?image
        WHERE {
          ?s a <http://schema.org/Event>.
          ?s rdfs:label ?name.
          ?s schema:description ?description.
          ?s schema:image ?image.
        }
        limit 20
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    # for result in results["results"]["bindings"]:
    #     # print result["label"]["value"]
    #     print result["s"]["value"],result["r"]["value"],result["o"]["value"]
    return render(request,"list.html",{"results":results["results"]["bindings"]})

def detail(request):
    sparql = SPARQLWrapper("http://localhost:3030/ds/query")
    sparql.setQuery("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix schema: <http://schema.org/>
        SELECT ?name ?description ?image ?startDate ?endDate ?locationName ?streetAddress ?postalCode ?addressLocality ?addressRegion 
        WHERE {
          ?s a <http://schema.org/Event>.
          ?s rdfs:label ?name.
          ?s schema:description ?description.
          ?s schema:image ?image.
          ?s schema:location ?location.
          ?s schema:startDate ?startDate.
          ?s schema:startDate ?endDate.
          ?location rdfs:label ?locationName.
          ?location schema:address ?address.
          ?address schema:streetAddress ?streetAddress.
          ?address schema:addressLocality ?addressLocality.
          ?address schema:addressRegion ?addressRegion.
          ?address schema:postalCode ?postalCode.
          filter (?s = <http://www.yelp.com/events/glendale-sparkle-and-share>)
        }
        limit 10
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return render(request,"detail.html",{"result":results["results"]["bindings"][0]})

def search_form(request):
    return render(request,"search_form.html")

def search(request):
    if 'event_name' in request.GET and request.GET['event_name']:
        event_name = request.GET['event_name']
        sparql = SPARQLWrapper("http://localhost:3030/ds/query")
        sparql.setQuery("""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            prefix schema: <http://schema.org/>
            SELECT ?name ?description ?image ?startDate ?endDate ?locationName ?streetAddress ?postalCode ?addressLocality ?addressRegion 
            WHERE {
              ?s a <http://schema.org/Event>.
              ?s rdfs:label ?name.
              ?s schema:description ?description.
              ?s schema:image ?image.
              ?s schema:location ?location.
              ?s schema:startDate ?startDate.
              ?s schema:startDate ?endDate.
              ?location rdfs:label ?locationName.
              ?location schema:address ?address.
              ?address schema:streetAddress ?streetAddress.
              ?address schema:addressLocality ?addressLocality.
              ?address schema:addressRegion ?addressRegion.
              ?address schema:postalCode ?postalCode.
              filter (regex(?name,\""""+event_name+"""\","i"))
            }
            limit 10
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        return render(request,'list.html',{"results":results["results"]["bindings"]})
    else:
        message = 'You submitted an empty form.'
        return HttpResponse(message)

def event_detail(request,event_id):
    sparql = SPARQLWrapper("http://localhost:3030/ds/query")
    #event id = glendale-sparkle-and-share
    sparql.setQuery("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix schema: <http://schema.org/>
        SELECT ?name ?description ?image ?startDate ?endDate ?locationName ?streetAddress ?postalCode ?addressLocality ?addressRegion 
        WHERE {
          ?s a <http://schema.org/Event>.
          ?s rdfs:label ?name.
          ?s schema:description ?description.
          ?s schema:image ?image.
          ?s schema:location ?location.
          ?s schema:startDate ?startDate.
          ?s schema:startDate ?endDate.
          ?location rdfs:label ?locationName.
          ?location schema:address ?address.
          ?address schema:streetAddress ?streetAddress.
          ?address schema:addressLocality ?addressLocality.
          ?address schema:addressRegion ?addressRegion.
          ?address schema:postalCode ?postalCode.
          filter (?s = <http://www.yelp.com/events/"""+event_id+""">)
        }
        limit 1
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return render(request,"detail.html",{"result":results["results"]["bindings"][0]})    


class EventsListView(ListView):

    # Events.objects.create(name="hello",description="go go go!")
    # model=results["results"]["bindings"]
    model=Events

    def get_context_data(self, **kwargs):
        context = super(EventsListView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context
