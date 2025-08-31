from enum import Enum

from tortoise import Model, fields


class TransactionStatus(str, Enum):
    SUCCESS = 'success'
    PENDING = 'pending'
    FAILURE = 'failure'
    CANCELED = 'canceled'


class Currency(str, Enum):
    RUB = 'RUB'
    USD = 'USD'
    EUR = 'EUR'
    CNY = 'CNY'


class UserSocials(Model):
    id = fields.UUIDField(primary_key=True, null=False)
    user: fields.ForeignKeyRelation['Users'] = fields.ForeignKeyField(
        model_name='models.Users', related_name='socials', null=False
    )
    title = fields.CharField(max_length=64, null=True)
    value = fields.CharField(max_length=64, null=False)


class Users(Model):
    id = fields.UUIDField(primary_key=True, null=False)
    username = fields.CharField(max_length=32, unique=True, null=False)
    password_hash = fields.BinaryField(null=False)
    display_name = fields.CharField(max_length=64, null=False)
    has_avatar = fields.BooleanField(default=False)

    created_at = fields.DatetimeField(auto_now_add=True, null=False)

    socials: fields.ReverseRelation['UserSocials']

    # tracks: fields.ReverseRelation['Tracks']
    # liked_tracks: fields.ReverseRelation['Tracks']
    # followed_tracks: fields.ReverseRelation['TrackFollows']
    # track_listens: fields.ReverseRelation['TrackListens']

    followed_users: fields.ReverseRelation['UserFollows']
    followers: fields.ReverseRelation['UserFollows']


class UserFollows(Model):
    id = fields.UUIDField(primary_key=True, null=False)
    following_user: fields.ForeignKeyRelation['Users'] = fields.ForeignKeyField(
        model_name='models.Users', related_name='followed_users', null=False
    )
    followed_user: fields.ForeignKeyRelation['Users'] = fields.ForeignKeyField(
        model_name='models.Users', related_name='followers', null=False
    )
    created_at = fields.DatetimeField(auto_now_add=True, null=False)
