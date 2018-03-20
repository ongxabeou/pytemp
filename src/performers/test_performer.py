from src.libs.subscribe import BasePerformer


class TestPerformer(BasePerformer):
    def do(self, item):
        """
        hàm thực hiện một yêu cầu, kiểm tra item.label xem có thuộc
        trách nhiệm của mình không nếu không thì return false, ngược lại thì thực hiện tác vụ
        :param item: dữ liệu yêu cầu thực thi bao gồm
        {
            'label':nhãn để xác định trách nhiệm,
            'entity_id': giá trị của một tham số trong hàm subscribe được quan tâm,
            'args': tham số đầu vào của hàm subscribe dang list,
            'kwargs': tham số đầu vào của hàm subscribe dang dict,
            'output': giá trị trả về của hàm subscribe
        }
        :return: trả về true nếu thực hiện và False nêu không thực hiện
        """
        if item['label'] != 'some_expensive_method':
            print('label %s not my responsibility' % item['label'])
            return False

        print(repr(item))
        return True
