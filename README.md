# Risk-Based-Trip-Recommender
An individual trip-recommendation system based on risk of epidemic infection and distance of trip

## Need to change a code locally:
Go to folium/plugins/marker_cluster.py or right click on MarkerCluster in poi_near_me.py
change the \_\_init\_\_ method to include the tooltip values:
```
def __init__(self, locations=None, popups=None, icons=None, name=None,
                 overlay=True, control=True, show=True, tooltip_strings=None,
                 icon_create_function=None, options=None, **kwargs):
        if options is not None:
            kwargs.update(options)  # options argument is legacy
        super(MarkerCluster, self).__init__(name=name, overlay=overlay,
                                            control=control, show=show)
        self._name = 'MarkerCluster'

        if locations is not None:
            locations = validate_locations(locations)
            for i, location in enumerate(locations):
                self.add_child(Marker(location,
                                      popup=popups and popups[i],
                                      icon=icons and icons[i],
                                      tooltip=tooltip_strings and tooltip_strings[i]))

        self.options = parse_options(**kwargs)
        if icon_create_function is not None:
            assert isinstance(icon_create_function, str)
        self.icon_create_function = icon_create_function
```

## SafeGraph Data
Use https://drive.google.com/drive/folders/1aTrklikj97VsuOBSC1Xk86uOb8QYRVxG?usp=sharing: ```ca_poi_rrisks_2021-04-19-one-week.csv```

## Usage
Run <code>mainPage.py</code>, copy the url and paste into the browser. 


