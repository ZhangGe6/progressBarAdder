# progressBarAdder

This is a simple tool to add progress bar to `.gif` file.

## usage

```bash
$ python main.py -h

optional arguments:
  -h, --help            show this help message and exit
  --input_gif_path INPUT_GIF_PATH, -i INPUT_GIF_PATH
                        the path to input gif file
  --output_gif_path OUTPUT_GIF_PATH, -o OUTPUT_GIF_PATH
                        the path to output gif file
  --bar_height_ratio BAR_HEIGHT_RATIO, -ratio BAR_HEIGHT_RATIO
                        the ratio of progress bar height vs. gif image height
  --bar_color BAR_COLOR, -color BAR_COLOR
                        the color of progress bar
  --tmp_frame_dir TMP_FRAME_DIR, -tmp TMP_FRAME_DIR
                        the color of progress bar
```

For example:
```bash
python main.py -i ./doc/SquarePants.gif

```
Then we can get the result `gif` with progress bar added (under the same folder with input gif by default)

![](./doc/SquarePants_res.gif)