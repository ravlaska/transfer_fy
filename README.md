# transfer_fy
Simple project written in Python [Flask] for Spotify playlists export/import.

<b>Instruction:</b>
1. Create Spotify App for API access [https://developer.spotify.com/].
    - In redirect URI you need addres that ends with ```/callback```
2. Configure Spotify App parameters in ```'transfer_fy-service/configs/params'```
3. Run this project:
    - In Docker container: ```docker-compose up -d```
        - You can configure it in ```docker-compose.yml```
    - Without contenerization: ```python3 app.py```
        - You need to install: ```python3, python3-pip``` and pip install: ```flask, requests, wheel, uwsgi```
