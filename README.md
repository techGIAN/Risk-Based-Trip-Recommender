#### Updated Toronto POIs risks' file (with normal, skewed and uniform distributions) is located in: https://drive.google.com/file/d/1VMbcir9q4-l_ODvDG60Yrzei3i_5iIDy/view?usp=sharing 

***





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

## Datasets
Link here: https://drive.google.com/drive/folders/1aTrklikj97VsuOBSC1Xk86uOb8QYRVxG?usp=sharing

and here: https://drive.google.com/drive/folders/1O3ZPLvYV6_P8lyms-3R-7pOqNm_CwPfK?usp=sharing
* POI Risk Map: ```GTA_risks.csv```
* Hex Risk Map: ```hex_gdf.csv```
***
### Faster Processing
Link here: https://drive.google.com/drive/folders/1O3ZPLvYV6_P8lyms-3R-7pOqNm_CwPfK?usp=sharing
To make the files run faster, use:
* Past trips recorded: ```df_trips.csv```
* Past coordinate recorder: ```df_past_coordinates_search.csv```

## Usage
Run <code>mainPage.py</code>, copy the url and paste into the browser. 

## Evaluation
To evaluate the program, run:
1. ```POI-Explorer.ipynb``` for the POIs in the GTA
2. ```POI_risk_calculator.ipynb``` for the extrapolated, hourly POI risks following skewed, normal, and uniform distributions.
3. ```queries_generator.py``` to generate random queries in Toronto
4. ```QueryProcessor.ipynb``` to process the queries from step 3
5. ```animate.py``` to animate the results

