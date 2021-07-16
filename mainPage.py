from flask import Flask, render_template, request, session, flash, redirect, url_for
from trip_recommender import Trip_Recommender
from Location import Location
from poi_near_me import POINearMe
from utilityMethods import SORT_BY, ROUTE_FROM
import geocoder
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

geoloc = Nominatim(user_agent='TripRecApp')
geolocation = RateLimiter(geoloc.geocode, min_delay_seconds=2, return_value_on_exception=None)
from datetime import datetime
from termcolor import colored

app = Flask(__name__)
app.secret_key = "some_complex_key"

errMsg = ''
errType = None

RouteFrom = ROUTE_FROM.OSRM
trip = None
poiNearMe = None


# handles the form request to get directions for a specific location
def handlePathRequests():
    global errMsg, errType, trip
    try:
        destination = request.args['destination']
        origin = request.args['origin']
        time = request.args['time']
        mode_of_transit = request.args['mode_of_transit']

        session['time'] = time
        session['destination'] = destination
        session['origin'] = origin
        session['setDestination'] = True
        session['mode_of_transit'] = mode_of_transit

        if time == 'time_later':
            # get the time the user wants to leave
            try:
                date_time = request.args['date_time']
                session['date_time'] = date_time

            except Exception as es:
                errMsg = "Error! Please set the time when to leave or click 'leave now'"
                errType = "recommender"
                return
        else:
            session['date_time'] = None

        if trip is None:
            trip = Trip_Recommender(source=origin, destination=destination,
                                    trip_count=5, ROUTE_FROM=RouteFrom,
                                    mode_of_transit=mode_of_transit,
                                    IS_DEBUG_MODE=True,
                                    IS_FULL_DEBUG_MODE=True)
        else:
            trip.setNewTrip(source=origin, destination=destination,
                            trip_count=5, ROUTE_FROM=RouteFrom,
                            mode_of_transit=mode_of_transit,
                            IS_DEBUG_MODE=True,
                            IS_FULL_DEBUG_MODE=True)

        trip.plot()

    except Exception as e:
        errMsg = "Error! Make sure all fields are set"
        errType = "recommender"


# handles the form request to get points of interest
def handlePOIRequests():
    global errMsg, errType, poiNearMe
    try:
        category = request.args['category']
        radius = request.args['radius']
        K_poi = request.args['K_poi']
        center = request.args['center']
        sort_by = request.args['sort_by']
        travel_poi = request.args['travel_poi']
        time = request.args['time_poi']

        session['time_poi'] = time
        session['travel_poi'] = travel_poi
        session['category'] = category
        session['radius'] = radius
        session['K_poi'] = K_poi
        session['center'] = center
        session['sort_by'] = sort_by

        s = None
        if sort_by == 'time_of_traver':
            s = SORT_BY.Time
        elif sort_by == 'distance_to_travel':
            s = SORT_BY.Distance
        elif sort_by == 'risk_of_trip':
            s = SORT_BY.Risk
        else:
            s = SORT_BY.POIScore

        travel = None
        if travel_poi == 'car_poi':
            travel = 'car'
        elif travel_poi == 'walk_poi':
            travel = 'foot'
        else:
            travel = 'bike'

        date_time = None

        if time == 'time_later_poi':
            # get the time the user wants to leave
            try:
                date_time = request.args['date_time_poi']
                session['date_time_poi'] = date_time

            except Exception as es:
                errMsg = "Error! Please set the time when to leave or click 'leave now'"
                errType = "recommender"
                return
        else:
            session['date_time_poi'] = None

        is_time_now = time == 'time_now_poi'

        if poiNearMe is None:
            poiNearMe = POINearMe(origin=center,
                                  radius=int(radius),
                                  K_poi=int(K_poi),
                                  category=category,
                                  sortBy=s,
                                  ROUTE_FROM=RouteFrom,
                                  travel_by=travel,
                                  IS_DEBUG_MODE=True,
                                  IS_FULL_DEBUG_MODE=True,
                                  is_time_now=is_time_now,
                                  time_later_val=date_time)
        else:
            poiNearMe.update_request(origin=center,
                                     radius=int(radius),
                                     K_poi=int(K_poi),
                                     category=category,
                                     sortBy=s,
                                     ROUTE_FROM=RouteFrom,
                                     travel_by=travel,
                                     IS_DEBUG_MODE=True,
                                     IS_FULL_DEBUG_MODE=True,
                                     is_time_now=is_time_now,
                                     time_later_val=date_time)

        poiNearMe.graphPOIs()

    except Exception as e:
        errMsg = "Error! Make sure both fields are set " + str(e)
        errType = "poi_shower"


@app.route('/', methods=['GET', 'POST'])
def home():
    global errMsg, errType, RouteFrom
    errMsg = ''
    errType = None

    if RouteFrom == ROUTE_FROM.OSRM:
        session['query_from'] = 'osrm'
    else:
        session['query_from'] = 'grass_hopper'

    if request.method == 'GET' and len(request.args.to_dict()) != 0:
        print(colored('received a get request', 'red'))
        request_from = None

        # -----------------------------------------
        # request a path for a specified location
        try:
            request_from = request.args['submit_paths']
        except Exception as e:
            pass

        if request_from is not None:
            print(colored('\tPATHS', 'red'))
            handlePathRequests()

            if errType is None:
                return render_template("index.html",
                                       setMap="recommender",
                                       destination=request.args['destination'],
                                       origin=request.args['origin'])
            else:
                init_map = Location()
                init_map.getGraph()
                return render_template("index.html", setMap="myLocation", errMsg=errMsg, errType=errType)

        # -----------------------------------------
        # request to set origin as current location
        try:
            request_from = request.args['compass.x']
        except Exception as e:
            pass

        if request_from is not None:
            location = geoloc.geocode(geocoder.ip('me').latlng)
            session['origin'] = str(location.address)

            init_map = Location()
            init_map.getGraph()
            return render_template("index.html", setMap="myLocation", errMsg=errMsg, errType=errType)

        # -----------------------------------------
        # request to set center to current location (for 2nd form)
        try:
            request_from = request.args['compass_poi.x']
        except Exception as e:
            pass

        if request_from is not None:
            location = geoloc.geocode(geocoder.ip('me').latlng)
            session['center'] = str(location.address)

            init_map = Location()
            init_map.getGraph()
            return render_template("index.html", setMap="myLocation", errMsg=errMsg, errType=errType)

        # -----------------------------------------
        # request to get POI's near a specified area
        try:
            request_from = request.args['submit_poi']
        except Exception as e:
            pass

        if request_from is not None:
            print(colored('\tPOI', 'red'))
            handlePOIRequests()

            if errType is None:
                return render_template("index.html", setMap="poi_shower")

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


@app.route('/setType', methods=['GET', 'POST'])
def setType():
    global RouteFrom
    try:
        type = request.args['type']
        session['query_from'] = type

        if type == 'osrm':
            RouteFrom = ROUTE_FROM.OSRM
        else:
            RouteFrom = ROUTE_FROM.GRASS_HOPPER
    except Exception as e:
        pass

    print(colored('route from =' + str(RouteFrom), 'red'))
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
