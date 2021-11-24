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
[How do I obtain an API access token in the Canvas Data Portal? ](https://community.canvaslms.com/t5/Admin-Guide/How-do-I-obtain-an-API-access-token-in-the-Canvas-Data-Portal/ta-p/157)


## Running

``` sh
python src/main.py
```

### Docker

1. Build the image
``` sh
docker build -t canvas-download .
```
This will copy config.json into the image

2. Create & run the container
``` sh
docker run -v ${PWD}/config.json:/app/config.json  -v ${PWD}/downloads:/app/downloads --name canvas-download canvas-download
```
Change `/app/downloads` to download path in config.json

3. Run existing container
``` sh
docker start convas-download
```

4. If you want to see progress attach to the container
``` sh
docker attach convas-download
```

- To update the local files run the container again as in step 3

- If you want to see what happend after the container stopped
``` sh
docker logs canvas-download
```

