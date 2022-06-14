# God knows I will use all of PIL, imageio and cv2 ...

import os
import argparse
import shutil
import cv2
from PIL import Image, ImageSequence
import imageio


# https://stackoverflow.com/a/53365469/10096987
def analyze_gif(gif_path):
    gif = Image.open(gif_path)
    
    gif.seek(0)
    frame_num = duration = 0
    while True:
        try:
            frame_num += 1
            duration += gif.info['duration']
            gif.seek(gif.tell() + 1)
        except EOFError:
            return {
                'gif': gif,
                'frame_num': frame_num,
                'avg_fps': frame_num / duration * 1000,
                'file_size': round(os.path.getsize(gif_path) / 1024, 2)   # in KB
            }


def split_gif_to_images(gif_obj, args):
    if not os.path.exists(args.tmp_frame_dir):
        os.mkdir(args.tmp_frame_dir)
    for i, frame in enumerate(ImageSequence.Iterator(gif_obj)):
        frame.save(os.path.join(args.tmp_frame_dir, "frame_{}.png".format(i)))
    
def add_bar_and_merge_to_gif(gif_info, args):
    filenames = [filename for filename in os.listdir(args.tmp_frame_dir)]
    filenames.sort(key = lambda x : int(x.split('frame_')[1].split('.png')[0]))
    frame_paths = [os.path.join(args.tmp_frame_dir, filename) for filename in filenames]
    # print(frame_paths)

    # # https://stackoverflow.com/a/35943809/10096987
    frames = []
    for i, frame_path in enumerate(frame_paths):
        cv2_img = cv2.imread(frame_path)
        height, width, _ = cv2_img.shape
        
        bar_height = int(args.bar_height_ratio * height)
        bar_width = int(((i + 1) / gif_info['frame_num']) * width)
        cv2.rectangle(cv2_img, (0, height - bar_height), (bar_width, height), color=args.bar_color, thickness=-1)
        
        # imageio.core.util.Image is an ndarray subclass # https://stackoverflow.com/a/50280844/10096987
        imageio_img_new = cv2_img[:, :, ::-1].copy()  # convert from BGR back to RGB
        frames.append(imageio_img_new)

    imageio.mimsave(args.output_gif_path, frames, fps=gif_info['avg_fps'])
    shutil.rmtree(args.tmp_frame_dir)

def optimize_gif(gif_path, expected_size):
    
    pass

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
    if not args.output_gif_path:
        args.output_gif_path = args.input_gif_path.split('.gif')[0] + '_res.gif'

    gif_info = analyze_gif(args.input_gif_path)
    # print(gif_info)
    
    split_gif_to_images(gif_info['gif'], args)
    add_bar_and_merge_to_gif(gif_info, args)
    
    print(" ===== out info: =====\n - progress bar added successfully!")
    out_gif_info = analyze_gif(args.output_gif_path)
    print(" - input gif size: {} KB, output size {} KB. \nWould you like to optimize for smaller size? [Y/N]".format(
        gif_info['file_size'], out_gif_info['file_size'])
    )
    optimize = input()
    if optimize == "Y":
        # https://imageio.readthedocs.io/en/stable/examples.html#optimizing-a-gif-using-pygifsicle
        from pygifsicle import optimize
        os.environ["gifsicle"] = "gifsicle.exe"
        # print("What is your expected size? [in KB]")
        # expected_size = float(input())
        optimize(args.output_gif_path)
        opt_out_gif_info = analyze_gif(args.output_gif_path)
        print(" - optimize done! the optimzed size is {} KB, which is {} smaller.".format(
            opt_out_gif_info['file_size'], round(opt_out_gif_info['file_size'] / out_gif_info['file_size'], 2))
        )
        
        
        
    
    
    
    
    