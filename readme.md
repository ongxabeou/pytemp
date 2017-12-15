# pytemp project mẫu cho ngôn ngữ python

đảm nhiệm các chức năng nhiệm vụ sau.

- tự động check authentication theo chuẩn JWT
- hỗ trợ local caching, singleton.
- cung cấp các giải pháp HTTP validate.
- ghi logging tự động và quản lý lỗi.
- cung cấp giải pháp OOP cho controller.
- hỗ trợ đa ngôn ngữ với VI và EN

## Install

    pip instal -r requirement
    py app

## Usage

xem cách cài đặt trong file bot.py

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
![request body](https://github.com/ongxabeou/pytemp/raw/master/resources/images/1.png)

![request header](https://github.com/ongxabeou/pytemp/raw/master/resources/images/2.PNG)

![request dùng cấu trúc json phúc tạp](https://github.com/ongxabeou/pytemp/raw/master/resources/images/3.PNG)

### Versioning

The default API version is `20171210`.