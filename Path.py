import copy

from utilityMethods import query

IS_DEBUG_MODE = True
IS_FULL_DEBUG_MODE = True


class Path:
    coordinates = None
    hexagons = []
    total_distance = None
    risk = None
    total_duration = None
    time_by_segment = []
    distance_by_segment = []
    ROUTE_FROM = None

    def __init__(self, coordinates, distance, time, ROUTE_FROM = 'OSRM'):
        self.coordinates = coordinates
        self.total_distance = distance
        self.total_duration = time
        self.ROUTE_FROM = ROUTE_FROM

    def calculate_risk(self):
        # get the distance and duration of each line segment of the path
        self.__set_paths__full_data()

    def print(self):
        return "<<-----------------------------\n" \
               "\tcoordinates = " + str(self.coordinates) + "\n" \
               "\thexagons = " + str(self.hexagons) + "\n" \
               "\ttotal_distance = " + str(self.total_distance) + "\n" \
               "\trisk = " + str(self.risk) + "\n" \
               "\ttotal_duration = " + str(self.total_duration) + "\n" \
               "\ttime_by_segment (minutes) = " + str(self.time_by_segment) + "\n" \
               "\tdistance_by_segment (km)  = " + str(self.distance_by_segment) + "\n" \
               "----------------------------->>"

    # For each line segment that is part of a path, this method finds its distance and duration
    # and updates the path's information accordingly
    def __set_paths__full_data(self):
        pts = self.coordinates
        isFirst = True
        last = None
        segment_distances = []
        segment_durations = []
        q = None

        # For each line segment in a path do:
        for line in pts:
            if isFirst:
                isFirst = False
            else:
                # q = queryOSRM(last, line)
                # sub_path_list, dist, dur = get_path_points(q, 2)
                sub_path_list, dist, dur  = query(last, line, trip_count=1, ROUTE_FROM=self.ROUTE_FROM)

                segment_durations.append(dur)
                segment_distances.append(dist)

            last = line

        self.time_by_segment = copy.deepcopy(segment_durations)
        self.distance_by_segment = copy.deepcopy(segment_distances)

    # Prints the number of points per kilometer to get a sense of the resolution
    def get_resolution(self):
        pts = self.coordinates

        print("\t"+str(round(len(pts)/self.total_distance,2)) + " points\Km (" + str(len(pts)) + " points for " +
              str(self.total_distance) + 'Km)')
        print(pts)
