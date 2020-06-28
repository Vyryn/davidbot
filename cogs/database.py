import random

import discord
from discord.ext import commands
import mysql.connector as mariadb
from mysql.connector import IntegrityError, InterfaceError, OperationalError

from functions import auth, now
from privatevars import DBUSER, DBPASS

global cursor
global db


def connect():
    global cursor, db
    try:
        db = mariadb.connect(
            host='localhost',
            user=DBUSER,
            password=DBPASS,
            database='datacamp'
        )
        cursor = db.cursor()
        print('Connected to database.')
    except:
        print('Could not connect to database.')
        print(f'An unexpected error occurred when trying to connect to the database for connect() at {now()}.')
        pass


def disconnect():
    db.close()


def pquery(query):
    connect()
    cursor.execute(query)
    return cursor.fetchall()


def adduser(user: discord.User, rsi, languages, location, joined_rsi, rsi_number, joined, hr_rep):
    connect()
    query = "INSERT INTO users (id, name, user_name, rsi, rsi_link, languages, location, joined_rsi, rsi_number, " \
            "joined, hr_rep) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
    rsi_link = f'https://robertsspaceindustries.com/citizens/{rsi}'
    values = (
        user.id, user.name, str(user), rsi, rsi_link, str(languages), str(location), str(joined_rsi), int(rsi_number),
        str(joined), hr_rep)
    try:
        cursor.execute(query, values)
        db.commit()
        return f'{cursor.rowcount} record(s) added successfully.'
    except IntegrityError:
        return f'It looks like that user was already in the database.'
    except OperationalError:
        return f'Reconnecting to database. Retrying...'
        connect()
        try:
            cursor.execute(query, values)
            db.commit()
            return f'{cursor.rowcount} record(s) added successfully.'
        except IntegrityError:
            return f'It looks like that user was already in the database.'
        except OperationalError:
            return f'Sorry, I wasn\'t able to connect to the database right now. Try again later.'
    disconnect()


def get_rsi(member_id: int):  # Simply query the DB for a single RSI link from a given user id
    connect()
    query = "SELECT rsi_link FROM users WHERE id = (%s)"
    values = member_id
    cursor.execute(query, (values,))
    try:
        return_val = cursor.fetchall()[0][0]
    except IndexError:
        return_val = 'Not Found'
    disconnect()
    return return_val


def get_rsi_name(member_id: int):  # Simply query the DB for a single RSI handle from a given user id
    connect()
    query = "SELECT rsi FROM users WHERE id = (%s)"
    values = member_id
    cursor.execute(query, (values,))
    try:
        return_val = cursor.fetchall()[0][0]
    except IndexError:
        return_val = 'Not Found'
    disconnect()
    return return_val


class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Loading Cog {self.qualified_name}...')
        connect()
        # cursor.execute("SHOW DATABASES")
        # databases = cursor.fetchall()
        # print(f"Databases: {databases}")
        # cursor.execute("DROP TABLE users")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        if 'users' not in str(tables):
            print('Users table not found. Creating a new one...')
            cursor.execute("CREATE TABLE users "
                           "(id BIGINT(20) NOT NULL AUTO_INCREMENT PRIMARY KEY, "
                           "name VARCHAR(255), "
                           "user_name VARCHAR(255), "
                           "rsi VARCHAR(255), "
                           "rsi_link VARCHAR(255), "
                           "languages VARCHAR(255), "
                           "location VARCHAR(255), "
                           "joined_rsi VARCHAR(255), "
                           "rsi_number INT(10), "
                           "joined VARCHAR(255), "
                           "hr_rep VARCHAR(255))")
        print(f'I have the following tables:\n{pquery("SHOW TABLES")}')
        print(f'My Users table is configured thusly:\n{pquery("DESC users")}')
        print(f'Users:\n{pquery("SELECT * FROM users")}')
        # ALTER TABLE table_name DROP column_name
        # ALTER TABLE table_name ADD PRIMARY KEY(column_name)

        print(f'Cog {self.qualified_name} is ready.')

    def cog_unload(self):
        print(f"Closing {self.qualified_name} cog.")
        disconnect()

    @commands.command(name='listusers', description='Prints the list of users to the console.')
    @commands.check(auth(4))
    async def listusers(self, ctx):
        users = pquery("SELECT * FROM users")
        print(f'Users: {users}')
        names = [user[1] for user in users]
        numUsers = len(users)
        await ctx.send(
            f'The list of {numUsers} users has been printed to the console. Here are their names only:\n{names}')

    @commands.command(name='directq', description='Does a direct database querry.')
    @commands.check(auth(8))
    async def directq(self, ctx, *, query):
        """
        Does a direct database query. Not quite as dangerous as eval, but still restricted to Auth 8.
        """
        result = pquery(query)
        print(f'{ctx.author} executed a direct database query at {now()}:\n{query}\nResult was:\n{result}')
        try:
            await ctx.send(pquery(query))
        except InterfaceError:
            await ctx.send("Okay. There's no result from that query.")


def setup(bot):
    bot.add_cog(Database(bot))
