import json

map_dict = {
    "STUDY": {
        "LOCATION": 0,
        "DIRECTIONS": ["RIGHT", "DIAG_RD", "DOWN"],
        "ROOMS": ["H0", "BILLIARD_ROOM", "H2"]
    },
    "H0": {
        "LOCATION": 0,
        "DIRECTIONS": ["LEFT", "RIGHT"],
        "ROOMS": ["STUDY", "HALL"]
    },
    "HALL": {
        "LOCATION": 0,
        "DIRECTIONS": ["LEFT", "DOWN", "RIGHT"],
        "ROOMS": ["H0", "H3", "H1"]
    },
    "H1": {
        "LOCATION": 0,
        "DIRECTIONS": ["LEFT", "RIGHT"],
        "ROOMS": ["HALL", "LOUNGE"]
    },
    "LOUNGE": {
        "LOCATION": 0,
        "DIRECTIONS": ["LEFT", "DIAG_LD", "DOWN"],
        "ROOMS": ["H1", "BILLIARD_ROOM", "H4"]
    },
    "H2": {
        "LOCATION": 0,
        "DIRECTIONS": ["UP", "DOWN"],
        "ROOMS": ["STUDY", "LIBRARY"]
    },
    "H3": {
        "LOCATION": 0,
        "DIRECTIONS": ["UP", "DOWN"],
        "ROOMS": ["HALL", "BILLIARD_ROOM"]
    },
    "H4": {
        "LOCATION": 0,
        "DIRECTIONS": ["UP", "DOWN"],
        "ROOMS": ["LOUNGE", "DINING_ROOM"]
    },
    "LIBRARY": {
        "LOCATION": 0,
        "DIRECTIONS": ["UP", "RIGHT", "DOWN"],
        "ROOMS": ["H2", "H5", "H7"]
    },
    "H5": {
        "LOCATION": 0,
        "DIRECTIONS": ["LEFT", "RIGHT"],
        "ROOMS": ["LIBRARY", "BILLIARD_ROOM"]
    },
    "BILLIARD_ROOM": {
        "LOCATION": 0,
        "DIRECTIONS": ["UP", "RIGHT", "DOWN", "LEFT"],
        "ROOMS": ["H3", "H6", "H8", "H5"]
    },
    "H6": {
        "LOCATION": 0,
        "DIRECTIONS": ["LEFT", "RIGHT"],
        "ROOMS": ["BILLIARD_ROOM", "DINING_ROOM"]
    },
    "DINING_ROOM": {
        "LOCATION": 0,
        "DIRECTIONS": ["UP", "LEFT", "DOWN"],
        "ROOMS": ["H4", "H6", "H9"]
    },
    "H7": {
        "LOCATION": 0,
        "DIRECTIONS": ["UP", "DOWN"],
        "ROOMS": ["LIBRARY", "CONSERVATORY"]
    },
    "H8": {
        "LOCATION": 0,
        "DIRECTIONS": ["UP", "DOWN"],
        "ROOMS": ["BILLIARD_ROOM", "BALLROOM"]
    },
    "H9": {
        "LOCATION": 0,
        "DIRECTIONS": ["UP", "DOWN"],
        "ROOMS": ["DINING_ROOM", "KITCHEN"]
    },
    "CONSERVATORY": {
        "LOCATION": 0,
        "DIRECTIONS": ["UP", "DIAG_RU", "RIGHT"],
        "ROOMS": ["H7", "BILLIARD_ROOM", "H10"]
    },
    "H10": {
        "LOCATION": 0,
        "DIRECTIONS": ["LEFT", "RIGHT"],
        "ROOMS": ["CONSERVATORY", "BALLROOM"]
    },
    "BALLROOM": {
        "LOCATION": 0,
        "DIRECTIONS": ["LEFT", "UP", "RIGHT"],
        "ROOMS": ["H10", "H8", "H11"]
    },
    "H11": {
        "LOCATION": 0,
        "DIRECTIONS": ["LEFT", "RIGHT"],
        "ROOMS": ["BALLROOM", "KITCHEN"]
    },
    "KITCHEN": {
        "LOCATION": 0,
        "DIRECTIONS": ["LEFT", "DIAG_LU", "UP"],
        "ROOMS": ["H11", "BILLIARD_ROOM", "H9"]
    },

}

with open("map_dict.json", "w") as write_file:
    json.dump(map_dict, write_file)