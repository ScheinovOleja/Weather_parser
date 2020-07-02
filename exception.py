#  исключения
class GetExcept(BaseException):

    def __str__(self):
        return 'Введены неверные данные'
