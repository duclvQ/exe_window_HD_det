import os
from typing import Any
import numpy as np
import time
import sys
import argparse
import warnings
from datetime import datetime
from HD_Detection import HD_Detection
from post_processing import Post_Processing
import time


warnings.filterwarnings("ignore", category=UserWarning, module="torchvision.io.image")
warnings.filterwarnings("ignore", category=UserWarning, module="torch._jit_internal")
warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser(description='Process some args.')

# Add arguments
parser.add_argument('video_path', metavar='video_path', type=str, help='path to input video')
parser.add_argument('--model_path', type=str, default='model.pt', help='path to model.pt file')
parser.add_argument('--remove_wb', type=bool, default=True, help='remove white and black frames from the predicted results')
parser.add_argument('--orange_percentage_threshold', type=int, default=10, help='minimum percentage of orange pixels required to return True')
parser.add_argument('--model_resnet', type=str, default='flag_resnet18.pth', help='path to double check model')
parser.add_argument('--conf', type=float, default=0.2, help='minimum confidence threshold for detection')
parser.add_argument('--stride', type=int, default=5, help='frame stride for detection')
parser.add_argument('--run_on', type=int, default=0, help='choose which GPU to run on')
parser.add_argument('--timing_inspection', type=int, default=0, help='print inference time for each batch')
parser.add_argument('--skip_similarity', type=int, default=0, help='skip similars frames by histogram comparison')
# Parse arguments
args = parser.parse_args()

label_dict = {0: "china", 1:"vietnam", 2:"malaysia", 3:"nine_dash_line",4:"nine_dash_line", 5:"flag"}

start_time = time.time()

#Detector = HD_Detection(args.video_path, args.model, args.model_resnet, args.conf, args.stride, args.run_on, args.timing_inspection, args.skip_similarity)
Detector = HD_Detection(video_path = args.video_path, \
                        
                        model_path = args.model_path,     \
                        remove_wb = args.remove_wb, \
                        orange_percentage_threshold = args.orange_percentage_threshold, \
                        conf = args.conf,      \
                        stride = args.stride,      \
                        run_on = args.run_on,      \
                        timing_inspection = args.timing_inspection, \
                        similarity_comparision = args.skip_similarity,  \
                        label_dict = label_dict
                        )
# starting the detection
Detector()
# post processing
post_process = Post_Processing(Detector.log_path, stride=args.stride, fps=Detector.video_FPS)
post_process_results = post_process()
for i in list(post_process_results.keys()):
    class_name = post_process_results[i]['class_name']
    first_frame = post_process_results[i]['frame_list'][0]
    timecode = Detector.frame_to_timecode(first_frame, Detector.video_FPS)
    position = post_process_results[i]['bbox']
    confidence = post_process_results[i]['score']
    duration = Detector.seconds_to_timecode(post_process_results[i]['duration'])
    msg = f"INFO:root:[DETECTED]type=[{class_name}];timecode={timecode};duration={duration};position={position};confidence={confidence};frame={first_frame};w_h={Detector.width}x{Detector.height}"
    print(msg)
print('\n')
print(f"Total inference time: {round(time.time() - start_time, 2)} seconds for a video of {Detector.total_frames} frames")



