import datetime
import re
from typing import Optional

from logger import get_logger

logger = get_logger(__name__)

W3C_XML_DATETIME: str = "%Y-%m-%dT%H:%M:%S.%fZ"
MESSAGE_REGEX = re.compile('(?P<lat>-?\d+.?\d+)\s+(?P<lon>-?\d+.?\d+)\s+(?P<description>.*)')


def cot_time(cot_stale: Optional[int] = None) -> str:
    time = datetime.datetime.now(datetime.timezone.utc)
    if cot_stale:
        time = time + datetime.timedelta(seconds=int(cot_stale))
    return time.strftime(W3C_XML_DATETIME)


def parse_message(message: str) -> Optional[tuple[float, float, str]]:
    m = re.match(MESSAGE_REGEX, message)

    if not m or len(m.groups()) != 3:
        logger.error(f'Could not parse message: "{message}"')
        return

    lat_str, lon_str, description = m.groups()
    lat = validate_latitude(lat_str)
    lon = validate_longitude(lon_str)

    if not lat or not lon:
        return

    return lat, lon, description


def validate_float(parsed: str, val_min: float, val_max: float) -> Optional[float]:
    try:
        value = float(parsed)
    except ValueError:
        logger.error(f'Value is not float: {parsed}')
        return None

    if not val_max > value > val_min:
        logger.error(f'Value is out of bounds: {parsed}')
        return None

    return value


def validate_latitude(parsed: str) -> Optional[float]:
    return validate_float(parsed, -90.0, 90.0)


def validate_longitude(parsed: str) -> Optional[float]:
    return validate_float(parsed, -180.0, 180.0)