import secrets
from DataBase import Suggestion, Ref_Links, Ready_Suggestion
import os

async def api_response(**data ):
    api_body = {}
    
    api_body["Value"]= data
    return api_body

async def scale(scale_dict):
    max_value = max(scale_dict.values())
    min_value = min(scale_dict.values())
    final_dict = dict()
    inter_dict = dict()
    if max_value != min_value:
        final_dict.update({k: 1 for k, v in scale_dict.items() if v == max_value and max_value != 0})
    elif max_value == min_value:
        final_dict.update({k: max_value for k, v in scale_dict.items()})
    else:
        final_dict.update(scale_dict)
    for el in scale_dict:
        if scale_dict[el] != max_value:
            inter_dict.update({el:scale_dict[el]})
    if len(inter_dict) != 0:
        max_value = max(inter_dict.values())
        min_value = min(inter_dict.values())
        if max_value == min_value and max_value != 0:
            final_dict.update({k: 0.5 for k, v in inter_dict.items()})
        else:
            final_dict.update({k: 0.5 for k, v in inter_dict.items() if v == max_value})
            final_dict.update({k: 0 for k, v in inter_dict.items() if v == min_value})
    return final_dict



""" async def scale(scale_dict: dict):
    final_dict = dict()
    for k, v in scale_dict.items():
        if v > 1:
            final_dict.update({k:1})
        elif v < -1:
            final_dict.update({k:-1})
        else:
            final_dict.update({k:v})
    return final_dict """

def my_exist(var_list, answer):
    for el in var_list:
        if el.answer == answer:
            return True
    return False

def age_valid(answer: dict, answer_to_answer: list):
    if "age" in list(answer.keys()):
        if answer["age"].isdigit():
            if 10<int(answer["age"])<100:
                return True
            else:
                return False
        else:
            False
    elif "gender" in list(answer.keys()):
        if answer["gender"] in answer_to_answer:
            return True
        else:
            return False
    else:
        return True


async def valid_url(url):
    if "http" not in url:
        return "http://"+url
    else:
        return url


async def edit_ref(sug:Suggestion, id:int, r_sug:int) -> str:
    link=os.environ.get("LINK_TEMPLATE_SUG")
    if sug.short_desc == None:
        sug.short_desc = sug.description[:200] + "..."
    if ((sug.contact.strip())[2:3]).isdigit():
        return sug
    if not await Ref_Links.exists(sug_title=sug.title):
        ref = await Ref_Links.create(
            ref_link = secrets.token_urlsafe(16),
            sug_link = await valid_url(sug.contact),
            sug_title = sug.title,
            ref_counter = 0,
            sug_counter = 0
        )
        sug.contact = link+ref.ref_link+f"&id={id}&session={r_sug}"
        return sug
    else:
        ref = await Ref_Links.get(sug_title=sug.title)
        sug.contact = link+ref.ref_link+f"&id={id}&session={r_sug}"
        return sug

