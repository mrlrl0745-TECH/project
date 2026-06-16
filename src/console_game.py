import time
coins = 0.0
income = 1.0
owned = ['Scratch']
while True:
    coins += income * 0.5
    print(f'Монеты: {coins:.1f} | Доход: {income}/сек')
    cmd = input('buy python / quit: ')
    if cmd == 'buy python' and coins >= 50:
        coins -= 50
        income += 2
        owned.append('Python')
    elif cmd == 'quit':
        break
    time.sleep(0.5)
