import json
import sys

print(f"Beer Name: {sys.argv[1]}")
print(f"Quantity: {sys.argv[2]}")

beer_name = sys.argv[1]
beer_quantity = int(sys.argv[2])


def sort_by_quantity(item):
    return int(item["quantity"])


def find_beer_line_items(datas, beer):
    found_items = []
    for data in datas:
        if "beer" not in data:
            continue

        if data["beer"] == beer:
            found_items.append(data)

    return found_items


def find_permutations(line_items, quantity):
    line_items.sort(key=sort_by_quantity, reverse=True)
    least_amount = int(line_items[-1]["quantity"])
    remaining = quantity
    perm = {}
    while remaining >= least_amount:
        for item in line_items:
            item_quantity = int(item["quantity"])
            if item_quantity <= remaining:
                if "to_buy" not in item:
                    item["to_buy"] = 0
                remaining -= item_quantity
                item["to_buy"] += 1
                perm[item["title"]] = item
    return perm


def print_results(perms):
    total = 0
    for perm in perms.values():
        total += int(perm["quantity"]) * perm["to_buy"]
        print(f"Buy: {perm['to_buy']}x {perm['title']} - {perm['quantity']}")
    print(f"For a total of {total}")


with open("beers.json") as json_blob:
    datas = json.load(json_blob)
    line_items = find_beer_line_items(datas, beer_name)
    perms = find_permutations(line_items, beer_quantity)

    print_results(perms)
