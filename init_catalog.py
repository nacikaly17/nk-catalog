#!/usr/bin/env python

"""
Module "init_catalog" create catalog.db
with example content to test the application.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model_catalog import Category, Base, Item, User, engine


# Create database session ( engine is created in model_catalog )
DBSession = sessionmaker(bind=engine)
session = DBSession()


def print_categories():
    categories = session.query(Category).all()
    output = ' '
    for category in categories:
        txt = str(category.id)
        txt += ' : ' + category.name + ' : ' + str(category.user.id)
        txt += ' : ' + category.user.username
        txt += ' : ' + category.user.email
        print(txt)
        items = session.query(Item).filter_by(category_id=category.id)
        for item in items:
            txt = '  -- ' + str(item.id)
            txt += ' : ' + ' Title = ' + item.title
            txt += '  Description = ' + item.description
            print(txt)

# Create 2 users
User1 = User(
  username="naci",
  email="naci@gmail.com",
  picture='',
  provider='local'
)
User1.hash_password("Udacity")
session.add(User1)
session.commit()

User2 = User(
  username="reviewer",
  email="",
  picture="""
https://pbs.twimg.com/profile_images/2671170543/
18debd694829ed78203a5a36dd364160_400x400.png""",
  provider='local'
)

User2.hash_password("Udacity")
session.add(User2)
session.commit()


##########################################################################
# 1. Category for Baseball
category = Category(user=User1, name="Baseball")
session.add(category)
session.commit()

# 1. Item for Category
item1 = Item(
  user=User1,
  title="Smal ball",
  category=category,
  description="very small")
session.add(item1)
session.commit()

##########################################################################

# 2. Category for Frisbee
category = Category(user=User2, name="Frisbee")
session.add(category)
session.commit()

##########################################################################

# 3. Category for Snowboarding
category = Category(user=User1, name="Snowboarding")
session.add(category)
session.commit()

# 1. Item for Category for Snowboarding
item1 = Item(
  user=User1,
  title="Snowboard",
  category=category,
  description="The hat"
)
session.add(item1)
session.commit()

##########################################################################

# 4. Category for Rock Climbing
category = Category(user=User2, name="Rock Climbing")
session.add(category)
session.commit()

##########################################################################

# 5. Category for Foosball
category = Category(user=User1, name="Foosball")
session.add(category)
session.commit()

##########################################################################

# 6. Category for Skating
category = Category(user=User2, name="Skating")
session.add(category)
session.commit()

##########################################################################

# 7. Category for Hockey
category = Category(user=User1, name="Hockey")
session.add(category)
session.commit()

##########################################################################

# 8. Category for Basketball
category = Category(user=User2, name="Basketball")
session.add(category)
session.commit()

# 1. Item for Category for Basketball
item1 = Item(
  user=User2,
  title="Ball",
  category=category,
  description="Big ball"
)
session.add(item1)
session.commit()

##########################################################################

# 8. Category for Soccer
category = Category(user=User2, name="Soccer")
session.add(category)
session.commit()

# 1. Item for Category for Soccer
item1 = Item(
  user=User2,
  title="Soccer Cleats",
  category=category,
  description="The shoes"
)
session.add(item1)
session.commit()

# 2. Item for Category for Soccer
item2 = Item(
  user=User1,
  title="Jersey",
  category=category,
  description="The shirt"
)
session.add(item2)
session.commit()

##########################################################################

print ("added Categories and  its Items!")
print_categories()
