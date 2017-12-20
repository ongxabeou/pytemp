# pytemp is python template project

I am writing this project to support backend service projects.
It undertakes the following functions.


- Automatic JWT authentication for API
- support local caching and singleton to manage memory.
- Provides HTTP validate solutions for RESTFull.
- Automatic logging and fault management.
- Provides OOP solution for the controller.
- Support multi language with VI and EN

The project will continue to improve after I have learned from
new projects, or ideas from the community.

## Install

    pip instal -r requirement
    py app

## Usage

See how to install the api in the bot.py file

## Apis

Method PUT BOT

```
curl -X PUT \
http://localhost:5000/api/v1.0/bot/bot_single_seller_shop_pizza_express \
-H 'authorization: Basic bliauwbralwiubnawk24114eobn' \
-H 'content-type: application/json' \
-d '{
    "id": 1245,
    "name": "Tuấn Anh",
    "age": 5,
    "gender": 4,
    "message": "Chào"
}'
```

Method GET BOT

```
curl -X GET \
http://localhost:5000/api/v1.0/bot/bot_single_seller_shop_pizza_express \
-H 'authorization: Basic bliauwbralwiubnawk24114eobn'
```

Method SET BOT

```
curl -X PATCH \
  http://localhost:5000/api/v1.0/bot/bot_single_seller_shop_pizza_express \
  -H 'authorization: Basic cawiuvnleruivkurwi2938r6lawihvw49fj123452' \
  -H 'content-type: application/json' \
  -d '{
    "consumer": {
        "address": "19 Dịch Vọng",
        "id": "shop_pizza_express",
        "name": "cửa hàng Pizza Express",
        "phone": "09888-------30588",
        "email": "pizza.Express@Express",
        "product": "bánh Pizza",
        "unit": "Chiếc"
    },
    "desc": "cửa hàng Pizza Express",
    "id": "bot_single_seller_shop_pizza_express",
    "meta_class": {
        "class_name": "BotSingleSeller",
        "module_name": "controllers.bot_single_seller"
    },
    "name": "Ngọc Trinh",
    "nlp_key": "bot_single_seller",
    "token": "bliauwbralwiubnawk24114eobn"
}'
```

* param body of request

![request body](https://github.com/ongxabeou/pytemp/raw/master/resources/images/1.png)

* param Authorization header of request

![request header](https://github.com/ongxabeou/pytemp/raw/master/resources/images/2.PNG)

* param Json has complex architecture

![request dùng cấu trúc json phúc tạp](https://github.com/ongxabeou/pytemp/raw/master/resources/images/3.PNG)

### Versioning

The default API version is `20171210`.