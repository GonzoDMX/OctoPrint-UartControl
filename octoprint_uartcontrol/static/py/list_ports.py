#!/usr/bin/env python3

import serial.tools.list_ports


def list_serial_ports():
	port_list = ["Dummy"]
	ports = list(serial.tools.list_ports.comports())
	for p in ports:
		port_list.append(p.device)
		
	print(port_list)
	
list_serial_ports()
