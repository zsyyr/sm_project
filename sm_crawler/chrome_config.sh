#!/bin/zsh
google-chrome --remote-debugging-port=9222 \
              --disk-cache-dir='/home/mfa/Project/sm_crawler_master/sm_crawler/data/chrome-cache/' \
              --disable-popup-blocking \
              --disable-infobars \
              --disable-images \
              --disable-flash-core-animation \
              --no-sandbox \
              --disk-cache-size=4000000000
            #   --headless