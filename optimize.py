import pickle
from functools import cmp_to_key

with open("save_names.pkl", "rb") as f:
    sellers = pickle.load(f)
with open("save_prices.pkl", "rb") as f:
    prices = pickle.load(f)
with open("save_cards.pkl", "rb") as f:
    cards = pickle.load(f)

def mycmp(a, b):
    return len(a[1]) - len(b[1])
"""    if len(a[1]) < len(b[1]):
        return -1
    elif len(a[1]) > len(b[1]):
        return 1
    else:
        return best_prices[a[0]] - best_prices[b[0]]"""

best_sellers = {}
best_prices = {}

def get_best():
    for card in cards:
        for seller in cards[card]:
            if seller in {"CrowsArena", "Filipe-Raq56"}: # doesn't ship to belgium
                continue
            if seller not in best_sellers:
                best_sellers[seller] = []
            if seller not in best_prices:
                best_prices[seller] = 0
            best_sellers[seller].append(card)
            best_prices[seller] += cards[card][seller]

    l1 = sorted(best_sellers.items(), key=cmp_to_key(mycmp), reverse=True)[:10]
    #if len(l1) > 0:
    #    print(len(l1[0][1]))
    l2 = []
    for t in l1:
        l2.append((t[0], best_prices[t[0]]))
    return l1, l2

temp_buy = []
temp_price = 0
while len(cards) > 0:
    best_sellers = {}
    best_prices = {}
    l1, l2 = get_best()
    temp_buy.append(l1[0])
    temp_price += l2[0][1]

    for c in l1[0][1]:
        cards.pop(c)


with open("save_cards.pkl", "rb") as f:
    cards = pickle.load(f)

to_buy = {}
final_price  = 0
for d in temp_buy:
    for card in d[1]:
        min_s = ""
        min_p = 10000
        for s in temp_buy:
            s = s[0]
            if cards[card].get(s, 10000) < min_p:
                min_s = s
                min_p = cards[card][s]
        final_price += min_p
        if min_s not in to_buy:
            to_buy[min_s] = []
        to_buy[min_s].append(card)


print(len(to_buy))
print(to_buy)
print(final_price)

