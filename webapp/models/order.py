from webapp.models.db_models import User

class Order():

    def __init__(self, order_items, order_url):
        self.order_items = order_items
        self.order_url = order_url

    def is_valid_order(self, menu):
        for order_item in self.order_items:

            # menu item must be part of the menu
            if order_item.menu_item not in menu.menu_items:
                return False

            # all required selections must be unique
            if not (len(order_item.required_selections) == len(set(order_item.required_selections))):
                return False

            # all optional selections must be unique
            if not (len(order_item.optional_selections) == len(set(order_item.optional_selections))):
                return False

            # all required selections must be an option given by the menu
            for required_selection in order_item.required_selections:
                if not any([required_selection in choice_set.choices for choice_set in order_item.menu_item.required_choice_sets]):
                    return False

            # all optional selections must be an option given by the menu
            for optional_selection in order_item.optional_selections:
                if not any([optional_selection in choice_set.choices for choice_set in order_item.menu_item.optional_choice_sets]):
                    return False

        return True

    def price(self):
        return sum([order_item.price() for order_item in self.order_items])

    def description(self):
        desc = ""
        i = 0
        for order_item in self.order_items:
            desc += order_item.menu_item.item_name + " x" + str(order_item.quantity) + ": $" + str(order_item.price())

            i += 1
            if i < len(self.order_items):
                desc += "\n"
        return desc
            

    def connected_account(self):
        return User.query.filter_by(order_url=self.order_url).first()


class OrderItem:

        def __init__(self, menu_item, required_selections, optional_selections, quantity, special_instructions):
            self.menu_item = menu_item
            self.required_selections = required_selections
            self.optional_selections = optional_selections
            self.quantity = quantity
            self.special_instructions = special_instructions

        def price(self):
            item_price = self.menu_item.price
            for required_selection in self.required_selections:
                item_price += required_selection.price
            for optional_selection in self.optional_selections:
                item_price += optional_selection.price
            return item_price*self.quantity


class ChoiceSet:

        def __init__(self, title, choices):
            self.title = title
            self.choices = choices

        def __eq__(self, other):
            if (self.title == other.title) and (len(self.choices) == len(other.choices)):
                if all([self.choices[i] == other.choices[i] for i in range(len(self.choices))]):
                    return True
            return False

        def __ne__(self, other):
            return not self.__eq__(other)


class Choice:

        def __init__(self, name, price, in_stock=True):
            self.name = name
            self.price = price
            self.in_stock = in_stock

        def __eq__(self, other):
            return (self.name == other.name) and (self.price == other.price)

        def __ne__(self, other):
            return not self.__eq__(other)

        def __hash__(self):
            return hash(repr(self))


class Menu:

    def __init__(self, menu_items, order_url):
        self.menu_items = menu_items
        self.order_url = order_url


class MenuItem:

        def __init__(self, item_name, item_description, price, required_choice_sets, optional_choice_sets, category, in_stock=True):
            self.item_name = item_name
            self.item_description = item_description
            self.price = price
            self.required_choice_sets = required_choice_sets
            self.optional_choice_sets = optional_choice_sets
            self.category = category
            self.in_stock = in_stock

        def __eq__(self, other):
            if (self.item_name == other.item_name) and (self.item_description == other.item_description) and (self.price == other.price):
                if (len(self.required_choice_sets) == len(other.required_choice_sets)) and (len(self.optional_choice_sets) == len(other.optional_choice_sets)):
                    if all([self.required_choice_sets[i] == other.required_choice_sets[i] for i in range(len(self.required_choice_sets))]):
                        if all([self.optional_choice_sets[i] == other.optional_choice_sets[i] for i in range(len(self.optional_choice_sets))]):
                            return True
            return False

        def __ne__(self, other):
            return not self.__eq__(other)


class ConvertJsonToOrder:

    def __init__(self, json_order, order_url):
        self.json_order = json_order
        self.order_url = order_url

    def order(self):
        order_items = []
        for json_order_item in self.json_order:
            order_items.append(ConvertJsonToOrder.json_order_item_to_class(json_order_item))
        return Order(order_items, self.order_url)

    @staticmethod
    def json_order_item_to_class(json_order_item):
        menu_item = ConvertJsonToOrder.json_menu_item_to_class(json_order_item['item'])
        required_selections = []
        for json_required_selection in json_order_item['required_selections']:
            required_selections.append(Choice(json_required_selection['name'], json_required_selection['price']))
        optional_selections = []
        for json_optional_selection in json_order_item['optional_selections']:
            optional_selections.append(Choice(json_optional_selection['name'], json_optional_selection['price']))
        return OrderItem(menu_item, required_selections, optional_selections, json_order_item['quantity'], json_order_item['special_instructions'])

    @staticmethod
    def json_menu_item_to_class(json_menu_item):
        required_choice_sets = []
        for json_required_choice_set in json_menu_item['required_choice_sets']:
            required_choice_sets.append(ConvertJsonToOrder.json_choice_set_to_class(json_required_choice_set))
        optional_choice_sets = []
        for json_optional_choice_set in json_menu_item['optional_choice_sets']:
            optional_choice_sets.append(ConvertJsonToOrder.json_choice_set_to_class(json_optional_choice_set))
        return MenuItem(json_menu_item['item_name'], json_menu_item['item_description'], json_menu_item['price'], required_choice_sets, optional_choice_sets, json_menu_item['category'])

    @staticmethod
    def json_choice_set_to_class(json_choice_set):
        choices = []
        for json_choice in json_choice_set['choices']:
            choices.append(Choice(json_choice['name'], json_choice['price']))
        return ChoiceSet(json_choice_set['title'], choices)

class ConvertJsonToMenu:

    def __init__(self, json_menu, order_url):
        self.json_menu = json_menu
        self.order_url = order_url

    def menu(self):
        menu_items = []
        for json_menu_item in self.json_menu:
            menu_items.append(ConvertJsonToOrder.json_menu_item_to_class(json_menu_item))
        return Menu(menu_items, self.order_url)
