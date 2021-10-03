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
    "bearer_token": "<API access token>"
  }
}
```
[How do I obtain an API access token in the Canvas Data Portal? ](https://community.canvaslms.com/t5/Admin-Guide/How-do-I-obtain-an-API-access-token-in-the-Canvas-Data-Portal/ta-p/157)


## Running

```sh
python src/main.py
```