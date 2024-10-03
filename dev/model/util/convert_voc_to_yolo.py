import glob
import os
import pickle
import xml.etree.ElementTree as ET
from os import listdir, getcwd
from os.path import join

class_json_dict = {
    "__background__":   0,

    "text":         1,
    "junction":     2,
    "crossover":    3,
    "terminal":     4,
    "gnd":          5,
    "vss":          6,

    "voltage.dc":       7,
    "voltage.ac":       8,
    "voltage.battery":  9,

    "resistor":             10,
    "resistor.adjustable":  11,
    "resistor.photo":       12,

    "capacitor.unpolarized":    13,
    "capacitor.polarized":      14,
    "capacitor.adjustable":     15,

    "inductor":         16,
    "inductor.ferrite": 17,
    "inductor.coupled": 18,
    "transformer":      19,

    "diode":                20,
    "diode.light_emitting": 21,
    "diode.thyrector":      22,
    "diode.zener":          23,

    "diac":                 24,
    "triac":                25,
    "thyristor":            26,
    "varistor":             27,

    "transistor.bjt":   28,
    "transistor.fet":   29,
    "transistor.photo": 30,

    "operational_amplifier":                    31,
    "operational_amplifier.schmitt_trigger":    32,
    "optocoupler":                              33,

    "integrated_circuit":                   34,
    "integrated_circuit.ne555":             35,
    "integrated_circuit.voltage_regulator": 36,
   
    "xor":  37,
    "and":  38,
    "or":   39,
    "not":  40,
    "nand": 41,
    "nor":  42,
	
    "probe":         43,
    "probe.current": 44,
    "probe.voltage": 45,

    "switch":   46,
    "relay":    47,

    "socket":   48,
    "fuse":     49,

    "speaker":      50,
    "motor":        51,
    "lamp":         52,
    "microphone":   53,
    "antenna":      54,
    "crystal":      55,
    
    "mechanical":   56,
    "magnetic":     57,
    "optical":      58,
    "block":        59,
    "explanatory":  60,

    "unknown":  61
}

dirs = ['/home/athip/psu/3/ecosys/proj/dev/model/data/train/new_data']
classes = list(class_json_dict.keys())

def getImagesInDir(dir_path):
    image_list = []
    # pipp = []
    for filename in glob.glob(dir_path + '/*.jpg'):
        image_list.append(filename)
    for filename in glob.glob(dir_path + '/*.jpeg'):
        image_list.append(filename)
    for filename in glob.glob(dir_path + '/*.png'):
        image_list.append(filename)
    for filename in glob.glob(dir_path + '/*.JPG'):
        image_list.append(filename)
    # for filename in glob.glob(dir_path + '/*'):
    #     pipp.append(filename[-3:])
    # print(set(pipp))
    print(len(image_list))

    return image_list

def convert(size, box):
    dw = 1./(size[0])
    dh = 1./(size[1])
    x = (box[0] + box[1])/2.0 - 1
    y = (box[2] + box[3])/2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)

def convert_annotation(dir_path, output_path, image_path):
    basename = os.path.basename(image_path)
    basename_no_ext = os.path.splitext(basename)[0]

    in_file = open(dir_path + '/' + basename_no_ext + '.xml')
    out_file = open(output_path + basename_no_ext + '.txt', 'w')
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult)==1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = convert((w,h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')

# cwd = getcwd()

for dir_path in dirs:
    # full_dir_path = cwd + '/' + dir_path
    full_dir_path = dir_path
    output_path = full_dir_path +'/yolo/'

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    image_paths = getImagesInDir(full_dir_path)
    list_file = open(full_dir_path + '.txt', 'w')

    for image_path in image_paths:
        list_file.write(image_path + '\n')
        convert_annotation(full_dir_path, output_path, image_path)
    list_file.close()

    print("Finished processing: " + dir_path)