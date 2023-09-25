# Raspi-Setup

This repository contains:

- A helper script in image_tools/setup_image.py to quickly setup a Raspberry pi with ssh and public key authentication enabled

- Ansible configuration for setting up a working cloud backup system at home

The backup consists of two parts: Firstly, the Raspberry Pi has Syncthing running in order to synchronize files from other devices.
Secondly, once a day the synchronized files residing on the Pi are backed up to the cloud using restic.
