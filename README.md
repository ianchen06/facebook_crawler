# Facebook fans page/public group crawler

A high performance Facebook fans page/public group crawler that utilizes cooperative multi-tasking via gevent

## Dependencies

* python 3.5+
* RethinkDB

## Getting Started

```
pip install -r requirements.txt`
```

```
cat << EOF > dev.env
export FB_ID=177612180793
export FB_ACCESS_TOKEN='EAACEdEose0cBAFYdIyGDyLJEnm4htkSvEkmjbYKQglIYe9vZAQ2jlLzItEiECPxymQSvG69pUPCAVo20hytwAfnByiGYLpHZAyTFS5JtcI4W47o58c7gV0Cf5LZA4tmeBVVFcZCn3DUFoo1e4fHUGYAiKWBqv2gkEr7M7szVNCXzr5V26VYk'
EOF
```

```
source dev.env
```

```
python crawler.py
```

if you would like to start from a particular URL(i.e. some pagination) you can put it as an arguments

```
python crawler.py https://graph.facebook.com/v2.8/177612180793/feed\?fields\=message,comments,likes,shares,created_time\&limit\=25\&__paging_token\=enc_AdCihd9CZBPMZAVFgjnRHJZBeAZBSbJV8ScKTSkvAjZA13hxAfQjH4DzbrhwV6WeINnW7OAH5mL2pGwvsLELlVU5G1zqzP1xXzXgp9mCkrt4ZAjFXpZCQZDZD\&access_token\=EAACEdEose0cBAFYdIyGDyLJEnm4htkSvEkmjbYKQglIYe9vZAQ2jlLzItEiECPxymQSvG69pUPCAVo20hytwAfnByiGYLpHZAyTFS5JtcI4W47o58c7gV0Cf5LZA4tmeBVVFcZCn3DUFoo1e4fHUGYAiKWBqv2gkEr7M7szVNCXzr5V26VYk\&until\=1430055001
```
