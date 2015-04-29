from django.shortcuts import render
from django.http import HttpResponse
from SPARQLWrapper import SPARQLWrapper, JSON
from django.views.generic.list import ListView
from django.utils import timezone
from events.models import Events
from datetime import date,timedelta,datetime
import urllib

endpoint="http://sumida.usc.edu:3030/Geocoded_Event/query"
sparql = SPARQLWrapper(endpoint)
select_prefix="""  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX schema: <http://schema.org/>
            SELECT ?s ?category ?name ?description ?image ?startDate ?endDate ?locationName ?streetAddress ?postalCode ?addressLocality ?addressRegion ?lat ?long ?superEvent 
            WHERE {
              ?s a <http://schema.org/Event>.
              optional{?s schema:category ?category.}
              ?s rdfs:label ?name.
              ?s schema:description ?description.
              ?s schema:image ?image.
              ?s schema:location ?location.
              ?s schema:startDate ?startDate.
              optional{?s schema:endDate ?endDate.}
              optional{?s schema:superEvent ?superEvent.}
              ?location rdfs:label ?locationName.
              ?location schema:address ?address.
              optional{?location schema:geo ?geo.
              ?geo schema:latitude ?lat.
              ?geo schema:longitude ?long.}
              ?address schema:streetAddress ?streetAddress.
              ?address schema:addressLocality ?addressLocality.
              ?address schema:addressRegion ?addressRegion.
              ?address schema:postalCode ?postalCode."""


def list_all(request):
    # sparql = SPARQLWrapper(endpoint)
    sparql.setQuery("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX schema: <http://schema.org/>
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
    return results

def search_form(request):
    results=list_all(request)["results"]["bindings"]
    for result in results:
      result['link']=result['s']['value'].split('.com/')[1]
    return render(request,"search_form.html",{"results":results})

def search(request):
    results={}
    endDate1=datetime.now().isoformat().split('.')[0]+'-07:00'
    if 'event_name' in request.GET and request.GET['event_name']:
        event_name = request.GET['event_name']
        # sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(
            select_prefix+
              """filter (regex(?name,\""""+event_name+"""\","i") || regex(?description,\""""+event_name+"""\","i"))
            }
            
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()["results"]["bindings"]
        
    elif 'within' in request.GET and request.GET['within']:
        endDate2=(datetime.now()+timedelta(days=int(request.GET['within']))).isoformat().split('.')[0]+'-07:00'
        
        # sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(
            select_prefix+
              """filter (?endDate > \""""+endDate1+"""\"^^xsd:dateTime
                && ?endDate < \""""+endDate2+"""\"^^xsd:dateTime)
            }
            ORDER BY ASC(?endDate)
            
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()["results"]["bindings"]
    elif 'category' in request.GET and request.GET['category']:
        category=request.GET['category']
        # sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(
            select_prefix+
              """filter (?category = \""""+category+"""\" && ?endDate > \""""+endDate1+"""\"^^xsd:dateTime)
            }
            ORDER BY ASC(?endDate)            
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()["results"]["bindings"]
    elif 'offset' in request.GET and request.GET['offset']:
        offset=request.GET['offset']
        # sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(
            select_prefix+
              """filter (?endDate > \""""+endDate1+"""\"^^xsd:dateTime)
            } 
            ORDER BY ASC(?endDate)
            limit 20
            OFFSET  """ +offset+ """
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()["results"]["bindings"]
    else:
        # sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(
            select_prefix+
              """filter (?endDate > \""""+endDate1+"""\"^^xsd:dateTime)
            } 
            ORDER BY ASC(?endDate)
            limit 20 
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()["results"]["bindings"]

    for (i,result) in enumerate(results):
        result['link']=result['s']['value'].split('.com/')[1]
        result['startDate']['value']=result['startDate']['value'][:-9].replace("T"," ").replace("-","/")
        if 'endDate' in result:
          result['endDate']['value']=result['endDate']['value'][:-9].replace("T"," ").replace("-","/")
        # sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(
        """
            PREFIX schema: <http://schema.org/>
            select distinct ?uri
            where {
                <"""+result['s']['value']+"""> schema:attendee ?uri.            
            }
        """)
        sparql.setReturnFormat(JSON)
        attendees = sparql.query().convert()["results"]["bindings"]
        result['attendees']=[]
        for attendee in attendees:
          attendee_name=attendee['uri']['value'].split('/')[-1].replace("_"," ")
          result['attendees'].append({'uri':attendee['uri']['value'],'name':attendee_name})
        
        if 'superEvent' in result:
          sparql.setQuery(
            """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX schema: <http://schema.org/>
                select distinct ?subEvent ?name
                where {
                    <"""+result['superEvent']['value']+"""> schema:subEvent ?subEvent.
                    ?subEvent rdfs:label ?name.
                }
            """)
          sparql.setReturnFormat(JSON)
          subEvents = sparql.query().convert()["results"]["bindings"]          
          result['subEvents']=[]
          for subEvent in subEvents:
            if subEvent['subEvent']['value']!=result['s']['value']:
              result['subEvents'].append({'uri':subEvent['subEvent']['value'],'name':subEvent['name']['value']})

    return render(request,'articlelist.html',{"results":results})
def event_detail(request,event_id):
    #event id = glendale-sparkle-and-share
    sparql.setQuery(select_prefix+"""
      filter (?s = <http://www.yelp.com/events/"""+event_id+""">)
        }
        limit 1
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return render(request,"detail.html",{"result":results["results"]["bindings"][0]})    
def map(request):
  return render(request,"events_map.html")

class EventsListView(ListView):

    # Events.objects.create(name="hello",description="go go go!")
    # model=results["results"]["bindings"]
    model=Events

    def get_context_data(self, **kwargs):
        context = super(EventsListView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context
