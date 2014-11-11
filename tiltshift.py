# coding: UTF-8

# The MIT License (MIT)
#
# Copyright (c) 2014 Takeshi OSOEKAWA
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import numpy as np;
from scipy import ndimage;
import cv2;

from PIL import Image;
from PIL import ImageEnhance;

import time;

import sys;
import argparse;
import re;

def limit_value(v,vmin,vmax):
  return max(vmin, min(vmax, v));

def gen_mask(sz, t, tc, c, bc):
  bounds = (0,limit_value(int(sz[1]*t),0,sz[1]),limit_value(int(sz[1]*(t+tc)),0,sz[1]),limit_value(int(sz[1]*(t+tc+c)),0,sz[1]),limit_value(int(sz[1]*(t+tc+c+bc)),0,sz[1]),sz[1]);
  mask = np.array(Image.new('L', sz));
  mask[bounds[0]:bounds[1],:] = 255;
  for i in range(bounds[1],bounds[2]):
    mask[i,:] = 255 - int(255.0/float( bounds[2] - bounds[1] ) * float(i - bounds[1]));
  mask[bounds[3]:bounds[2],:] = 0;
  for i in range(bounds[3],bounds[4]):
    mask[i,:] = int(255.0/float( bounds[4] - bounds[3] ) * float(i - bounds[3]));
  mask[bounds[4]:bounds[5],:] = 255;
  mask = Image.fromarray(mask);
  return mask;

def enhance_image(image, saturation, contrast, brightness, sharpness):
  image_ = image;
  if saturation != 1.0:
    image_ = ImageEnhance.Color(image_).enhance(saturation);
  if contrast != 1.0:
    image_ = ImageEnhance.Contrast(image_).enhance(contrast);
  if brightness != 1.0:
    image_ = ImageEnhance.Brightness(image_).enhance(brightness);
  if sharpness != 1.0:
    image_ = ImageEnhance.Sharpness(image_).enhance(sharpness);
  return image_;

def gen_blurred_image(image, blur_factor):
  if blur_factor == 0:
    return image;
  im = np.array(image);
  return Image.fromarray(ndimage.gaussian_filter(im, sigma=[blur_factor, blur_factor, 0]));

def paste_image(base, layer, mask):
  im = base;
  im.paste(layer, mask = mask);
  return im;

if __name__ == '__main__':

  def parse_resize(string):
    return [int(x) for x in string.split('*')];

  parser = argparse.ArgumentParser(description='Tilt shift effector');
  parser.add_argument('input',type=str,help='input file');
  parser.add_argument('--resize',type=parse_resize,help='画像サイズの変更。デフォルトは変更なし。width*height e.g. 640*360');
  parser.add_argument('--margin',type=float,nargs=4,help='上のぼかし、上と焦点の間、焦点、下と焦点の間 の幅をそれぞれ、全体を1.0とした割合で与える。下のぼかし幅は残りが割り当てられる。(0.0から1.0の浮動小数、デフォルトは0.5 0.1 0.05 0.08)',default=[0.5,0.1,0.05,0.08]);
  parser.add_argument('--skip',type=int,help='飛ばすフレーム数 (0以上の整数、0で全フレーム、デフォルトは0)',default=0);
  parser.add_argument('--saturation',type=float,help='彩度 (0.0以上の浮動小数、1.0で元と同じ。デフォルトは2.0)', default=2.0);
  parser.add_argument('--contrast',type=float,help='コントラスト (0.0以上の浮動小数、1.0で元と同じ。デフォルトは1.2)', default=1.2);
  parser.add_argument('--brightness',type=float,help='明度 (0.0以上の浮動小数、1.0で元と同じ。デフォルトは1.0)', default=1.0);
  parser.add_argument('--sharpness',type=float,help='シャープネス (0.0以上の浮動小数、1.0で元と同じ。デフォルトは1.0)', default=1.0);
  parser.add_argument('--blur', type=float,help='ぼかしの強さ (0.0以上の浮動小数、0.0でぼかしなし。デフォルトは4.0)',default=4.0);
  parser.add_argument('--fps',type=int,help='fps (1以上の整数。デフォルトは変更なし)');
  parser.add_argument('--limit',type=int,help='書き出すフレーム数のリミット (1以上の整数。デフォルトは変更なし)');
  parser.add_argument('--output', type=str, help='出力ファイル名。デフォルトは [inputファイル名][日付時刻].mov');
  args = parser.parse_args();

  cap = cv2.VideoCapture(args.input);
  orig_size = (int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)));
  size = orig_size;
  if args.resize != None:
    if len(args.resize) < 2:
      sys.exit('resize の値が不正');
    size = (args.resize[0], args.resize[1]);
  fps = int(cap.get(cv2.cv.CV_CAP_PROP_FPS));
  if args.fps != None:
    fps = args.fps;
  ofname = re.sub(r'\.[^.]*$','',args.input)+'_'+time.strftime('%Y%m%d%H%M%S')+'.mov';
  if args.output != None:
    ofname = args.output;
    if not ofname.endswith('.mov'):
      ofname = ofname + '.mov';
  out = cv2.VideoWriter(ofname, cv2.cv.CV_FOURCC('m','p','4','v'), fps, size);
  mask = gen_mask(orig_size, args.margin[0], args.margin[1], args.margin[2], args.margin[3]);
  frame = 0;

  while cap.isOpened():
    ret,im_orig = cap.read();
    if ret == True:
      frame = frame + 1;
#      cv2.imshow('orig_view', im_orig);
      if args.skip > 0 and frame%args.skip != 0:
        continue;
      im = enhance_image(Image.fromarray(im_orig), args.saturation, args.contrast, args.brightness, args.sharpness);
      im_blur = gen_blurred_image(im, args.blur);
      im = np.array(paste_image(im, im_blur, mask));
      if args.resize != None:
        im = cv2.resize(im, size);

      cv2.imshow('view', im);
      out.write(im);
      key = cv2.waitKey(1);
      if key == 27:
        break;
      if args.limit != None and frame > args.limit:
        break;
    else:
      break;

  out.release();
  cap.release();
  cv2.destroyAllWindows();
  # bye
