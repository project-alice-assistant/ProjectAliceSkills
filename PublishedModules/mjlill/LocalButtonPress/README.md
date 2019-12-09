# LocalButtonPress

### Download

##### > WGET method
```bash
wget http://modules.projectalice.ch/LocalButtonPress -O ~/ProjectAlice/system/moduleInstallTickets/LocalButtonPress.install
```

##### > Alice CLI method
```bash
./alice add module mjlill LocalButtonPress
```

### Description
Press an imaginary button on or off

 The Google AIY hat has 500ma drivers on 4 gpio pins and I use one to turn on a work space light.
 It would be nice to ask Alice to do that for me and this is my attempt to put all the pieces
 together for a module. This can use any free gpio for a non AIY system, just use a resistor and a led. 
 Edit the python script to assign a different gpio pin


- Version: 1.0.66
- Author: mjlill
- Maintainers:
  - Psycho
  - maxbachmann
- Alice minimum Version: 1.0.0-a4
- Conditions:
  - en
- Requirements: 
  - RPI.GPIO

