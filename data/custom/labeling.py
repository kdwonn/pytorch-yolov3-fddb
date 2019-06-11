import os
import errno
from PIL import Image
from math import *

# Taken from https://stackoverflow.com/a/600612/119527
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def safe_open_w(path):
    ''' Open "path" for writing, creating any parent directories as needed.
    '''
    mkdir_p(os.path.dirname(path))
    return open(path, 'w')

def labelConvert(imgName, rawLabel):
    img = Image.open(os.path.abspath('images/'+imgName+'.jpg'))
    width, height = img.size

    a, b, angle, centre_x, centre_y = rawLabel

    def filterCoordinate(c,m):
	    if c < 0:
	    	return 0
	    elif c > m:
	    	return m
	    else:
	    	return c

    tan_t = -(b/a)*tan(angle)
    t = atan(tan_t)
    x1 = centre_x + (a*cos(t)*cos(angle) - b*sin(t)*sin(angle))
    x2 = centre_x + (a*cos(t+pi)*cos(angle) - b*sin(t+pi)*sin(angle))
    x_max = filterCoordinate(max(x1,x2),width)
    x_min = filterCoordinate(min(x1,x2),width)

    if tan(angle) != 0:
    	tan_t = (b/a)*(1/tan(angle))
    else:
    	tan_t = (b/a)*(1/(tan(angle)+0.0001))
    t = atan(tan_t)
    y1 = centre_y + (b*sin(t)*cos(angle) + a*cos(t)*sin(angle))
    y2 = centre_y + (b*sin(t+pi)*cos(angle) + a*cos(t+pi)*sin(angle))
    y_max = filterCoordinate(max(y1,y2),height)
    y_min = filterCoordinate(min(y1,y2),height)
	
    return [(x_max+x_min)/(2*width), (y_max+y_min)/(2*height), (x_max-x_min)/width, (y_max-y_min)/height]

def readLabels(fold, train_list_f, valid_list_f, isTrain):
    fileName = 'FDDB-fold-{:02n}-ellipseList.txt'.format(fold)
    with open(os.path.abspath("FDDB-folds/"+fileName)) as f:
        readingState, imgName, boxNum, boxCnt = 0, '', 0, 0
        for line in f:
            line = line.strip()
            if readingState == 0:
                #print(0)
                imgName = line
                label_f = safe_open_w(os.path.abspath('labels/'+imgName+'.txt'))
                (train_list_f if isTrain else valid_list_f).write('data/custom/images/'+imgName+'.jpg\n')
                readingState += 1

            elif readingState == 1:
                #print(1)
                boxNum = int(line)
                readingState += 1

            elif readingState == 2:
                #print(2)
                rawLabel = list(map(float, line.split()))[0:5]
                label = labelConvert(imgName, rawLabel)
                label_f.write('0 {l[0]}, {l[1]}, {l[2]}, {l[3]}\n'.format(l=label))
                boxCnt += 1
                if boxNum == boxCnt:
                    label_f.close()
                    readingState = 0
                    boxCnt = 0
            else:
                raise NotImplementedError
            
if __name__ == "__main__":
    train_list_f = open('train.txt', 'w')
    valid_list_f = open('valid.txt', 'w')
    for i in range(0, 10):
        readLabels(i+1, train_list_f, valid_list_f, True if i < 8 else False)