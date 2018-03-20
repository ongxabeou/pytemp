from src.libs.subscribe import SubscribeAssigner
from src.performers.test_performer import TestPerformer


def init_all_performer():
    SubscribeAssigner().add_performer(TestPerformer())