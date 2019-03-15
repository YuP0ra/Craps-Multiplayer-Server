# from threading import Thread, Lock
# import time
#
#
# class Player(Thread):
#     def __init__(self, name):
#         Thread.__init__(self)
#
#         self._name = name
#
#     def run(self,):
#         tmp = 1
#         for i in range(100):
#             tmp = tmp * i + 1
#             tmp = tmp * i + 1
#
#
# players = [Player(i) for i in range(1000)]
#
# a = time.time()
# for p in players:
#     p.start()
#
# print(time.time() - a)
