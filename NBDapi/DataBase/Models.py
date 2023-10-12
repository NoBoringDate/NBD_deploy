from tortoise import models, fields
from tortoise.contrib.postgres.fields import ArrayField
from tortoise.contrib.pydantic import pydantic_model_creator
from typing import List


class Bot_Config(models.Model):
    id = fields.IntField(pk=True, unique=True)
    bot_token = fields.CharField(max_length=255, null=False)


class User_States(models.Model):
    id = fields.IntField(pk=True, unique=True)
    state = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "user_states"


class Contact(models.Model):
    id = fields.IntField(pk=True, null=False, unique=True)
    description = fields.CharField(max_length=255, null=True)
    link = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "contacts"

    def __str__(self) -> str:
        return self.full_name


class Promoter(models.Model):
    id = fields.IntField(pk=True, null=False, unique=True)
    full_name = fields.CharField(max_length=255, null=True)
    distribution_chanell = fields.CharField(max_length=255, null=True)
    ref_link = fields.CharField(max_length=255, null=True)
    people_counter = fields.IntField(null=True, default=0)

    class Meta:
        table = "promoters"


class User_Ref_Link(models.Model):
    id = fields.IntField(pk=True, null=False, unique=True)
    ref_link = fields.CharField(max_length=255, null=True)
    user_id = fields.BigIntField(null=False)
    counter = fields.IntField(default=0)
    date_create = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table="user_ref_links"


class User_Tg(models.Model):
    id = fields.BigIntField(pk=True, null=False, unique=True)
    username = fields.CharField(max_length=255, null=True)
    first_name = fields.CharField(max_length=255, null=True)
    last_name = fields.CharField(max_length=255, null=True)
    lang = fields.CharField(max_length=255, null=True)
    gender = fields.CharField(max_length=255, null=True)
    age = fields.CharField(max_length=255, null=True)
    advert = fields.CharField(max_length=255, null=True)
    date_create = fields.DatetimeField(auto_now_add=True)
    last_enter = fields.DatetimeField(null=True)
    curent_state = fields.ForeignKeyField(
        "models.User_States", related_name="users_state_curent", null=True)
    pref_state = fields.ForeignKeyField(
        "models.User_States", related_name="users_state_pref", null=True)
    ref_link = fields.ForeignKeyField(
        "models.Promoter", related_name="users", null=True)
    text_view = fields.BooleanField(default=False)
    user_ref_links = fields.ForeignKeyField(
        "models.User_Ref_Link", related_name="users", null=True)

    class Meta:
        table = "users_tg"

    @staticmethod
    async def get_states(tg_id):
        user = await User_Tg.get(id=tg_id)
        user_state_curent = await user.curent_state
        user_state_pref = await user.pref_state
        return {"curent_state": user_state_curent.state, "pref_state": user_state_pref.state}

class Meet_Question(models.Model):
    id = fields.IntField(pk=True, unique=True)
    order = fields.IntField(unique=True, null=True)
    tag = fields.CharField(max_length=255, null=True)
    question = fields.CharField(max_length=255, null=True)
    recomended_answer = ArrayField(element_type="text", null=True)
    validation = fields.CharField(max_length=255, null=True)
    answer_to_answer = ArrayField(element_type="text", null=True)

    class Meta:
        table = "meet_questions"
        ordering = ["order"]



class Meet_Session(models.Model):
    id = fields.IntField(pk=True, unique=True)
    tg_id = fields.BigIntField(null=True)
    curent_question = fields.IntField(null=True)
    close_question = ArrayField(element_type="int", null=True)
    date_create = fields.DatetimeField(auto_now_add=True)
    date_close = fields.DatetimeField(null=True)
    close = fields.BooleanField(default=False)

    class Meta:
        table = "meet_sessions"


class Variable(models.Model):
    id = fields.IntField(pk=True, unique=True)
    answer = fields.CharField(max_length=255, null=True)
    answer_to_answer = fields.CharField(max_length=255, null=True)
    intellect = fields.FloatField(null=True)
    phys = fields.FloatField(null=True)
    skill = fields.FloatField(null=True)
    question: fields.ManyToManyRelation["Main_Question"]

    class Meta:
        table = "variables"


