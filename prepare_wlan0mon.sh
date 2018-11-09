#!/usr/bin/env bash
airmon-ng check kill &&
airmon-ng start wlan0 &&
airmon-ng start wlan0mon