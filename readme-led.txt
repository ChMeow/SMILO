TO install LED:

sudo apt-get install gcc make build-essential python-dev git scons swig
sudo nano /etc/modprobe.d/snd-blacklist.conf

add the following line:
blacklist snd_bcm2835

sudo nano /boot/config.txt

comment out the following line:
#dtparam=audio=on

sudo reboot
git clone https://github.com/jgarff/rpi_ws281x
cd rpi_ws281x/
sudo scons
cd python
sudo python3 setup.py build
sudo python3 setup.py install

if failed, try:
curl -L http://coreelec.io/33 | bash

TO INSTALL DLIB:
sudo pip3 install dlib
sudo pip3 install imutils


*****IMPORTANT*****
RUN IT USING SUDO,eg:

sudo python3 script.py