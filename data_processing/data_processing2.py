from PIL import Image
import pytesseract
import csv
import re
import os
import pandas as pd

def GetTimeFromImg(path):
	img = Image.open(path).crop((727,770, 790, 790))
	# img.save("../../EmbryoScopeAnnotatedData/Folder 1/try.jpg")
	text = pytesseract.image_to_string(img ,config ='--psm 6')
	start_ind = 0
	for i,ch in enumerate(text):
		if ch.isdigit(): 
			start_ind = i
			break
	new_text = text[i:]
	return GetTimeFromText(new_text)


def GetTimeFromText(text = "", debug=0):
	if text is "": return None
	m = re.search(r'.*(?=h)', file_path)
	if m:
		label = m.group(0).strip()
		try:
			res = float(label)
			return res
		except:
			if debug>0: print ("Error finding the label")
			return None
	else: 
		return None

# dictionary with (folder number, well number), and the value as list of (ending time, label)
def GetLabelFromTime(time, file_path, dct = {}):
	m = re.search(r'(?<=/Folder).*(?=/)')
	n = re.search(r'(?<=WELL).*(?=/)')
	if m and n:
		folder, well = m.group(0).strip(), n.group(0).strip()
		try:
			times = dct[int(folder),int(well)]
			for t, label in times:
				if time > t: continue
				# if less than the ending time return label.
				return label
		except:
			if debug>0: print ("Error finding the label")



def ProcessAllCSVs(path):
	annots = pd.read_csv('data.csv')
	for col in annots.columns:
		




# def yield_image(path, debug=0):
# 	pass
# yield_image("../../EmbryoScopeAnnotatedData")

print(GetTimeFromImg('../../test_EmbryoScopeAnnotatedData/Folder 11/D2019.03.16_S00014_I3205_P_WELL02/D2019.03.16_S00014_I3205_P_WELL02_RUN016.JPG'))

path = "../../test_EmbryoScopeAnnotatedData/"
counter = 0
for directory in os.listdir(path):
	if directory[0] is ".": continue
	file_path = os.path.join(path, directory)
	for well in os.listdir(file_path):
		if well[0] is ".": continue
		full_path_to_well = os.path.join(file_path, well)
		for img in os.listdir(full_path_to_well):
			if img[0] is ".": continue
			print(counter)
			full_path_to_img = os.path.join(full_path_to_well, img)
			print("current_image: " + full_path_to_img)
			if GetTimeFromImg(full_path_to_img):
				print(GetTimeFromImg(full_path_to_img))
			else:
				print("error")