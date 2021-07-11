class MenuItem:

        def __init__(self, item_name, item_description, price, required_choice_sets, optional_choice_sets):
            self.item_name = item_name
            self.item_description = item_description
            self.price = price
            self.required_choice_sets = required_choice_sets
            self.optional_choice_sets = optional_choice_sets

        def __eq__(self, other):
            if (self.item_name == other.item_name) and (self.item_description == other.item_description) and (self.price == other.price):
                if (len(self.required_choice_sets) == len(other.required_choice_sets)) and (len(self.optional_choice_sets) == len(other.optional_choice_sets)):
                    if all([self.required_choice_sets[i] == other.required_choice_sets[i] for i in range(len(self.required_choice_sets))]):
                        if all([self.optional_choice_sets[i] == other.optional_choice_sets[i] for i in range(len(self.optional_choice_sets))]):
                            return True
            return False

        def __ne__(self, other):
            return not self.__eq__(other)


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

        def __init__(self, name, price):
            self.name = name
            self.price = price

        def __eq__(self, other):
            return (self.name == other.name) and (self.price == other.price)

        def __ne__(self, other):
            return not self.__eq__(other)

        def __hash__(self):
            return hash(repr(self))

