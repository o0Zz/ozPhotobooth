#!/bin/bash

function DisableScreenSaver()
{
	sed -i -e 's/\[Seat:\*\]/\[Seat:\*\]\nxserver-command = X -nocursor -s 0 -dpms/g' /etc/lightdm/lightdm.conf
}

function SetupAccessPoint()
{
	echo "Setup access point..."
	
	sudo apt-get install dnsmasq hostapd  -y
	
	sudo systemctl stop dnsmasq
	sudo systemctl stop hostapd

	(
		echo interface wlan0
		echo -e "\tstatic ip_address=192.168.4.1/24"
		echo -e "\tnohook wpa_supplicant"
	) > /etc/dhcpcd.conf
	
	if [ $? -ne 0 ]; then
		echo "Error while writing /etc/dhcpcd.conf"
		exit 1
	fi


	(
		echo interface=wlan0
		echo dhcp-range=192.168.4.2,192.168.4.250,255.255.255.0,10m
	) > /etc/dnsmasq.conf
	
	if [ $? -ne 0 ]; then
		echo "Error while writing /etc/dnsmasq.conf"
		exit 1
	fi
	
	
	(
		echo interface=wlan0
		echo driver=nl80211
		echo ssid=ozPhotoBooth
		echo hw_mode=g
		echo channel=7
		echo wmm_enabled=0
		echo macaddr_acl=0
		echo auth_algs=1
		echo ignore_broadcast_ssid=0
		echo \#wpa=2
		echo \#wpa_passphrase=123456789
		echo \#wpa_key_mgmt=WPA-PSK
		echo \#wpa_pairwise=TKIP
		echo \#rsn_pairwise=CCMP
	) > /etc/hostapd/hostapd.conf
	
	if [ $? -ne 0 ]; then
		echo "Error while writing /etc/hostapd/hostapd.conf"
		exit 1
	fi
	
	
	(
		echo DAEMON_CONF="/etc/hostapd/hostapd.conf"
	) > /etc/default/hostapd

	if [ $? -ne 0 ]; then
		echo "Error while writing /etc/default/hostapd"
		exit 1
	fi
	
	
	sudo systemctl enable dnsmasq
	sudo systemctl start dnsmasq

	sudo systemctl restart dhcpcd

	sudo systemctl unmask hostapd
	sudo systemctl enable hostapd
	sudo systemctl start hostapd
}

function SetupBootTxt()
{
	echo "Writing config.txt..."

	(
		echo \#**********************************************
		echo \# PhotoBooth Config
		echo \#**********************************************
		echo \#Overscan
		echo disable_overscan=0
		echo overscan_left=155
		echo overscan_right=165
		echo overscan_top=152
		echo overscan_bottom=152
		echo \#Enable camera
		echo start_x=1
		echo gpu_mem=128
		echo \# Force HDMI Mode
		echo hdmi_group=2
		echo hdmi_force_hotplug=1
		echo hdmi_drive=2
		echo \#35 = 1280x1024 60Hz
		echo hdmi_mode=35
		echo \#Disable camera led
		echo disable_camera_led=1
		echo \#Try to improve sound stop working
		echo dtparam=audio=on
		echo audio_pwm_mode=2
		echo disable_audio_dither=1
		echo hdmi_ignore_edid_audio=1
		echo hdmi_force_edid_audio=0
		echo \#**********************************************
	) >> /boot/config.txt
	
	if [ $? -ne 0 ]; then
		echo "Error while writing config.txt"
		exit 1
	fi
}

function SetupPackages()
{
	echo "Install packages..."
	sudo apt-get install git vim -y
	sudo apt-get install python3 python3-venv python3-pip python3-dev python3-setuptools -y #Python3
	sudo apt-get install libjasper-dev libatlas-base-dev libcblas-dev libjpeg-dev libtiff5-dev libqtgui4 libqt4-test -y #OpenCV
	sudo apt-get install zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.5-dev tk8.5-dev python-tk -y #Others
	sudo apt-get remove python3-pil -y
	sudo pip3 install zipstream Pillow opencv-python pygame
	
}

if [ "$(id -u)" != "0" ]; then
	echo "Error, please launch this script as root user"
	exit 1
fi

sudo apt-get update
sudo apt-get upgrade -y
	
SetupPackages

SetupBootTxt

SetupAccessPoint

DisableScreenSaver

#Autostart photobooth
mkdir -p /home/pi/.config/lxsession/LXDE-pi/
echo @sudo /usr/bin/python3 /home/pi/ozPhotoBooth/ozPhotobooth.py > /home/pi/.config/lxsession/LXDE-pi/autostart

echo "Please reboot your raspberry pi !"