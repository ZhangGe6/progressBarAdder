# God knows I will use all of PIL, imageio and cv2 ...

import os
import platform
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


def config_gifsicle():
    if platform.system() == "Windows":
        # gifsicle.exe should be ported in this repo
        # otherwise it can be downloaded from https://eternallybored.org/misc/gifsicle/
        assert os.path.exists( "./gifsicle.exe")
    elif platform.system() == "Linux":
        # giflossy: https://github.com/kornelski/giflossy is merged to gifsicle in version 1.92
        # see gifsicle update log: https://github.com/kohler/gifsicle/blob/master/NEWS.md#version-192--18apr2019
        # However, Ubuntu 18 can only install 1.91 by apt-get
        # check it by: `apt-cache policy gifsicle` : https://askubuntu.com/questions/428772/how-to-install-specific-version-of-some-package
        # so we have to manually install giflossy (install reference: https://github.com/kornelski/giflossy/blob/master/INSTALL)
        # (and Ubuntu 20 install 1.92 by default andd can enjoy giflossy by only installing gifsicle. check here: https://superuser.com/a/1619955)
        release_info = os.popen("more /etc/lsb-release").read()
        dist = release_info.split("\n")[1].split("=")[1]
        print(dist)
        if int(dist.split(".")[0]) >= 20:
            os.system("sudo apt-install gifsicle")
        else:
            # I tried install giflossy manually, but the ./configure file can not work in my case
            raise RuntimeError("Unsupported Linux distribution for this version")

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

    split_gif_to_images(gif_info['gif'], args)
    add_bar_and_merge_to_gif(gif_info, args)
    
    print(" ===== out info: =====\n - progress bar added successfully!")
    out_gif_info = analyze_gif(args.output_gif_path)
    print(" - input gif size: {} KB, output size {} KB. \nWould you like to optimize for smaller size? [Y/N]".format(
        gif_info['file_size'], out_gif_info['file_size'])
    )
    optimize = input()
    if optimize == "Y":
        print("What is your expected size? [in KB]")
        expected_size = float(input())
        
        tmp_gif_path = args.output_gif_path.split('.gif')[0] + '_tmp.gif'
        lossiness = 20
        while True:
            # https://www.lcdf.org/gifsicle/man.html
            config_gifsicle()

            if platform.system() == "Windows":
                # prebuilt `gifsicle.exe` for Windows ha been ported in this repo
                os.system("gifsicle.exe -O3 --lossy={} {} -o {}".format(
                    lossiness,
                    args.output_gif_path, tmp_gif_path
                ))
            elif platform.system() == "Linux":
                os.system("gifsicle -O3 --lossy={} {} -j4 -o {}".format(
                    lossiness,
                    args.output_gif_path, tmp_gif_path
                ))
            else:
                raise RuntimeError("{} is not supported platform in this version.".format(platform.system()))
            
            optimized_size = analyze_gif(tmp_gif_path)['file_size']
            print("Try optimize level = 3, lossiness = {}, get optimized size {}".format(
                lossiness, optimized_size
            ))
            if optimized_size <= expected_size:
                shutil.move(tmp_gif_path, args.output_gif_path)
                print("Done! try optimize level = 3, lossiness = {}, get optimized size {}".format(
                    lossiness, optimized_size
                ))
                break
                
            lossiness += 10