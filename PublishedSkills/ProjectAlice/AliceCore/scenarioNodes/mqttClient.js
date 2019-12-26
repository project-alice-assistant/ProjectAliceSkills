module.exports = function (RED) {
    function MQTTClientNode(n) {
        RED.nodes.createNode(this, n);
        this.host = n.host;
        this.port = n.port;

        this.connect = function () {
            try {
                this.client = mqtt.connect('mqtt://' + this.host + ':' + this.port)
            } catch (error) {
                console.log(error)
            }
        }
    }

    RED.nodes.registerType('mqtt-client', MQTTClientNode);
};
