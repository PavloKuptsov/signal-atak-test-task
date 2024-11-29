import uuid
from xml.etree import ElementTree

from config import CLIENT_IP, CLIENT_PORT, DEFAULT_HAE, DEFAULT_CE, DEFAULT_LE, DEFAULT_STALE_S, DEFAULT_TYPE
from socket_connection import SocketConnection
from utils import cot_time, parse_message
from logger import get_logger

logger = get_logger(__name__)

def generate_cot(lat: float, lon: float, description: str) -> bytes:
    root = ElementTree.Element('event')
    root.set('version', '2.0')
    root.set('type', DEFAULT_TYPE)
    root.set('uid', str(uuid.uuid4()))
    root.set('how', 'm-g')
    root.set('time', cot_time())
    root.set('start', cot_time())
    root.set('stale', cot_time(DEFAULT_STALE_S))
    pt_attr = {
        'lat': str(lat),
        'lon': str(lon),
        'hae': DEFAULT_HAE,
        'ce': DEFAULT_CE,
        'le': DEFAULT_LE
    }
    point = ElementTree.SubElement(root, 'point', attrib=pt_attr)
    detail = ElementTree.SubElement(root, 'detail')
    contact = ElementTree.SubElement(detail, 'contact', attrib={'callsign': description})
    cot = ElementTree.tostring(root)
    logger.info(f'Formed CoT message: {cot}')
    return cot


if __name__ == '__main__':
    msg = '50.4461186 -200 test invalid latitude'
    parsed = parse_message(msg)
    if parsed:
        data = generate_cot(*parsed)
        with SocketConnection(CLIENT_IP, CLIENT_PORT) as socket:
            socket.send(data)