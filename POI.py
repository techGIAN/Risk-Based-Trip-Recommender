from trip_recommender import Trip_Recommender
from utilityMethods import ROUTE_FROM, SORT_BY
import ast

class POI(Trip_Recommender):
    poi_risk = None
    normal_risk = None
    skewed_risk = None
    uniform_risk = None
    main_index = 0

    def __init__(self, coordinate, origin, hour, row, ROUTE_FROM=ROUTE_FROM.OSRM, IS_DEBUG_MODE=False,
                 IS_FULL_DEBUG_MODE=False, mode_of_transit='car', is_time_now=True, time_later_val=None,
                 sort_by=SORT_BY.Distance):

        super().__init__(source=origin,
                         destination=coordinate,
                         trip_count=3,
                         IS_DEBUG_MODE=IS_DEBUG_MODE,
                         IS_FULL_DEBUG_MODE=IS_FULL_DEBUG_MODE,
                         ROUTE_FROM=ROUTE_FROM,
                         mode_of_transit=mode_of_transit,
                         is_time_now=is_time_now,
                         time_later_val=time_later_val)

        self.main_index = 0
        self.normal_risk = []
        self.skewed_risk = []
        self.uniform_risk = []

        for path in self.paths:
            try:
                arrival = int(path.total_duration / 60 + hour) % 168
                self.normal_risk = (ast.literal_eval(row['normal_risks'])[5])
                self.skewed_risk =(ast.literal_eval(row['skewed_risks'])[5])
                self.uniform_risk = (ast.literal_eval(row['uniform_risks'])[5])

                # self.normal_risk = (row['normal_risks' + str(arrival)])
                # self.skewed_risk =(row['skewed_risks' + str(arrival)])
                # self.uniform_risk = (row['uniform_risks_' + str(arrival)])
            except Exception as e:
                print("ERROR, ERROR: POI.py: " + str(e))

        # if sort_by == SORT_BY.Distance:
        #     self.set_min_distance_index()
        # elif sort_by == SORT_BY.Time:
        #     self.set_min_duration_index()
        # else:
        #     self.set_min_risk_index()

    # filter out paths based on distance and time to get to the location
    def filter(self, dist_filter, time_filter):
        for index in reversed(range(len(self.paths))):
            if not (self.paths[index].total_distance <= dist_filter and
                    self.paths[index].total_duration <= time_filter):
                self.paths.pop(index)

    # return all travel time
    def getTime(self):
        return self.paths[self.main_index].total_duration

    # return all distances
    def getDistance(self):
        return self.paths[self.main_index].total_distance

    # return normal risk
    def get_normal_risk(self):
        return self.normal_risk

    # return skewed risk
    def get_skewed_risk(self):
        return self.skewed_risk

    # return uniform risk
    def get_uniform_risk(self):
        return self.uniform_risk

    # return path risk
    def risk_of_paths(self):
        return self.paths[self.main_index].risk

    def isEmpty(self):
        return len(self.paths) == 0

    # Sort by distance - set index accordingly
    def set_min_distance_index(self):
        index = 0

        for i in range(1,len(self.paths)):
            if self.paths[i].total_distance < self.paths[index].total_distance:
                index = i

        self.main_index = index

    # Sort by duration - set index accordingly
    def set_min_duration_index(self):
        index = 0

        for i in range(1,len(self.paths)):
            if self.paths[i].total_duration < self.paths[index].total_duration:
                index = i

        self.main_index = index

    # Sort by risk - set index accordingly
    def set_min_risk_index(self):
        index = 0

        for i in range(1,len(self.paths)):
            if self.paths[i].risk < self.paths[index].risk:
                index = i

        self.main_index = index
