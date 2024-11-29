# signal-atak-test-task
Signal bot to send geolocation and target information to an ATAK (Android Team Awareness Kit) client.

## Basic approach
The bot uses dedicated Python library, [signalbot](https://pypi.org/project/signalbot/) and [dockerized signal-cli](https://github.com/bbernhard/signal-cli-rest-api) to communicate with Signal and plain TCP socket connection to TAK clients.
The message sent to the connected Signal account is received by the bot, parsed for latitude, longitude and description (latitude and longitude values are validated) and sent via `tcp://<client_ip>:4242` straight to the client. The port 4242 is open by default on ATAK and WinTAK clients specifically for this purpose.

## Setup and run
1. Run docker-compose to start Signal REST API CLI:
```bash
	docker-compose up
```
2. Open http://127.0.0.1:8081/v1/qrcodelink?device_name=local to link your account with the signal-cli-rest-api server
3. In your Signal app, open settings and scan the QR code. The server can now receive and send messages. The access key will be stored in ./signal-api directory.
4. Set the following env variables (alternatively, edit the default values in `config.py`): 
   - PHONE_NUMBER
   - CLIENT_IP
5. Run `main.py` in whatever way you see fitting

## CoT data protocol
Cursor-on-Target protocol messages are XML-based. The basic message follows structure like this:
```xml
<?xml version='1.0' standalone='yes'?>
<event version="2.0"
	uid="J-01334"
	type="a-h-A-M-F-U-M"
	time="2005-04-05T11:43:38.07Z"
	start="2005-04-05T11:43:38.07Z"
	stale="2005-04-05T11:45:38.07Z" >
  <detail>
  </detail>
  <point lat="30.0090027" lon="-85.9578735" ce="45.3"
       	 hae="-42.6" le="99.5" />
</event>
```

The schema is as follows:

| Element | Attribute | Opt/Req | Definition | XML Schema Type |
| --------- | --------- | --------- | --------- | --------- |
| Event | version | Req | Schema version of this event instance (e.g. 2.0) | Decimal equal to 2.0 |
| | type | Req | Hierarchically organized hint about event type | string of pattern "\w+(-\w+)*(;[^;]*)?" |
| | uid | Req | Globally unique name for this information on this event | string |
| | time | Req | time stamp: when the event was generated | dateTime |
| | start | Req | starting time when an event should be considered valid | dateTime |
| | stale | Req | ending time when an event should no longer be considered valid | dateTime |
| | how | Req | Gives a hint about how the coordinates were generated | string of pattern “\w-\w" |
| | opex | Opt | | |
| | qos | Opt | | |
| | access | Opt | | |
| Point | lat | Req | Latitude referred to the WGS 84 ellipsoid in degrees | decimal -90 to 90 inclusive |
| | lon | Req | Longitude referred to the WGS 84 in degrees | decimal -180 to 180 inclusive |
| | hae | Req | Height above the WGS ellipsoid in meters | decimal |
| | ce | Req | Circular 1-sigma or a circular area about the point in meters | decimal |
| | le | Req | Linear 1-sigma error or an altitude range about the point in meters | decimal |
| Detail | N/A | Opt | An optional element used to hold CoT sub-schema | empty element |

For more details, refer to [Cursor-on-Target Message Router User's Guide](https://www.mitre.org/sites/default/files/pdf/09_4937.pdf)

## Implementation notes
- UUID4 is used for `Event.uid` attribute
- Static "100.0" value is used for `Point.hae` attribute
- Static "10.0" value is used for `Point.ce` and `Point.le` attributes
- For our purposes, we'll use Details sub-element `Contact` with string attribute `callsign` to show coordinates description, as it’s shown in ATAK and WinTAK clients on the map alongside the marker itself.
- PoC doesn't try to parse the description to figure out the meaning and map it to marker types. This means that every created marker will have a static `a-f-G-U-C-I` type, a friendly infantry unit.
- Event.stale is set to be 60 seconds greater than `Event.start`, which means the markers will disappear from the client map a minute after creation.
- Current limited scope solution means we only have one Signal account and one CoT data recipient.
- Sending the data to a dedicated TAK Server is possible the same way, by TCP socket connection. The server then should share the received information with all connected clients. Though, available servers are complicated in installation and, especially, setting up (this knowledge is gained *the hard way*)
