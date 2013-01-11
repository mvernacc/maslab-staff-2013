# Defines a class to store features found by the robot
# MASLab Team 4

class Feature:
    (UNK, BALL, TOWER, WALL) = (0,1,2,3) # feature types
    def __init__(self, distance, angle, feature_type):
        self.dist = distance # Distance to the feature (cm)
        self.angle = angle # Angle to the feature (degrees, 0=straight, 90=left,
            # -90=right)
        self.feat_type = feature_type # type of feature
