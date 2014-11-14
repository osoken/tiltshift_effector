tiltshift_effector
==================

.mov などの動画ファイルに、偽ティルトシフトエフェクトを掛けるPythonスクリプト。
Numpy, Scipy, OpenCV, Pillow を使用。

usage: python tiltshift.py [-h] [--flip FLIP] [--resize RESIZE]
                    [--margin MARGIN MARGIN MARGIN MARGIN] [--skip SKIP]
                    [--saturation SATURATION] [--contrast CONTRAST]
                    [--brightness BRIGHTNESS] [--sharpness SHARPNESS]
                    [--blur BLUR] [--fps FPS] [--limit LIMIT]
                    [--output OUTPUT]
                    input

positional arguments:
----

*  input:                 input file

optional arguments:
----

*  -h, --help:            show this help message and exit

*  --flip FLIP:           反転。0でx軸、1でy軸、-1で両方の軸について反転する。デフォルトは変更なし

*  --resize RESIZE:       画像サイズの変更。デフォルトは変更なし。width\*height e.g. 640\*360

*  --margin MARGIN MARGIN MARGIN MARGIN: 上のぼかし、上と焦点の間、焦点、下と焦点の間 の幅をそれぞれ、全体を1.0とした割合で与える。下のぼかし幅は残りに割り当てられる。(0.0から1.0の浮動小数。デフォルトは0.5 0.1 0.05 0.08)

*  --skip SKIP:           飛ばすフレーム数 (0以上の整数、0で全フレーム、デフォルトは0)

*  --saturation SATURATION:
                        彩度 (0.0以上の浮動小数、1.0で元と同じ。デフォルトは2.0)

*  --contrast CONTRAST:   コントラスト (0.0以上の浮動小数、1.0で元と同じ。デフォルトは1.2)

*  --brightness BRIGHTNESS:
                        明度 (0.0以上の浮動小数、1.0で元と同じ。デフォルトは1.0)

*  --sharpness SHARPNESS:
                        シャープネス (0.0以上の浮動小数、1.0で元と同じ。デフォルトは1.0)

*  --blur BLUR:           ぼかしの強さ (0.0以上の浮動小数、0.0でぼかしなし。デフォルトは4.0)

*  --fps FPS:             FPS
                        (1以上の整数。デフォルトは変更なし)

*  --limit LIMIT:         書き出すフレーム数のリミット
                        (1以上の整数。デフォルトは変更なし)

*  --output OUTPUT:       出力ファイル名。デフォルトは
                        [inputファイル名][日付時刻].mov

例
----

* 全てデフォルトで IMG_xxxx_[日付時刻].mov に出力
  - python tiltshift.py IMG_xxxx.mov
* 元動画と同じものを出力
  - python tiltshift.py IMG_xxxx.mov --contrast=1.0 --saturation=1.0 --blur=0
* 上下を反転
  - python tiltshift.py IMG_xxxx.mov --flip=-1
* マージンの調整（焦点をデフォルトよりやや上にかける）
  - python tiltshift.py IMG_xxxx.mov --margin 0.4 0.2 0.05 0.1
* 8倍速
  - python tiltshift.py IMG_xxxx.mov --skip=8 
* 動画の縦横のピクセル数を360pに指定
  - python tiltshift.py IMG_xxxx.mov --resize=640*360

