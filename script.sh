#!/bin/bash

sudo systemctl unmask wpa_supplicant.service;sudo ip link set dev wlxb4b0240913e2 down;sudo iw dev wlxb4b0240913e2 set type managed;sudo ip link set dev wlxb4b0240913e2 up;sudo service network-manager restart