class Main_Question(models.Model):
    id = fields.IntField(pk=True, unique=True)
    order = fields.IntField(unique=True, null=True)
    question = fields.CharField(max_length=255, null=True)
    variable: fields.ManyToManyRelation[Variable] = fields.ManyToManyField(
        "models.Variable", related_name="main_question")

    class Meta:
        table = "main_questions"


class Main_Session(models.Model):
    id = fields.IntField(pk=True, unique=True)
    tg_id = fields.BigIntField(null=True)
    curent_question = fields.IntField(null=True)
    close_question = ArrayField(element_type="int", null=True)
    curent_filter_question = fields.IntField(null=True)
    close_filter_question = ArrayField(element_type="int", null=True)
    curent_stat_question = fields.IntField(null=True)
    close_stat_question = ArrayField(element_type="int", null=True)
    date_create = fields.DatetimeField(auto_now_add=True)
    date_close = fields.DatetimeField(null=True)
    intellect = fields.FloatField(null=True, default=0)
    filter_param = fields.JSONField(null=True)
    stat_answer = fields.JSONField(null=True)
    phys = fields.FloatField(null=True, default=0)
    skill = fields.FloatField(null=True, default=0)
    answers = ArrayField(element_type="text", null=True)
    close = fields.BooleanField(default=False)
    tag = fields.TextField(null=True)

    class Meta:
        table = "main_sessions"


class Filter_Question(models.Model):
    id = fields.IntField(pk=True, unique=True)
    question = fields.CharField(max_length=255, null=True)
    answer = ArrayField(element_type="text", null=True)
    answer_to_answer = ArrayField(element_type="text", null=True)

    class Meta:
        table = "filter_questions"


class Statistic_Question(models.Model):
    id = fields.IntField(pk=True, unique=True)
    question = fields.CharField(max_length=255, null=True)
    answer = ArrayField(element_type="text", null=True)
    answer_to_answer = ArrayField(element_type="text", null=True)

    class Meta:
        table = "statistic_questions"


class Ready_Suggestion(models.Model):
    id = fields.IntField(pk=True, unique=True)
    tg_id = fields.BigIntField(null=True)
    session = fields.ForeignKeyField(
        "models.Main_Session", related_name="ready_suggestion")
    suggestions_1 = ArrayField(element_type="int", null=True)
    suggestions_2 = ArrayField(element_type="int", null=True)
    suggestions_3 = ArrayField(element_type="int", null=True)
    ready_suggestions = ArrayField(element_type="int", null=True)
    sended_suggestion = fields.IntField(null=True)
    view_suggestions = ArrayField(element_type="int", null=True)

    class Meta:
        table = "ready_suggestions"


class Bug_Report(models.Model):
    id = fields.IntField(pk=True, unique=True)
    tg_id = fields.BigIntField(null=False)
    bug_text = fields.CharField(null=False, max_length=255)
    date_create = fields.DatetimeField(auto_now_add=True)
    fixed = fields.BooleanField(default=False)

    class Meta:
        table = "bug_reports"


class Text(models.Model):
    id = fields.IntField(pk=True, null=False, unique=True)
    text = fields.CharField(max_length=2047, null=True)
    description = fields.TextField(null=True)
    func = fields.CharField(max_length=255, null=True)
    variable = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "texts"


class User(models.Model):
    id = fields.IntField(pk=True, null=False, unique=True)
    first_name = fields.CharField(max_length=255, null=True)
    last_name = fields.CharField(max_length=255, null=True)
    login = fields.CharField(max_length=255, null=True, unique=True)
    password = fields.CharField(max_length=255, null=True)
    password_token = fields.CharField(max_length=255, null=True)
    email = fields.CharField(max_length=255, null=True)
    role = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "users"


