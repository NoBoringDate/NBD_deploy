from tortoise import models, fields


class Ref_Links(models.Model):
    id = fields.BigIntField(pk=True)
    ref_link = fields.TextField(null=True)
    sug_link = fields.TextField(null=True)
    ref_counter = fields.IntField(default=0)
    sug_counter = fields.IntField(default=0)
    sug_title = fields.TextField(null=True)
    
    class Meta:
        table = "ref_links"


class Ref_User(models.Model):
    id = fields.BigIntField(pk=True)
    ref_link = fields.TextField(null=True)
    user_id = fields.BigIntField(null=True)
    r_sug_id = fields.IntField(null=True)
    relink = fields.BooleanField(default=False)
    date_create = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "ref_users"


class Promo_Ref_Link(models.Model):
    id = fields.BigIntField(pk=True)
    tg_link = fields.TextField(null=True)
    counter = fields.IntField(default=1)
    
    class Meta:
        table = "promo_ref_link"


class User_Ref_Link(models.Model):
    id = fields.IntField(pk=True, null=False, unique=True)
    ref_link = fields.CharField(max_length=255, null=True)
    user_id = fields.BigIntField(null=False)
    counter = fields.IntField(default=0)
    date_create = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table="user_ref_links"


class Promoter(models.Model):
    id = fields.IntField(pk=True, null=False, unique=True)
    full_name = fields.CharField(max_length=255, null=True)
    distribution_chanell = fields.CharField(max_length=255, null=True)
    ref_link = fields.CharField(max_length=255, null=True)
    people_counter = fields.IntField(null=True, default=0)

    class Meta:
        table = "promoters"