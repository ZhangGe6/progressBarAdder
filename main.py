# God knows I will use all of PIL.Image, imageio and cv2 ...

# https://www.tutorialexample.com/extract-each-frame-of-an-animated-gif-using-python-pillow/

import os
import shutil
import numpy as np
import cv2
from PIL import Image, ImageSequence
import imageio

bar_height_frac = 1 / 20

# https://stackoverflow.com/a/53365469/10096987
def analyze_gif(PIL_Image_object):
    """ Returns the average framerate of a PIL Image object """
    PIL_Image_object.seek(0)
    frame_num = duration = 0
    while True:
        try:
            frame_num += 1
            duration += PIL_Image_object.info['duration']
            PIL_Image_object.seek(PIL_Image_object.tell() + 1)
        except EOFError:
            return frame_num, frame_num / duration * 1000

gif_path = 'SquarePants.gif'
gif = Image.open(gif_path)
frame_num, avg_fps = analyze_gif(gif)

# print(gif.info)
print(gif.mode)
print("gif frames = " + str(gif.n_frames))
print("Average fps: {}".format(avg_fps))

tmp_frame_dir = './tmp_frame_dir'
if not os.path.exists(tmp_frame_dir):
    os.mkdir(tmp_frame_dir)
for i, frame in enumerate(ImageSequence.Iterator(gif)):
    # frame.save("gif-webp-"+str(i)+".webp",format = "WebP", lossless = True)
    frame.save(os.path.join(tmp_frame_dir, "frame_{}.png".format(i)))

filenames = [filename for filename in os.listdir(tmp_frame_dir)]
filenames.sort(key = lambda x : int(x.split('frame_')[1].split('.png')[0]))
frame_paths = [os.path.join(tmp_frame_dir, filename) for  filename in filenames]
# print(frame_paths)

# # https://stackoverflow.com/a/35943809/10096987
frames = []
for i, filename in enumerate(frame_paths):
    # imageio.core.util.Image is an ndarray subclass # https://stackoverflow.com/a/50280844/10096987
    # print(isinstance(imageio.v2.imread(filename), np.ndarray))  # True
    imageio_img = imageio.v2.imread(filename)  # RGB format https://github.com/imageio/imageio/issues/345#event-1644137811
    # print(imageio_img.shape) # (height, width, 4), the 4th channel is alpha
    
    # 1. discard the 4th alpha channel. 2. convert RBG to BGR. 3. copy to a new object (otherwise `Overload resolution failed:` will be invoked)
    cv2_img = imageio_img[:, :, :3][:, :, ::-1].copy()
    height, width, _ = cv2_img.shape
    
    bar_height = int(bar_height_frac * height)
    bar_width = int(((i + 1) / frame_num) * width)
    cv2.rectangle(cv2_img, (0, height - bar_height), (bar_width, height), color=(0, 0, 255), thickness=-1)

    imageio_img_new = cv2_img[:, :, ::-1].copy()  # convert from BGR back to RGB
    frames.append(imageio_img_new)
    
imageio.mimsave('./res.gif', frames, fps=avg_fps)
shutil.rmtree(tmp_frame_dir)

    
    
    



    
