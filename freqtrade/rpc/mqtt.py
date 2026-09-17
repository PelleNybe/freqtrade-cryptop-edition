import json
import logging

from freqtrade.rpc import RPC
from freqtrade.rpc.rpc_types import RPCSendMsg


logger = logging.getLogger(__name__)


class MQTT(RPC):
    """
    Native MQTT Notification Provider for IoT integration on Edge devices.
    """

    def __init__(self, freqtrade) -> None:
        super().__init__(freqtrade)
        self._config = freqtrade.config
        self.mqtt_config = self._config.get("mqtt", {})
        self.enabled = self.mqtt_config.get("enabled", False)

        if self.enabled:
            logger.info("MQTT Notifications enabled. Attempting to initialize client...")
            try:
                import paho.mqtt.client as mqtt

                self.client = mqtt.Client(client_id="freqtrade_edge")

                if "username" in self.mqtt_config and "password" in self.mqtt_config:
                    self.client.username_pw_set(
                        self.mqtt_config["username"], self.mqtt_config["password"]
                    )

                host = self.mqtt_config.get("host", "127.0.0.1")
                port = self.mqtt_config.get("port", 1883)

                self.client.connect_async(host, port, 60)
                self.client.loop_start()
                logger.info(f"Connected to MQTT broker at {host}:{port}")
            except ImportError:
                logger.error(
                    "paho-mqtt missing. Run `pip install paho-mqtt` to use MQTT."
                )
                self.enabled = False
            except Exception as e:
                logger.error(f"Failed to initialize MQTT client: {e}")
                self.enabled = False

    def cleanup(self) -> None:
        if self.enabled and hasattr(self, "client"):
            self.client.loop_stop()
            self.client.disconnect()

    def send_msg(self, msg: RPCSendMsg) -> None:
        if not self.enabled:
            return

        topic_base = self.mqtt_config.get("topic", "freqtrade")
        msg_type = msg.get("type")

        # Publish generic payload
        topic = f"{topic_base}/{msg_type.name.lower() if msg_type else 'system'}"

        # Strip out non-serializable objects (like datetime) before JSON dump
        payload = {k: str(v) for k, v in msg.items()}

        try:
            self.client.publish(topic, json.dumps(payload))
            logger.debug(f"Published MQTT message to topic {topic}")
        except Exception as e:
            logger.warning(f"Failed to publish MQTT message: {e}")
