coins: float = 0.0
coins_per_second: float = 1.0
player_name: str = 'Новичок'


python_cost = 50
if coins >= python_cost:
    print('Можно купить Python!')
else:
    print('Нужно ещё монет')


languages = ['Scratch', 'Python', 'Rust']
for lang in languages:
    print(lang)


python = {'name': 'Python', 'cost': 50, 'income': 2}
print(python['income'])


def total_income(owned: list[dict]) -> float:
    return sum(lang['income'] for lang in owned)

class Language:
    def __init__(self, name: str, cost: int, income: int):
        self.name = name
        self.cost = cost
        self.income = income
