from trip_recommender import Trip_Recommender
import time

trip = Trip_Recommender(source=[43.797632, -79.421758], address='1203 Peter Kaiser Gate', postal_code='M3N 2H5',
                        specific_poi=False,trip_count=3, isCurrentLocation=False)
trip.get_resolution_data()
trip.plot()
time.sleep(5)

trip.setNewTrip(source=[43.797632, -79.421758], address='1203 Peter Kaiser Gate', postal_code='M3N 2H5',
                specific_poi=False,trip_count=3, isCurrentLocation=True)
trip.get_resolution_data()
trip.plot()
time.sleep(5)

trip.setNewTrip(source=[43.797632, -79.421758], address='300 Antibes Drive', postal_code='M2R 3N8',
                specific_poi=False,trip_count=3, isCurrentLocation=True)
trip.get_resolution_data()
trip.plot()
time.sleep(5)

trip.setNewTrip(source=[43.797632, -79.421758], address='300 Antibes Drive', postal_code='M2R 3N8',
                specific_poi=False,trip_count=3, isCurrentLocation=False)
trip.get_resolution_data()
trip.plot()
time.sleep(5)

trip.setNewTrip(source=[43.797632, -79.421758], address='1486 Aldergrove Dr, Oshawa,', postal_code='L1K 2Y4',
                specific_poi=False,trip_count=3, isCurrentLocation=True)
trip.get_resolution_data()
trip.plot()
time.sleep(5)

trip.setNewTrip(source=[43.797632, -79.421758], address='1486 Aldergrove Dr, Oshawa,', postal_code='L1K 2Y4',
                specific_poi=False,trip_count=3, isCurrentLocation=False)
trip.get_resolution_data()
trip.plot()
time.sleep(5)

trip.setNewTrip(source=[43.797632, -79.421758], address='1486 Aldergrove Dr, Oshawa,', postal_code='M8Z 1R1',
                specific_poi=False,trip_count=3, isCurrentLocation=False)
trip.get_resolution_data()
trip.plot()
time.sleep(5)

trip.setNewTrip(source=[43.797632, -79.421758], address='1486 Aldergrove Dr, Oshawa,', postal_code='M8Z 1R1',
                specific_poi=False,trip_count=3, isCurrentLocation=True)
trip.get_resolution_data()
#
# trip = Trip_Recommender(source=[43.931866, -79.451360], address='Richmond Hill, ON', postal_code='L4E 3S3',
#                 specific_poi=False,trip_count=3, isCurrentLocation=False)
# trip.get_resolution_data()
# print("\n\n\n\n")
# for p in trip.paths:
#     print(p.print())
# trip.plot()