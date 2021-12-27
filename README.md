# canvas-download
## Requirements
- [docker](https://docs.docker.com/get-docker/) or [python](https://www.python.org/)

## Running

### Docker

1. Create & run the container 
``` sh
docker run -it -v canvas-download_data:/app/data -v ${PWD}/downloads:/app/downloads --name canvas-download ghcr.io/vdbe/canvas-download:release
```
You can change `${PWD}/downloads` to a location of your choosing,
all downloaded files will be placed here

2. Run existing container
``` sh
docker start -i canvas-download
```
You can leave out the `-i` if you don't want to attach to the containers STDIN & STDOUT/STEDERR

- To update the local files run the container again as shown in step 2

- If you want to see what happend after the container stopped
``` sh
docker logs canvas-download
```

- Remove container
``` sh
docker rm canvas-download
```

- Remove data volume
``` sh
docker volume rm canvas-download_data
```

### Native

0. Setup & activate venv (optional)

``` sh
python3 -m env
source env/bin/activate
```

1. Install dependencies

``` sh
pip3 install -r requirements-gui.txt
```

2. Run it

``` sh
python3 src/main.py [config file]
```

## Configuration
This is not needed if no `data/config/config.json` exists it will be created when you run `src/main.py` for the first time.
[How do I obtain an access token?](https://community.canvaslms.com/t5/Admin-Guide/How-do-I-manage-API-access-tokens-as-an-admin/ta-p/89)

Create `data/config/config.json` file in the root with the following content:
```json
{
  "canvas": {
    "endpoint": "<canvas endpoint>",
    "bearer_token": "<API access token>"
  },
  "db": {
    "directory": "data/db",
    "name": "db.json"
  },
  "download": {
    "parallel_downloads": 10,
    "download_locked": false,
    "path": "./downloads"
  }
}
```

