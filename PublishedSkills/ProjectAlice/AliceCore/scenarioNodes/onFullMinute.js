module.exports = function (RED) {
	function OnFullMinuteNode(config) {
		RED.nodes.createNode(this, config);
		let node = this;
		node.on('input', function (msg) {
			msg.payload = msg.payload.toLowerCase();
			node.send(msg);
		});
	}

	RED.nodes.registerType('onFullMinute', OnFullMinuteNode);
};
