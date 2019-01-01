# Automata

Airflow project to scrape r/progmetal each day, and aggregate them into a spotify playlists
for each week.

## Setup
`cp airflow_variables_api_config_template.json`

Add your own reddit client secrets and spotify secrets

The OAuth token is cached by spotify under the `~/.cache-{userid}` file. Copy
the contents entire and put it under `SPOTIFY_CLIENT_TOKEN_CACHE`.

This is deployed using astronomer
