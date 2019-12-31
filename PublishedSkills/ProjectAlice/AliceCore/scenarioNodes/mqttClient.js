import * as mqtt from "mqtt";

module.exports = function (RED) {
	"use strict";

	function AliceNode(n) {
		RED.nodes.createNode(this, n);
		this.connecting = false;
		this.connected = false;
		this.client = '';

		this.users = {};
		let node = this;

		this.connect = function () {
			if (!node.connected && !node.connecting) {
				node.connecting = true;

				try {
					node.client = mqtt.connect('mqtt://localhost:1883');
					node.client.setMaxListeners(0);
					node.client.on('connect', function () {
						node.connecting = false;
						node.connected = true;
						console.log('Mqtt connected');
						node.log(RED._('mqtt.state.connected', {broker: ('scenarios@projectalice')}));
						for (let id in node.users) {
							if (node.users.hasOwnProperty(id)) {
								node.users[id].status({
									fill: 'green',
									shape: 'dot',
									text: 'node-red:common.status.connected'
								});
							}
						}
					});

					// Birth message
					node.client.publish('projectalice/events/scenariosConnected', '');

				} catch (error) {
					console.log('Error connecting to mqtt: ' + error);
				}
			}
		}
	}
};
