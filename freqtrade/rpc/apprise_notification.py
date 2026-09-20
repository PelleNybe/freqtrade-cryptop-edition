import logging

from freqtrade.enums import RPCMessageType
from freqtrade.rpc import RPC
from freqtrade.rpc.rpc_types import RPCSendMsg


logger = logging.getLogger(__name__)


class AppriseNotification(RPC):
    """
    Omni-Notification System using Apprise for Freqtrade - Crypto P Edition.
    Allows routing trade alerts to Signal, Slack, Matrix, SMS, etc.
    """

    def __init__(self, freqtrade) -> None:
        super().__init__(freqtrade)
        self._config = freqtrade.config
        self.apprise_config = self._config.get("apprise", {})
        self.enabled = self.apprise_config.get("enabled", False)

        if self.enabled:
            try:
                import apprise

                self.apobj = apprise.Apprise()

                urls = self.apprise_config.get("urls", [])
                for url in urls:
                    self.apobj.add(url)

                logger.info(f"Apprise Notifications enabled with {len(urls)} endpoints.")
            except ImportError:
                logger.error("Apprise is not installed. Run `pip install apprise`.")
                self.enabled = False
            except Exception as e:
                logger.error(f"Failed to initialize Apprise: {e}")
                self.enabled = False

    def cleanup(self) -> None:
        pass

    def send_msg(self, msg: RPCSendMsg) -> None:
        if not self.enabled:
            return

        msg_type = msg.get("type")
        if msg_type in [
            RPCMessageType.STATUS,
            RPCMessageType.WARNING,
            RPCMessageType.STARTUP,
            RPCMessageType.BUY,
            RPCMessageType.SELL,
            RPCMessageType.EXIT,
        ]:
            try:
                # Basic text formatting. Could be expanded.
                title = f"Freqtrade - {msg_type.name if msg_type else 'Update'}"
                body = str(msg)

                # Apprise supports Markdown by default in many plugins
                self.apobj.notify(
                    body=body,
                    title=title,
                )
            except Exception as e:
                logger.warning(f"Failed to send Apprise notification: {e}")
