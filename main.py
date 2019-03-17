from Kernel.kyServer import GameServer

if __name__ == '__main__0':
    GameServer("0.0.0.0", 4466).start()


a = [x for x in range(5)]
b = [x for x in range(5)]
c = [x for x in range(5)]

arr = [list(z) for z in zip(a, b, c)]

print(arr)
