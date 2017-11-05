from tqdm import tqdm
from pathlib import Path
import subprocess
import ipdb
import sys
import os
import glob
import cv2
from tesserocr import PyTessBaseAPI
import tesserocr

try:
    import Image
except ImportError:
    from PIL import Image


#pytesseract.pytesseract.tesseract_cmd = '/usr/local/Cellar/tesseract/3.05.01/'
# add common code to path
sys.path.insert(0, '/Users/maxtby/Dropbox/swisschicks/syncher')

from utils import configure_logger, resize_video, get_frame_dims 
from utils import get_video_duration_in_seconds, compute_stats

# parameters for optical flow computation
FPS = 4
VIDEO_DIMS = (320, 240)


def make_parent_dirs(path):
    if not path.parent.is_dir():
        make_parent_dirs(path.parent)
    print('creating dir at {}'.format(path))
    path.parent.mkdir(exist_ok=True) 

file_in=  Path('/Volumes/CCTVFootage/datadir0/')
file_out = Path('/Users/maxtby/Documents/frenchImages/')

videos = glob.glob(str(file_in) + '/*.mp4')
videos.sort()

raw_paths = []
for video in videos:
    raw_paths.append(Path(os.path.realpath(video)))

#resized_paths = [ resized_dir / p.relative_to(raw_dir) for p in raw_paths]
#resized_paths = [ p.with_suffix('.raw') for p in resized_paths]


