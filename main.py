# God knows I will use all of PIL.Image, imageio and cv2 ...

import os
import argparse
import shutil
import cv2
from PIL import Image, ImageSequence
import imageio

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

def split_gif_to_images(gif_obj, args):
    if not os.path.exists(args.tmp_frame_dir):
        os.mkdir(args.tmp_frame_dir)
    for i, frame in enumerate(ImageSequence.Iterator(gif_obj)):
        frame.save(os.path.join(args.tmp_frame_dir, "frame_{}.png".format(i)))
    
def add_bar_and_merge_to_gif(args, avg_fps):
    filenames = [filename for filename in os.listdir(args.tmp_frame_dir)]
    filenames.sort(key = lambda x : int(x.split('frame_')[1].split('.png')[0]))
    frame_paths = [os.path.join(args.tmp_frame_dir, filename) for  filename in filenames]
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
        
        bar_height = int(args.bar_height_ratio * height)
        bar_width = int(((i + 1) / frame_num) * width)
        cv2.rectangle(cv2_img, (0, height - bar_height), (bar_width, height), color=(0, 0, 255), thickness=-1)

        imageio_img_new = cv2_img[:, :, ::-1].copy()  # convert from BGR back to RGB
        frames.append(imageio_img_new)
        
    output_gif_path = args.output_gif_path
    if not output_gif_path:
        output_gif_path = args.input_gif_path.split('.gif')[0] + '_res.gif'
    imageio.mimsave(output_gif_path, frames, fps=avg_fps)
    shutil.rmtree(args.tmp_frame_dir)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_gif_path', '-i', required=True, help='the path to input gif file')
    parser.add_argument('--output_gif_path', '-o', default=None, help='the path to output gif file')
    parser.add_argument('--bar_height_ratio', '-ratio', type=float, default=1/20, help='the ratio of progress bar height vs. gif image height')
    parser.add_argument('--bar_color', '-color',  default=(0, 0, 255), help='the color of progress bar')
    parser.add_argument('--tmp_frame_dir', '-tmp', type=str, default='tmp_frame_dir', help='the color of progress bar')
    
    args = parser.parse_args()
    
    return args
    
if __name__ == "__main__":
    args = parse_args()
    # print(args)

    gif = Image.open(args.input_gif_path)
    frame_num, avg_fps = analyze_gif(gif)
    
    split_gif_to_images(gif, args)
    add_bar_and_merge_to_gif(args, avg_fps)