#!/usr/bin/env bash
interface="${1-wlo1}" # other common: 'wlan0'
interface_mon="${2-${interface}mon}"
sudo systemctl stop NetworkManager.service
sudo systemctl stop wpa_supplicant.service
rfkill unblock 1
sudo airmon-ng check kill
sudo airmon-ng start $interface
sudo airmon-ng start $interface_mon
