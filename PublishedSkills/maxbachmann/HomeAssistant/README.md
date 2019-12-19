# HomeAssistant

### Download

##### > WGET method
```bash
wget http://skills.projectalice.ch/HomeAssistant -O ~/ProjectAlice/system/skillInstallTickets/HomeAssistant.install
```

### Description
bridge events between alice and HomeAssistant.
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

- Version: 0.0.1
- Author: maxbachmann
- Maintainers: 
- Alice minimum Version: 1.0.0-a4
- Requirements: N/A

