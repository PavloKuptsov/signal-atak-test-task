from signalbot import SignalBot, Command, Context

from config import SIGNAL_SERVICE, PHONE_NUMBER, CLIENT_IP, CLIENT_PORT
from cot import generate_cot
from logger import get_logger
from socket_connection import SocketConnection
from utils import parse_message

logger = get_logger(__name__)


class SendCotCommand(Command):
    async def handle(self, c: Context):
        logger.info(f'Message received: {c.message.text}')
        parsed = parse_message(c.message.text)
        if parsed:
            data = generate_cot(*parsed)
            with SocketConnection(CLIENT_IP, CLIENT_PORT) as socket:
                socket.send(data)


if __name__ == '__main__':
    bot = SignalBot({
        'signal_service': SIGNAL_SERVICE,
        'phone_number': PHONE_NUMBER
    })
    bot.register(SendCotCommand())
    bot.start()