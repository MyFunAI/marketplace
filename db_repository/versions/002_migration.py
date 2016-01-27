from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
topics = Table('topics', pre_meta,
    Column('customer_id', INTEGER),
    Column('topic_id', INTEGER),
)

category = Table('category', post_meta,
    Column('category_id', Integer, primary_key=True, nullable=False),
)

category_tags = Table('category_tags', post_meta,
    Column('expert_id', Integer),
    Column('category_id', Integer),
)

following_experts = Table('following_experts', post_meta,
    Column('customer_id', Integer),
    Column('expert_id', Integer),
)

following_topics = Table('following_topics', post_meta,
    Column('customer_id', Integer),
    Column('topic_id', Integer),
)

paid_topics = Table('paid_topics', post_meta,
    Column('customer_id', Integer),
    Column('topic_id', Integer),
)

topic = Table('topic', post_meta,
    Column('topic_id', Integer, primary_key=True, nullable=False),
    Column('body', String(length=500)),
    Column('title', String(length=100)),
    Column('timestamp', DateTime),
    Column('rate', Float),
    Column('expert_id', Integer),
)

expert = Table('expert', pre_meta,
    Column('user_id', INTEGER, primary_key=True, nullable=False),
    Column('degree', VARCHAR(length=10)),
    Column('university', VARCHAR(length=50)),
    Column('major', VARCHAR(length=50)),
    Column('rating', FLOAT),
    Column('needed_count', INTEGER),
    Column('serving_count', INTEGER),
    Column('category_1_index', INTEGER),
    Column('category_2_index', INTEGER),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['topics'].drop()
    post_meta.tables['category'].create()
    post_meta.tables['category_tags'].create()
    post_meta.tables['following_experts'].create()
    post_meta.tables['following_topics'].create()
    post_meta.tables['paid_topics'].create()
    post_meta.tables['topic'].columns['expert_id'].create()
    pre_meta.tables['expert'].columns['category_1_index'].drop()
    pre_meta.tables['expert'].columns['category_2_index'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['topics'].create()
    post_meta.tables['category'].drop()
    post_meta.tables['category_tags'].drop()
    post_meta.tables['following_experts'].drop()
    post_meta.tables['following_topics'].drop()
    post_meta.tables['paid_topics'].drop()
    post_meta.tables['topic'].columns['expert_id'].drop()
    pre_meta.tables['expert'].columns['category_1_index'].create()
    pre_meta.tables['expert'].columns['category_2_index'].create()
