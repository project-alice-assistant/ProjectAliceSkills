cd ~
curl -sL https://deb.nodesource.com/setup_10.x | -E bash -
git clone https://github.com/Koenkk/zigbee2mqtt.git /opt/zigbee2mqtt
chown -R pi:pi /opt/zigbee2mqtt
cd /opt/zigbee2mqtt
npm install

cat >> /etc/systemd/system/zigbee2mqtt.service <<EOL
[Unit]
Description=zigbee2mqtt
After=network.target

[Service]
ExecStart=/usr/bin/npm start
WorkingDirectory=/opt/zigbee2mqtt
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOL
