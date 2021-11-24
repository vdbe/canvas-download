# canvas-download
## Requirements
- [python](https://www.python.org/)

## Installation

```sh
pip install -r requirements.txt
```

## Configuration
Create `config.json` file in the root with the following content:

```json
{
  "canvas": {
    "endpoint": "<canvas endpoint>",
    "bearer_tokens": [
      "<API access token>"
    ]
  },
  "db": {
    "directory": "data/db",
    "name": "db.json"
  },
  "download": {
    "parallel_downloads": 10,
    "download_locked": true,
    "path": "./downloads"
  }
}
```
[How do I obtain an access token?](https://community.canvaslms.com/t5/Admin-Guide/How-do-I-manage-API-access-tokens-as-an-admin/ta-p/89)


## Running

``` sh
python src/main.py
```

### Docker

1. Create & run the container 
``` sh
docker run -it -v ${PWD}/downloads:/app/downloads --name canvas-download ghcr.io/vdbe/canvas-download:release
```
You can provide an existing config.json by adding the following option `-v ${PWD}/config.json:/app/config.json`,
if you don't provide a config.json it will guide you to create one.
Change `/app/downloads` to download path in config.json (default is `app/downloads`)


2. Run existing container
``` sh
docker start convas-download
```

3. If you want to see progress attach to the container
``` sh
docker attach convas-download
```

- To update the local files run the container again as in step 2

- If you want to see what happend after the container stopped
``` sh
docker logs canvas-download
```
- Remove container

``` sh
docker rm canvas-download
```

