from flask import Flask, render_template, request, session, flash
from trip_recommender import Trip_Recommender
from Location import Location

app = Flask(__name__)
app.secret_key = "some_complex_key"


@app.route('/', methods=['GET', 'POST'])
def home():
    print(request.args.to_dict(), len(request.args.to_dict()) != 0)

    if request.method == 'GET' and len(request.args.to_dict()) != 0:
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
            flash("Error! Make sure both fields are set", "info")

    init_map = Location()
    init_map.getGraph()

    return render_template("index.html", setMap="myLocation")


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


if __name__ == "__main__":
    app.run(debug=True)
