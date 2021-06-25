from trip_recommender import Trip_Recommender
from utilityMethods import ROUTE_FROM

class POI(Trip_Recommender):
    poi_risk = None

    def __init__(self, coordinate, origin, isCurrentLocation=True, ROUTE_FROM=ROUTE_FROM.OSRM):
        super().__init__(source=origin, address=None,
                         postal_code=None, specific_poi=False, trip_count=3,
                         isCurrentLocation=isCurrentLocation, destination_coordinates=True,
                         destination=coordinate, ROUTE_FROM=ROUTE_FROM)

        # TO DO
        # compute POI risk and update it accordingly

    # filter out paths based on distance and time to get to the location
    def filter(self, dist_filter, time_filter):
        for index in reversed(range(len(self.paths))):
            if not (self.paths[index].total_distance <= dist_filter and
                    self.paths[index].total_duration <= time_filter):
                self.paths.pop(index)

    # return min travel time
    def getTime(self):
        minT = self.paths[0].total_duration

        for i in range(1, len(self.paths)):
            if self.paths[i].total_duration < minT:
                minT = self.paths[i].total_duration
        return minT

    # return min distance
    def getDistance(self):
        minD = self.paths[0].total_distance

        for i in range(1, len(self.paths)):
            if self.paths[i].total_distance < minD:
                minD = self.paths[i].total_distance
        return minD

    def isEmpty(self):
        return len(self.paths) == 0
