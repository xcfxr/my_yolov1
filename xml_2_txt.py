import xml.etree.ElementTree as ET
import os

VOC_CLASSES = (    # always index 0
    'aeroplane', 'bicycle', 'bird', 'boat',
    'bottle', 'bus', 'car', 'cat', 'chair',
    'cow', 'diningtable', 'dog', 'horse',
    'motorbike', 'person', 'pottedplant',
    'sheep', 'sofa', 'train', 'tvmonitor')


def parse_rec(filename):
    tree = ET.parse(filename)
    objects = []
    for obj in tree.findall('object'):
        obj_struct = {}
        difficult = int(obj.find('difficult').text)
        if difficult == 1:
            continue
        obj_struct['name'] = obj.find('name').text
        bbox = obj.find('bndbox')
        obj_struct['bbox'] = [int(float(bbox.find('xmin').text)),
                              int(float(bbox.find('ymin').text)),
                              int(float(bbox.find('xmax').text)),
                              int(float(bbox.find('ymax').text))]
        objects.append(obj_struct)
    return objects


txt_file = open('trainval.txt', 'w')
test_file = open(r'trainval.txt', 'r')
lines = test_file.readlines()
lines = [x[:-1] for x in lines]
print(lines)

Annotations = r'D:\BaiduNetdiskDownload\VOC07+12+test\VOCdevkit\VOC2007\Annotations\\'
xml_files = os.listdir(Annotations)

count = 0
for xml_file in xml_files:
    count += 1
    if xml_file.split('.')[0] not in lines:
        continue
    image_path = xml_file.split('.')[0] + '.jpg'
    results = parse_rec(os.path.join(Annotations, xml_file))
    if len(results) == 0:
        print(xml_file)
        continue
    txt_file.write(image_path)
    for result in results:
        class_name = result['name']
        bbox = result['bbox']
        class_name = VOC_CLASSES.index(class_name)
        txt_file.write(' '.join(str(each) for each in ['', bbox[0], bbox[1], bbox[2], bbox[3], class_name]))
    txt_file.write('\n')
txt_file.close()


