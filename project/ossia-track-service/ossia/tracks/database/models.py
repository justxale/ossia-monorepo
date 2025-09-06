import uuid

from tortoise import Model, fields

from ossia.tracks.enum import TrackStatus, TrackVisibility


class Tracks(Model):
    id: uuid.UUID = fields.UUIDField(primary_key=True)
    title = fields.CharField(max_length=32, null=False)
    description = fields.CharField(max_length=512, null=True)
    creator: fields.ForeignKeyRelation['Creators'] = fields.ForeignKeyField(
        'ossia.Creators', null=False, related_name='tracks'
    )

    has_cover = fields.BooleanField(default=False)
    duration = fields.IntField(default=-1)

    status = fields.CharEnumField(
        TrackStatus, default=TrackStatus.QUEUED, max_length=16
    )
    visibility = fields.CharEnumField(
        TrackVisibility, default=TrackVisibility.DRAFT, max_length=8
    )

    tags: fields.ManyToManyRelation['Tags'] = fields.ManyToManyField(
        'ossia.Tags', related_name='tracks'
    )

    created_at = fields.DatetimeField(auto_now_add=True)
    edited_at = fields.DatetimeField(auto_now=True)


class Tags(Model):
    id: uuid.UUID = fields.UUIDField(primary_key=True)
    value = fields.CharField(max_length=32, null=False, unique=True)

    tracks: fields.ManyToManyRelation[Tracks]


class Creators(Model):
    id: uuid.UUID = fields.UUIDField(primary_key=True, null=False)

    display_name = fields.CharField(32, null=False)
    url = fields.CharField(32, unique=True, null=True)
    description = fields.CharField(2 ** 11, null=True)

    has_banner = fields.BooleanField(default=False)
    has_avatar = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=True)

    owner: uuid.UUID = fields.UUIDField(null=False)

    tags: fields.ManyToManyRelation['Tags'] = fields.ManyToManyField(
        'ossia.Tags', related_name='creators'
    )
    tracks: fields.ReverseRelation[Tracks]

    created_at = fields.DatetimeField(auto_now_add=True)
    edited_at = fields.DatetimeField(auto_now=True)
