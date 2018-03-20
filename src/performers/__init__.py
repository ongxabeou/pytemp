from src.libs.subscribe import SubscribeAssigner
from src.performers.test_performer import TestPerformer

SubscribeAssigner().add_performer(TestPerformer())


class SUBSCRIBE_LABEL:
    UPDATE_BOT_CONFIG = 'update_bot_config'
    PUT_CUSTOMER = 'put_customer'
    DELETE_BOT_CONFIG = 'delete_bot_config'