User_Pydantic = pydantic_model_creator(User, name='User')
UserIn_Pydantic = pydantic_model_creator(
    User, name='UserIn', exclude_readonly=True)


class Suggestion(models.Model):
    id = fields.IntField(pk=True, null=False, unique=True)
    title = fields.TextField(null=True)
    short_desc = fields.TextField(null=True)
    description = fields.TextField(null=True)
    price = fields.TextField(null=True)
    contact = fields.TextField(null=True)
    address = fields.TextField(null=True)
    intellect = fields.FloatField(null=True, default=0)
    phys = fields.FloatField(null=True, default=0)
    skill = fields.FloatField(null=True, default=0)
    tag = fields.TextField(null=True)
    filter_param = fields.JSONField(null=True)
    cover = fields.CharField(max_length=512, null=True)
    images = ArrayField(element_type="text", null=True)
    author = fields.ForeignKeyField("models.User", related_name="users", null=True)
    author_edit = fields.ForeignKeyField("models.User", related_name="users_edit", null=True)
    create_time = fields.DatetimeField(auto_now_add=True)
    last_modified_time = fields.DatetimeField(null=True)
    view_counter = fields.IntField(default=0, null=True)
    real_view_counter = fields.IntField(default=0, null=True)
    verif = fields.BooleanField(default=False)
    deleted = fields.BooleanField(default=False)
    deleted_time = fields.DatetimeField(null=True)
    similar_sug = fields.JSONField(null=True)
    advance_date_start = fields.DatetimeField(null=True)
    advance_date_end = fields.DatetimeField(null=True)
    advance = fields.BooleanField(default=False)
    active = fields.BooleanField(default=True)

    class Meta:
        table = "suggestions"


class Id_Images(models.Model):
    id = fields.IntField(pk=True, null=False)
    images = ArrayField(element_type="int", null=True)
    id_post = fields.CharField(max_length=50, null=True, unique=True)
    
    class Meta:
        table = "id_images"


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


class New_Variable(models.Model):
    id = fields.IntField(pk=True, unique=True)
    answer = fields.CharField(max_length=255, null=True)
    ques = fields.ManyToManyField(
        "models.Question", related_name="new_variable")
    question: fields.ManyToManyRelation["Question"]

    class Meta:
        table = "new_variable"

class Question(models.Model):
    id = fields.BigIntField(pk=True)
    question = fields.TextField(null=True)
    variable: fields.ManyToManyRelation[New_Variable] = fields.ManyToManyField(
        "models.New_Variable", related_name="question")
    
    class Meta:
        table = "question"


class Send_Message(models.Model):
    id = fields.BigIntField(pk=True)
    user = fields.TextField(null=True)
    text_message = fields.TextField(null=True)
    send_date = fields.DatetimeField(auto_now_add=True)
    status = fields.TextField(null=True)
    
    class Meta:
        table = "send_message"
   

class Global_Send(models.Model):
    id = fields.BigIntField(pk=True)
    send_name = fields.TextField(null=True)
    tg_id = fields.BigIntField(null=True)
    button_id = fields.TextField(null=True)
    
    class Meta:
        table="global_send"


class Showed_Phone_Number(models.Model):
    id = fields.IntField(pk=True)
    sug_id = fields.IntField(null=True)
    r_sug_id = fields.IntField(null=True)
    tg_id = fields.BigIntField(null=True)
    date_click = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table="showed_phone_number"


class Promo_Ref_Link(models.Model):
    id = fields.BigIntField(pk=True)
    tg_link = fields.TextField(null=True)
    counter = fields.IntField(default=1)
    
    class Meta:
        table = "promo_ref_link"


class Advert_Send(models.Model):
    id = fields.IntField(pk=True)
    r_sug_id = fields.IntField(null=True)
    tg_id = fields.BigIntField(null=True)
    group_id = fields.TextField(null=True)

    class Meta:
        table = "advert_send"


class Lottery_Participants(models.Model):
    id = fields.IntField(pk=True)
    tg_id = fields.BigIntField(null=True)
    date_create = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "lottery_participants"
