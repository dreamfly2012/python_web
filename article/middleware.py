from .models import article

class MyMiddleware:
    def __init__(self,get_response):
        # self.get_response = get_response


        # print('init...')
        # return

    def __call__(self, request):
        # infos = article.objects.all()
        # for info in infos:
        #     print(info.date.strftime('%Y-%m-%d %H:%M:%S' ) )
        #     if(info.date.strftime('%Y-%m-%d %H:%M:%S' ) < '2019-05-16 23:59:59'):
        #         print(info.title + '数据需要更新')
        #     else:
        #         print(info.title + '数据不需要更新')

        # print('call....')
        # response = self.get_response(request)

        # return response