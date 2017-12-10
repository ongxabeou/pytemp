# dm.ai dialog mamagement ai

đảm nhiệm các chức năng nhiệm vụ sau.

- sử dụng wit.ai để làm xác định các intent và entity.
- lưu caching trên redis để giảm tại việc request lên wit.ai.
- cung cấp các api để import dữ liệu training.
- quản lý các dialog hội thoại.
- xây dựng kịch bản hội thoại.
- xây dựng interface để mở rộng phạm vị tương tác với hệ thống ngoài nhằm hoàn thiện dữ liệu cho hội thoại

## Install

    pip instal -r requirement
    python app

## Usage

xem cách cài đặt một bot trong file bot_single_saler

## API

### Versioning

The default API version is `20171230`.
You can target a specific version by setting the env variable `WIT_API_VERSION`.

### Wit class

The Wit constructor takes the following parameters:
* `access_token` - the access token of your Wit instance

A minimal example looks like this:

```python
from wit import Wit

client = Wit(access_token)
client.message('set an alarm tomorrow at 7am')
```