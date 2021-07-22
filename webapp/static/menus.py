from webapp.models.order import *
from webapp import db
from webapp.models.db_models import User
import json

# SUPER CUCAS MENU
menu_items, order_url, account_email = [], 'super-cucas-micheltorena', 'test@gmail.com'
menu_items.append(MenuItem("#1 Chorizo Burrito", "Mexican sausage, scrambled eggs, cheese, and potatoes.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#2 Protein Burrito", "Beef, scrambled eggs, cheese, and potatoes.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#3 Sausage Burrito", "Sausage scrambled eggs, cheese, and potatoes.", 10.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#4 Ham Burrito", "Ham, scrambled eggs, cheese, and potatoes.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#5 Veggie Burrito", "Grilled onions, bell peppers, zucchini, mushrooms, scrambled eggs, cheese, potatoes, and home style salsa.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#6 Carnitas Burrito", "Pork meat, scrambled eggs, cheese, and potatoes.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#7 Pastor Burrito", "Marinated pork meat, scrambled eggs, cheese, and potatoes.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#8 Eggs Burrito", "Scrambled eggs, cheese, and potatoes.", 7.99, [], [], "Breakfast"))
menu_items.append(MenuItem("#9 Ranchero Burrito", "Chorizo, bacon, scrambled eggs, cheese, potatoes, and ranchero salsa.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#10 Macho Burrito (Spicy)", "Marinated pork, jalapenos, scrambled eggs, cheese, potatoes, and macho salsa.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#11 Chicken Burrito", "Chicken, scrambled eggs, cheese, potatoes, and home style salsa.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#12 Energy Burrito", "Beef, veggies, scrambled eggs, cheese, potatoes, and home style salsa.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#13 Ham and Bacon Burrito", "Ham, bacon, scrambled eggs, cheese, and potatoes.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#14 Breakfast Plate", "Choice of meat, eggs, cheese, rice, beans, and tortillas.", 7.99, [ChoiceSet("Meat", [Choice("Chicken", 1.00), Choice("Beef", 0), Choice("Pork", 0)]), ChoiceSet("Egg Style", [Choice("Scrambled", 0), Choice("Over Easy", 0), Choice("Over Medium", 0), Choice("Over Hard", 0), Choice("Sunny-Side Up", 0)])], [ChoiceSet("Goodies", [Choice("Brownies", 1.00), Choice("Sprinkles", 0)])], "Breakfast"))
menu_items.append(MenuItem("#15 Chile Relleno Burrito", "Pico de gallo, scrambled eggs, cheese, and potatoes.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("Shrimp Burrito", "Grilled vegetables, rice, beans, cheese, and pico de gallo.", 11.94, [],[], "Burritos"))
menu_items.append(MenuItem("Combo Burrito", "Cheese, sour cream, onion, and cilantro.", 10.99, [],[], "Burritos"))

#User.query.filter_by(email_address=account_email).first().json_menu = json.dumps(Menu(menu_items, order_url), default=lambda x:x.__dict__)
#db.session.commit()
