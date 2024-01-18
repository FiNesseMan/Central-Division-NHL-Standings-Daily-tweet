from nhlpy import NHLClient
from requests_oauthlib import OAuth1Session

import json
import os
import datetime
import pytz

access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
# Use the tokens directly if they are already available

oauth = OAuth1Session(
    consumer_key,  # consumer_key
    client_secret=consumer_secret,  # consumer_secret
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret,
)

def get_standings_sorted_by_points():
    client = NHLClient()
    standings = client.standings.get_standings()

    if 'standings' in standings:
        division_standings = {}
        for team_data in standings['standings']:
            division = team_data['divisionName']
            if division == "Metropolitan":
                team_name = team_data['teamName']['default']

                # Replace "Vegas Golden Knights" with "Vegas Knights"
                if team_name == "Vegas Golden Knights":
                    team_name = "Vegas Knights"

                team_info = {
                    'Team': team_name,
                    'GP': team_data['gamesPlayed'],
                    'W': team_data['wins'],
                    'L': team_data['losses'],
                    'OL': team_data['otLosses'],
                    'PTS': team_data['points']
                }

                if division not in division_standings:
                    division_standings[division] = []
                division_standings[division].append(team_info)

        # Sorting each division by points
        for division, teams in division_standings.items():
            division_standings[division].sort(key=lambda x: x['PTS'], reverse=True)

        return division_standings
    else:
        return "Error: 'standings' key not found in API response."

# Example usage
standings_by_division = get_standings_sorted_by_points()

output = ""
if standings_by_division and "Metropolitan" in standings_by_division:
    output += "\nMetropolitan Division Standings:\n"
    for team in standings_by_division["Metropolitan"]:
        output += f"{team['Team']}, PTS: {team['PTS']}\n"
else:
    output = "Unable to retrieve Metropolitan Division standings."

eastern = pytz.timezone('US/Eastern')
current_time = datetime.datetime.now(eastern)

if current_time.hour == 17:
    # Prepare your tweet
    payload = {"text": output}

    # Making the request
    response = oauth.post("https://api.twitter.com/2/tweets", json=payload)

    # Handle the response
    if response.status_code != 201:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )

    print("Response code: {}".format(response.status_code))