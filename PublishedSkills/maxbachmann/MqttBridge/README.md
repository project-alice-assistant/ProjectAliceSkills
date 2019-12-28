# MqttBridge

### Download

##### > WGET method
```bash
wget http://skills.projectalice.ch/MqttBridge -O ~/ProjectAlice/system/skillInstallTickets/mqtt.install
```

### Description
bridge events between alice and mqtt.
All events that are shared with skills will create the following MQTT Message:
```
projectalice/events/<eventName>/<eventArguments>
```
the event arguments are a string converted dict, with the structure:
```
'{
	"<argumentName>": <value>,
	...
}'
```

- Version: 0.0.3
- Author: maxbachmann
- Maintainers: N/A
- Alice minimum Version: 1.0.0-a5
- Requirements: N/A

