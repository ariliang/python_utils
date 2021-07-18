import peewee

from config.mysql import db_config


# database
class WanbuUpdateDB(peewee.Model):
    class Meta():
        database = peewee.MySQLDatabase(database='wanbu_update', **db_config)


# table
class MedalTable(WanbuUpdateDB):

    class Meta():
        primary_key = peewee.CompositeKey('user', 'medal_id')

    user = peewee.CharField()
    medal_id = peewee.CharField()
    visit_time = peewee.DateTimeField()
    create_time = peewee.DateTimeField()
    medal_name = peewee.CharField()
    desc = peewee.TextField()
    icon = peewee.TextField()


# test
if __name__ == '__main__':

    for item in MedalTable.select().order_by(MedalTable.user.cast('int')):
        print(item)