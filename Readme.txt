A. For windows (USB Camera):
1. Install python 3.7
2. install all whl files in whl folder using command prompt:
pip install "............"
replace ............ with filename.whl

3. install pillow using python shell:
pip install Pillow

B. For Raspberrypi (Both USB and PiCam):
1. Install and update every important library using:
   (for python2 use pip instead of pip3)
sudo apt-get update && sudo apt-get upgrade
sudo reboot now
sudo apt-get install -y build-essential cmake pkg-config
sudo apt-get install -y libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get install -y libxvidcore-dev libx264-dev
sudo apt-get install -y libgtk2.0-dev
sudo apt-get install -y libatlas-base-dev gfortran

sudo apt-get install -y python2.7-dev python3-dev (ignore this if you have latest python)

cd ~
wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.4.1.zip
unzip opencv.zip
wget -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/3.4.1.zip
unzip opencv_contrib.zip
sudo pip3 install numpy
cd ~/opencv-3.4.1/
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D ENABLE_PRECOMPILED_HEADERS=OFF \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-3.4.1/modules \
    -D BUILD_EXAMPLES=ON ..
make
sudo make install
sudo ldconfig
sudo pip3 install "picamera[array]"


C. For VM (after install RasOS - enable EAX/PAX)
sudo sh /media/cdrom/VBoxLinuxAdditions.run
sudo reboot

D. For SSH using shared hotspot
1. install tmux:
sudo atp install tmux

2. Connect raspberrypi to phone shared hotspot

3. SSH to:
raspberrypi.local
user: pi
password: raspberry

4. Run tmux from terminal:
tmux

5. run the python script:
GUI Version (with screen): DISPLAY=:0 python3 target.py
GUI Verison (without screen, run as background): DISPLAY=:0 python3 target.py &
Non-GUI script(with or without screen): python3 target.py


