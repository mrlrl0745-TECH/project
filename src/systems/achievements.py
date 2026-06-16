ACHIEVEMENTS = [
{'id': 'first_python', 'title': 'Hello World', 'check': lambda p: has_lang(p, 'python')},
{'id': 'millionaire', 'title': 'Миллионер', 'check': lambda p: p.coins >= 1_000_000},
]
def check_achievements(player, unlocked: set) -> list[str]:
    new = []
    for a in ACHIEVEMENTS:
        if a['id'] not in unlocked and a['check'](player):
            unlocked.add(a['id'])
            new.append(a['title'])
    return new
