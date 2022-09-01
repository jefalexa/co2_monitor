# co2_monitor
Weigh CO2 tank in kegerator to measure CO2

- serial_average_01.py:  working script to modify
- read_serial.py:  production script, copy from working once satisfied

- copy read_serial.service to /etc/systemd/system/read_serial.service to run the script as a service.  
- Start/Stop/Monitor the service with 'systemctl status read_serial'

Writes logs to /var/log/co2mon.log

In order to console into the scale directly from the terminal:  
- Stop the service via systemctl
- Connect via screen /dev/ttyUSB0 9600
- Exit via Control A and then k