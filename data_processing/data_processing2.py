from PIL import Image
import pytesseract
import csv
import re
import os
import pandas as pd
from math import isnan
from imageio import imread
import numpy as np


TIME_NAME = ["tPB2","tPNa","tPNf","t2","t3","t4","t5","t6","t7","t8","t9+","tSC","tM","tSB","tB","tEB","tHB","tDead"]

# This returns the result as a dictionary: {well_num: (label_header, start_time, end_time)}
def ProcessCSV(path):
	annots = pd.read_csv(path, encoding = "ISO-8859-1")
	res = {}
	for index, row in annots.iterrows():
		if row["Well"]:
			well_num = int(row["Well"])
			res[well_num] = []
			for i, label_header in enumerate(TIME_NAME):
				if(label_header in row):
					start_time = float(row[label_header])
					if isnan(start_time): continue
					next_time = False
					for next_time_label in TIME_NAME[i+1:]:
						if next_time_label in row:
							next_time = float(row[next_time_label])
							if isnan(next_time): continue
							else: break
				if start_time and not isnan(start_time) and next_time and not isnan(next_time):
					res[well_num].append((label_header,start_time,next_time))
	return res


def GetTimeFromImg(path):
	img = Image.open(path).crop((727,770, 790, 790))
	text = pytesseract.image_to_string(img ,config ='--psm 6')
	time_match = re.search(r'([0-9]+).([0-9])', text)
	if not time_match: return None
	time_in_float = float(time_match.group(0))
	if(time_match and time_in_float and (not isnan(time_in_float))): 
		return time_in_float
	else: return None

def YieldImage(base_path, debug):
	for folder_name_raw in os.listdir(base_path):
		print("\n##################################\nProcessing Folder:", folder_name_raw)
		folder_name_match = re.search(r'Folder ([0-9]+$)', folder_name_raw)
		if not folder_name_match: continue
		folder_num = int(folder_name_match.group(1))

		# Drill down inside folder. Let's find the annotations first
		annotations = None
		for under_folder in os.listdir(os.path.join(base_path, folder_name_raw)):
			annotation_match = re.search(r'P\.csv', under_folder)
			if not annotation_match: continue
			annotations = ProcessCSV(os.path.join(base_path, folder_name_raw, under_folder))
			if debug > 0: print("Annotations: ", annotations)
		if not annotations: 
			print("[WARNING] ", folder_name_raw, " does not have annotations, passing...")
			continue

		# Now we have the annotation, go to each well
		for well_name_raw in os.listdir(os.path.join(base_path, folder_name_raw)):
			well_match = re.search(r'WELL([0-9]+$)', well_name_raw)
			if not well_match: continue
			well_num = int(well_match.group(1))
			if debug > 0: print("Processing well: ", well_num)
			for picture_name in os.listdir(os.path.join(base_path, folder_name_raw, well_name_raw)):
				image_full_path = os.path.join(base_path, folder_name_raw, well_name_raw, picture_name)
				time = GetTimeFromImg(image_full_path)
				if debug > 0: print(image_full_path, time)
				if not time: continue
				if well_num not in annotations: 
					print("[WARNING] Well ",well_num, " not in annotations, passing...")
					continue
				for (label_header,start_time,next_time) in annotations[well_num]:
					if time >= start_time and time < next_time:
						yield(np.swapaxes(np.swapaxes([imread(image_full_path),]*3, 0, 2), 0 ,1), label_header)
						if debug > 0: print("Label: ", label_header)
						break;


# YieldImage('../../EmbryoScopeAnnotatedData', 1)