import folium
import geocoder

WEBNAME = 'templates/myLocation.html'

class Location():
    source = None
    IS_DEBUG_MODE = False
    IS_FULL_DEBUG_MODE = False

    def __init__(self):
        self.source = geocoder.ip('me').latlng

    def getGraph(self):
        m = folium.Map(location=self.source, zoom_start=14)

        # markers
        folium.Marker(
            location=self.source,
            popup=self.source,
            icon=folium.Icon(color='blue', prefix='fa', icon='here')
        ).add_to(m)

        m.save(WEBNAME)

