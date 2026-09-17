#!/bin/bash
# Behavioural coordinate for a scope program run under xvfb: how much of the Type 30 face is lit,
# and whether successive frames differ. simh writes screenshot NAME as NAME.bmp.
# Gates (declared before the run): a frame with 20..20000 lit pixels of 512x512 is CONTENT (a blank
# scope is ~0, a saturated one ~262144); two frames with different sha256 are ANIMATION.
set -e
for f in frame1 frame2; do
  n=$(convert "$f.png.bmp" -threshold 10% -format "%[fx:round(mean*w*h)]" info:)
  echo "lit_pixels_$f=$n"
  convert "$f.png.bmp" "$f.png"
done
n2=$(convert frame2.png.bmp -threshold 10% -format "%[fx:round(mean*w*h)]" info:)
if [ "$n2" -ge 20 ] && [ "$n2" -le 20000 ]; then echo FRAME_HAS_CONTENT; else echo FRAME_EMPTY_OR_SATURATED; fi
if [ "$(sha256sum frame1.png | cut -c1-64)" != "$(sha256sum frame2.png | cut -c1-64)" ]; then echo FRAMES_DIFFER; else echo FRAMES_IDENTICAL; fi
sha256sum frame1.png frame2.png
