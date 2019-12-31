module.exports = function (RED) {
	function OnFiveMinuteNode(n) {
		RED.nodes.createNode(this, n);
		let node = this;
		node.on('input', function (msg) {
			msg.payload = msg.payload.toLowerCase();
			node.send(msg);
		});
	}

	RED.nodes.registerType('onFiveMinute', OnFiveMinuteNode);
};
