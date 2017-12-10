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

Method PUT

```
    PUT /api/v1.0/bot/bot_single_seller_shop_pizza_express HTTP/1.1
    Host: localhost:5000
    Authorization: Basic bliauwbralwiubnawk24114eobn
    Content-Type: application/json
    Cache-Control: no-cache
    Postman-Token: c9004467-4a53-c7b3-03ae-a05440d5d642

    {
        "id": 1245,
        "name": "Tuấn Anh",
        "age": 5,
        "gender": 4,
        "message": "Chào"
    }
```

Method GET

```
    GET /api/v1.0/bot/bot_single_seller_shop_pizza_express HTTP/1.1
    Host: localhost:5000
    Authorization: Basic bliauwbralwiubnawk24114eobn
    Cache-Control: no-cache
    Postman-Token: 6ec7ca7b-475c-2082-6fe5-64f6b822b8e9
```

### Versioning

The default API version is `20171230`.
You can target a specific version by setting the env variable `WIT_API_VERSION`.