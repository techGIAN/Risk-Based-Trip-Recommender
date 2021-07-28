import folium
import geocoder
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

geoloc = Nominatim(user_agent='TripRecApp')
geolocation = RateLimiter(geoloc.geocode, min_delay_seconds=2, return_value_on_exception=None)

WEBNAME = 'templates/myLocation.html'


class Location():
    source = None
    IS_DEBUG_MODE = False
    IS_FULL_DEBUG_MODE = False
    GDF_FILE = 'hex_gdf.csv'
    time_now = True
    time_later_value = None
    results_html = None

    def __init__(self):
        self.source = geocoder.ip('me').latlng

    def get_results(self):
        return self.results_html

    def getGraph(self):
        m = folium.Map(location=self.source, zoom_start=14)

        # markers
        folium.Marker(
            location=self.source,
            popup=self.source,
            icon=folium.Icon(color='blue', prefix='fa', icon='here')
        ).add_to(m)

        m.save(WEBNAME)

    # gets the geocoordinates of a location
    # requires either one of postal code or address
    # note: postal code takes precedence
    def get_coordinates(self, ad):
        location = geoloc.geocode(ad)
        return [location.latitude, location.longitude]

