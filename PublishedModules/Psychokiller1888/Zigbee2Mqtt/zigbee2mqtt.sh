cd ~
curl -sL https://deb.nodesource.com/setup_10.x | -E bash -
git clone https://github.com/Koenkk/zigbee2mqtt.git /opt/zigbee2mqtt
chown -R pi:pi /opt/zigbee2mqtt
cd /opt/zigbee2mqtt
npm install