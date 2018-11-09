#!/usr/bin/env python3
import pickle

filename = "/root/Documents/Scripts/lib/wifi_database.pkl"

def main():
    with open(filename, 'rb') as file:
        L = pickle.load(file)
    for wifi in L:
        if wifi.get('wps_pin', '') or wifi.get('wpa_psk', ''):
            for key in ('essid', 'bssid', 'channel', 'wpa_psk', 'wps_pin', 'power'):
                print("{}: {}".format(key, wifi.get(key, '')))
            print('')

if __name__ == '__main__':
    main()