for raw in raw_paths:
    res_path =  file_out #os.path.join(file_out) # raw.stem)
    picture1 = Path(str(res_path) + '/' + raw.stem + 'begin.jpg')
    picture2 = Path(str(res_path) + '/' + raw.stem + 'end.jpg')

    ffmpeg_duration = subprocess.run("ffmpeg -i " + str(raw) +  " 2>&1 | grep  'Duration' | sed 's/Duration: \\(.*\\), start.*/\\1/g' ", shell=True, stdout=subprocess.PIPE)
    dur = ffmpeg_duration.stdout.decode("utf-8").strip() 


    subprocess.run("ffmpeg -ss " + "00:00:00.00" + " -i " + str(raw) + "  -vframes 1 -q:v 2 " +  str(picture1), shell=True)
    subprocess.run("ffmpeg -ss " +  dur + " -i " + str(raw) + " -vframes 1 -q:v 2 " +  str(picture2), shell=True)

    img1 = cv2.imread(str(picture1))
    img2 = cv2.imread(str(picture2))

    crop_img1 = img1[56:112, 70:1000, :] 
    crop_img2 = img1[56:112, 70:1000, :] 
    #cv2.imshow("ims",crop_img1)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    for i in range (crop_img1.shape[0]): #traverses through height of the image
      for j in range (crop_img1.shape[1]):
        if (((j <= 125) or (j >= 430)) and crop_img1[i, j, 1]  >= 245
             and crop_img1[i,j, 2] >= 238
             and crop_img1[i,j,0] >= 245 # and ((crop_img1[i, j,1] < 255) and (crop_img1[i, j,2] < 255) and (crop_img1[i, j,0] < 255))
            or (crop_img1[i,j, 2] < 5 and crop_img1[i,j, 1] < 5)): # and crop_img1[i, j, 2] is 0):
          crop_img1[i,j] = 0,0,0
        elif(((j <= 125) or (j >= 430)) and not (crop_img1[i, j, 1]  >= 245
             and crop_img1[i,j, 2] >= 238
             and crop_img1[i,j,0] >= 245 # and ((crop_img1[i, j,1] < 255) and (crop_img1[i, j,2] < 255) and (crop_img1[i, j,0] < 255))
            or (crop_img1[i,j, 2] < 5 and crop_img1[i,j, 1] < 5))):
          crop_img1[i,j] = 255,255,255

        if((j > 125) and (j < 430) and crop_img1[i,j, 2] < 5 and crop_img1[i,j, 1] < 5):
          crop_img1[i,j] = 0,0,0
        elif(((j > 125) and (j < 430)) and not (crop_img1[i,j, 2] < 5 and crop_img1[i,j, 1] < 5)):
          crop_img1[i,j] = 255,255,255

    month1 = str(picture1).replace('.jpg','month.png')
    date1 = str(picture1).replace('.jpg','date.png')
    year1 = str(picture1).replace('.jpg','year.png')
    day1 = str(picture1).replace('.jpg','day.png')
    hour1 = str(picture1).replace('.jpg','hour.png')
    min1 = str(picture1).replace('.jpg','min.png')
    sec1 = str(picture1).replace('.jpg','sec.png')

    container1 = [month1, date1, year1, day1, hour1, min1, sec1]

    cv2.imwrite(month1, crop_img1[:, 0:85, :])
    cv2.imwrite(date1, crop_img1[:, 126:206, :])
    cv2.imwrite(year1, crop_img1[:, 327:409, :])
    cv2.imwrite(day1, crop_img1[:, 446:565, :])
    cv2.imwrite(hour1, crop_img1[:, 608:693, :])
    cv2.imwrite(min1, crop_img1[:, 721:812, :])
    cv2.imwrite(sec1, crop_img1[:, 845:926, :])

     #125,420

    bordersize=500
    crop_img1 =cv2.copyMakeBorder(crop_img1, top=bordersize, bottom=bordersize, left=bordersize, right=bordersize, borderType= cv2.BORDER_CONSTANT, value=[255,255,255] )
    cv2.imwrite(str(picture1).replace('.jpg','.png'), crop_img1)
    cv2.imshow("ims",crop_img1)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite(str(picture2), crop_img2)

    size = 930, 56
    image1 = Image.open(str(picture1).replace('.jpg','.png'))
    #im1_resized = image1.resize(size, Image.ANTIALIAS)
    image1.save(str(picture1).replace('.jpg','.png'), "PNG", dpi=[300,300])

    image2 = Image.open(str(picture2))
    #im2_resized = image2.resize(size, Image.ANTIALIAS)
    image2.save(str(picture2),  dpi=[70,70])


    #print(ocr.image_to_string(Image.open(str(picture1).replace('.jpg','.png'))))
    #ocr = tesseract.TessBaseAPI();
    #ocr.Init(".","eng",tesseract.OEM_TESSERACT_ONLY)
    #ocr.SetVariable("tessedit_char_whitelist", "0123456789")

    ocr = ''
    with PyTessBaseAPI() as api:

      api.SetImageFile(str(picture1).replace('.jpg','.png'))
      api.SetVariable("tessedit_char_whitelist", "0123456789-:")
      print(api.GetUTF8Text())
      api.SetImageFile(month1)
      api.SetVariable("tessedit_char_whitelist", "0123456789")
      ocr += api.GetUTF8Text() + ' '

      api.SetImageFile(date1)
      api.SetVariable("tessedit_char_whitelist", "0123456789")
      ocr += api.GetUTF8Text() + ' '

      api.SetImageFile(year1)
      api.SetVariable("tessedit_char_whitelist", "2017")
      ocr += api.GetUTF8Text() + ' '

      api.SetImageFile(day1)
      api.SetVariable("tessedit_char_whitelist", "MonTueWdhuFriSat")
      ocr += api.GetUTF8Text() + ' '

      api.SetImageFile(hour1)
      api.SetVariable("tessedit_char_whitelist", "0123456789")
      ocr += api.GetUTF8Text() + ' '

      api.SetImageFile(min1)
      api.SetVariable("tessedit_char_whitelist", "0123456789")
      ocr += api.GetUTF8Text() + ' '

      api.SetImageFile(sec1)
      api.SetVariable("tessedit_char_whitelist", "0123456789")
      ocr += api.GetUTF8Text() + ' '


      print(ocr)


#70 by 56
#930 by 56

    exit()
#    res = res_p.parent / res_p.stem
#    of_path = str(res) + '.of'
#    if not Path(of_path).exists():
#        make_parent_dirs(resized)
#        resize_video(raw, resized, size=VIDEO_DIMS, fps=FPS) # fps already handled by rotation
#        num_seconds = get_video_duration_in_seconds(raw) 
#        num_frames = FPS * num_seconds
#        make_parent_dirs(res)
#        compute_stats(resized, res, num_frames, BINARY_PATH)
#        resized.unlink()
#        print('src: {}'.format(raw))
#    else:
#        print('{} exists, skipping..'.format(str(res)))