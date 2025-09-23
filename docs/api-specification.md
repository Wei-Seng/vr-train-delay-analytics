# API Specifications

## GET /delays/route/{fromStation}/{toStation}
Returns delay statistics between two stations.

- Parameters:
  - `fromStation` (string): Code of departure station.
  - `toStation` (string): Code of arrival station.
  - `start` (string, optional): Start date in YYYY-MM-DD.
  - `end` (string, optional): End date in YYYY-MM-DD.

- Sample Request:
GET /delays/route/HKI/TPE?start=2023-01-01&end=2023-01-31

- Sample Response:
{“route”: “Helsinki-Tampere”,“average_delay”: 6.5,“max_delay”: 45,“min_delay”: 0}


## GET /delays/stations/{stationCode}
Returns delay statistics for single station.

- Parameters:
  - `stationCode` (string): Station code.

- Sample Request:
GET /delays/stations/HKI

- Sample Response:
{“station”: “Helsinki”,“average_delay”: 4.2,“max_delay”: 40,“min_delay”: 0,“trend”: “stable”}


## GET /trains/{trainNumber}/events
Returns full event history for a given train.

- Parameters:
  - `trainNumber` (string): Train identifier.

- Sample Request:
GET /trains/IC123/events

- Sample Response:
{“trainNumber”: “IC123”,“events”: {“station”: “Helsinki”, “scheduled”: “08:30”, “actual”: “08:40”, “delay”: 10},{“station”: “Tampere”, “scheduled”: “10:30”, “actual”: “10:33”, “delay”: 3}}


All endpoints use HTTPS and return data in JSON format. Input parameters are validated and meaningful error messages are provided in case of invalid requests.