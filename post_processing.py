# This file contains the post processing class for HD_Detection
import os
import numpy as np 
from sort import *
import timeit
import sys
import math


class Post_Processing:
    """
    Post processing class for HD_Detection
    
    Attributes:
    -----------
    log_path: str
        path to log file
    
    Methods:
    --------
    __init__(self, log_path: str)
        Constructor
    Converter(self, log_path: str)
        Convert the log file to a numpy file
    Tracker(self, numpy: file)
        Track the detected objects
    """
    
    def __init__(self, log_path: str, stride: int=5, fps: int=30):
        """
        Constructor
        
        Parameters:
        -----------
        log_path: str
            path to log file
        """
        # check if the log file exists
        self.log_path = log_path
        if not os.path.exists(self.log_path):
            raise FileNotFoundError("log file not found")
            sys.exit(1)
        self.stride = stride
        self.FPS = fps
        self.tracker = Sort(max_age=3, min_hits=1, iou_threshold=0.1)
        self.tracker.reset()
    def __call__(self, ):
        return self.track()
    
    def read_log(self):
        with open(self.log_path, 'r') as f:
            lines = f.readlines()
        data_dict = {}
        frame_info = {}
        width, heihgt = 0, 0
        for line in lines:
            line = line[10:]
            line = line.split(";")
            frame_number = int(line[0])
            
            
            class_name = line[1]
            bbox = [int(float(i)) for i in line[2].split(",")]
            score = round(float(line[3]), 2)
            detection = bbox + [score]
            detection = np.array(detection)
            detection = np.expand_dims(detection, axis=0)
            if frame_number not in list(frame_info.keys()):
                frame_info[frame_number] = {}
            frame_info[frame_number][bbox[0]] = [class_name, score]
            

            if frame_number not in list(data_dict.keys()):
                data_dict[frame_number] = detection

            else:
                data_dict[frame_number] = np.vstack((data_dict[frame_number], detection))
        width, height = line[4].split(",")
        height = height.replace("\n", "")
        # convert to float before converting to int
        width, height = float(width), float(height)
        width, height = int(width), int(height)
        self.width = width
        self.height = height
        return data_dict,  frame_info
    
    def track(self, ):
        data_dict, frame_info = self.read_log()
        id_counter_dict = {}
        data_dict_with_id = {}
        #start_time = timeit.default_timer()
        for i in range(0, max(list(data_dict.keys())), self.stride):
            if i not in list(data_dict.keys()):
                detection = np.array([[0, 0, 0, 0, 0]])
                state = self.tracker.update(detection)
                continue
            # check if data_dict[i] is tuple or not
            if type(data_dict[i]) == np.ndarray:
                try:
                    detection = data_dict[i] #.reshape(1, -1)
                    #start_time = timeit.default_timer()
                    state = self.tracker.update(detection)
                    #print("time: ", timeit.default_timer() - start_time)
                except:
                    print("error")
                    print(data_dict[i])
                #state = tracker.update(data_dict[i])
                for res in state:
                    res = res.astype(int)
                    x1, y1, x2, y2, id = res
                    
                    if id not in id_counter_dict:
                        id_counter_dict[id] = {}
                        id_counter_dict[id]['frame_list'] = list()
                    id_counter_dict[id]['frame_list'].append(i)
                    
                    #print("frame: ", i, "id: ", id, "x1: ", x1, "y1: ", y1, "x2: ", x2, "y2: ", y2)
                    if i not in list(data_dict_with_id.keys()):
                        data_dict_with_id[i] = np.array([x1, y1, x2, y2, id])
                        data_dict_with_id[i] = np.expand_dims(data_dict_with_id[i], axis=0)
                    else:
                        data_dict_with_id[i] = np.vstack((data_dict_with_id[i], [x1, y1, x2, y2, id]))
            else:
                print(data_dict[i])
                print("error")
        for _id in list(id_counter_dict.keys()):
            # print(list(id_counter_dict.keys()   ))
            # print("id: ", _id)
            start_frame_of_id = id_counter_dict[_id]['frame_list'][0]
            end_frame_of_id = id_counter_dict[_id]['frame_list'][-1]
            duration = end_frame_of_id - start_frame_of_id
            # convert duration to seconds
            duration = duration / self.FPS
            id_counter_dict[_id]['duration'] = duration
            id_counter_dict[_id]['score'] = 0
            for i in range(data_dict_with_id[start_frame_of_id].shape[0]):
                x1, y1, x2, y2, id = data_dict_with_id[start_frame_of_id][i]

                if _id == id:
                    distance = 100000

                    for _x1 in list(frame_info[start_frame_of_id].keys()):
                        if math.sqrt((_x1 - x1)**2) < distance:
                            distance = math.sqrt((_x1 - x1)**2)
                            x1 = _x1
                    id_counter_dict[_id]['score'] = frame_info[start_frame_of_id][x1][1]
                    id_counter_dict[_id]['class_name'] = frame_info[start_frame_of_id][x1][0]
                    x_center, y_center = (x1 + x2) / 2, (y1 + y2) / 2
                    _w, _h = x2 - x1, y2 - y1
                    normalized_bbox = [x_center / self.width, y_center / self.height, _w / self.width, _h / self.height]
                    id_counter_dict[_id]['bbox'] = normalized_bbox
                    break

        return id_counter_dict
                
            
