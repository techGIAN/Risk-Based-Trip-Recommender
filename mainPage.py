from flask import Flask, render_template, request, session, flash
from trip_recommender import Trip_Recommender
from Location import Location
from poi_near_me import POINearMe
from utilityMethods import SORT_BY

app = Flask(__name__)
app.secret_key = "some_complex_key"


def handlePathRequests(errMsg, errType):
    try:
        destination = request.args['destination']
        postal_code = request.args['postal']

        session['destination'] = destination
        session['postal_code'] = postal_code
        session['setDestination'] = True

        trip = Trip_Recommender(source=[43.8711, -79.4373], address=destination, postal_code=postal_code,
                                specific_poi=False, trip_count=5, isCurrentLocation=True)
        trip.getPaths()

        return render_template("index.html", setMap="recommender", destination=destination, postal_code=postal_code)

    except Exception as e:
        errMsg = "Error! Make sure both fields are set"
        errType = "recommender"


def handlePOIRequests(errMsg, errType):
    try:
        category = request.args['category']
        radius = request.args['radius']
        K_poi = request.args['K_poi']

        session['category'] = category
        session['radius'] = radius
        session['K_poi'] = K_poi

        p = POINearMe(radius=30, K_poi=20, category="Grocery Stores")
        p.graphPOIs()

        return render_template("index.html", setMap="poi_shower", category=category, radius=radius, K_poi=K_poi)
    except Exception as e:
        errMsg = "Error! Make sure both fields are set"
        errType = "poi_shower"


@app.route('/', methods=['GET', 'POST'])
def home():
    errMsg = ''
    errType = None

    if request.method == 'GET' and len(request.args.to_dict()) != 0:
        request_from = None
        try:
            request_from = request.args['submit_paths']
        except Exception as e:
            pass

        if request_from is not None:
            try:
                destination = request.args['destination']
                postal_code = request.args['postal']

                session['destination'] = destination
                session['postal_code'] = postal_code
                session['setDestination'] = True

                trip = Trip_Recommender(source=[43.8711, -79.4373], address=destination, postal_code=postal_code,
                                        specific_poi=False, trip_count=5, isCurrentLocation=True)
                trip.getPaths()

                return render_template("index.html", setMap="recommender", destination=destination, postal_code=postal_code)

            except Exception as e:
                errMsg = "Error! Make sure both fields are set"
                errType = "recommender"
        else:
            try:
                category = request.args['category']
                radius = int(request.args['radius'])
                K_poi = int(request.args['K_poi'])

                session['category'] = category
                session['radius'] = radius
                session['K_poi'] = K_poi
                print(radius, K_poi, category)
                p = POINearMe(radius=radius,
                              K_poi=K_poi,
                              poi=None,
                              duration=60,
                              category=category,
                              sortBy=SORT_BY.Time)
                print("\n\n\tDONE!!!!!\n\n")
                print(p.poi_list)
                p.graphPOIs()

                return render_template("index.html", setMap="poi_shower", category=category, radius=radius, K_poi=K_poi)
            except Exception as e:
                errMsg = "Error! Make sure both fields are set" + str(e)
                errType = "poi_shower"

    init_map = Location()
    init_map.getGraph()

    return render_template("index.html", setMap="myLocation", errMsg=errMsg, errType=errType)


@app.route('/myLocation')
def myLocation():
    init_map = Location()
    init_map.getGraph()

    return render_template("myLocation.html")


@app.route('/recommender')
def recommender():
    init_map = Location()
    init_map.getGraph()
    return render_template("recommender.html")


@app.route('/poi_near_me')
def poi_near_me():
    init_map = Location()
    init_map.getGraph()
    return render_template("poi_near_me.html")


if __name__ == "__main__":
    app.run(debug=True)
