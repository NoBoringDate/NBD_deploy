import os
import random
from NBDapp import app
import secrets
from DataBase import *
from fastapi import Body, Response, Request
from .api_utils import api_response, scale, my_exist, age_valid, edit_ref
from datetime import datetime
from loguru import logger
from starlette.concurrency import iterate_in_threadpool
from starlette.types import Message
from starlette.background import BackgroundTask
import pytz


def info_only(record):
    return record["level"].name == "INFO"


logger.remove()
logger.add("logs/log_{time:DD-MM-YYYY}.log", rotation="00:00", retention="1 months", filter=info_only,
           format="{time:HH:mm:ss} | {level} | <level>{message}</level>")
logger.add("logs/log_error_{time:DD-MM-YYYY}.log", rotation="00:00", retention="1 months", level=30 , 
           format="{time:HH:mm:ss} | {level} | <level>{message}</level>")


def log_info(req_body, res_body, request):
    logger.info(f"{request.method} {request.url}")
    logger.info(f"Request Body: {req_body.decode()}{request.query_params}")
    logger.info("Headers:")
    for name, value in request.headers.items():
        logger.info(f"\t{name}: {value}")
    logger.info(f"Response Body: {res_body.decode()}")


async def set_body(request: Request, body: bytes):
    async def receive() -> Message:
        return {'type': 'http.request', 'body': body}
    request._receive = receive


@app.middleware("http")
@logger.catch(message="Error:")
async def log_middle(request: Request, call_next):
    req_body = await request.body()
    await set_body(request, req_body)
    response = await call_next(request)
    response_body = b''
    async for chunk in response.body_iterator:
        response_body += chunk
    task = BackgroundTask(log_info, req_body, response_body, request)
    return Response(background=task, content=response_body, status_code=response.status_code, headers=dict(response.headers), media_type=response.media_type, )


@app.get("/get_states")
async def get_states():
    states = await User_States.all()
    all_state = {el.state:el.state for el in states}
    return all_state
    
           
@app.get("/get_user_state")
async def get_user_state(id: int):
    return await User_Tg.get_states(tg_id=id)


@app.post("/set_user_state")
async def set_user_state(data = Body()):
    user = await User_Tg.get(id=data["id"])
    pref_state = await user.curent_state
    user.curent_state = await User_States.get(state=data["state"])
    user.pref_state = pref_state
    await user.save()


@app.get("/get_user_reflink")
async def get_user_reflink(tg_id: int):
    link = os.environ.get("LINK_TEMPLATE")
    ref=""
    if await User_Ref_Link.exists(user_id=tg_id):
        ref = (await User_Ref_Link.filter(user_id=tg_id).first()).ref_link
    else:
        ref = (await User_Ref_Link.create(
            ref_link = "fromuser"+secrets.token_urlsafe(10),
            user_id = tg_id
        )).ref_link
    return {"ref_link" : link+ref}


@app.get('/get_user_text_view')
async def get_user_text_view(tg_id: int):
    text_view = (await User_Tg.get(id=tg_id)).text_view
    return {"text_view":text_view}


@app.get("/exist_user")
async def user_exist(response: Response, tg_id: int):
    if await User_Tg.exists(id=tg_id):
        response.status_code = 200
        return response
    else:
        response.status_code = 404
        return response


@app.get("/get_contact")
async def get_contact():
    contact = await Contact.all()
    contacts = {}
    for el in contact:
        contacts.update({el.description:el.link})
    return contacts


@app.get("/get_text")
async def get_text(response: Response, func: str, variable: str, tg_id: int = None):
    if await Text.exists(func=func, variable=variable):
        response.status_code = 200
        if tg_id != None:
            user = await User_Tg.get(id=tg_id)
            if user.text_view and func == "get_sug_view" and variable == "1":
                return {"text":None}
            elif func == "get_sug_view" and variable == "2":
                user.text_view = True
                await user.save()
        text = await Text.filter(func=func, variable=variable).first()
        return {"text":text.text}
    else:
        response.status_code = 404
        return response


@app.get("/user_profile")
async def user_profile(response: Response, tg_id: int):
    user = await User_Tg.get(id=tg_id)
    return {"Имя":user.first_name, "Фамилия" : user.last_name, "username":user.username, "Пол":user.gender, "Возраст":user.age}


@app.get("/bug_report")
async def bug_report(
    tg_id: int, 
    bug_report: str
):
    await Bug_Report.create(
        tg_id = tg_id,
        bug_text = bug_report
    )
    return await api_response(result="Successful",arg={"ok": "ok"})


@app.get("/get_token")
async def get_token(response: Response):
    if await Bot_Config.exists(id=2):
        config = await Bot_Config.get(id=2)
        return {"token": os.environ.get("BOT_TOKEN")}
    else:
        response.status_code = 404
        return response

#{"id":"12123213","username":"asd","first_name":"asdads","last_name":"asdasd", "language_code":"ew"}
@app.post("/add_user_tg")#создание юзера 
async def user_create(response: Response, user = Body()):
    usermy = await User_Tg.create(
        id = user["id"],
        username = user["username"],
        first_name = user["first_name"],
        last_name = user["last_name"],
        lang = user["language_code"],
        curent_state = await User_States.get(state="after_start"),
        pref_state = await User_States.get(state="after_start")
    )
    if user.get("ref_link") != None: 
        if (ref_link := await Promoter.filter(ref_link=user["ref_link"]).first()) is not None:
            usermy.ref_link = ref_link
            ref_link.people_counter += 1
            await usermy.save()
            await ref_link.save()
        if "fromuser" in user.get("ref_link"):
            if (ref_link := await User_Ref_Link.filter(ref_link=user["ref_link"]).first()) is not None:
                usermy.user_ref_links = ref_link
                ref_link.counter +=1
                await usermy.save()
                await ref_link.save()
    response.status_code = 201
    return response


#{"id":"12123213", tag:answer}
@app.post("/meet_answer")
async def meet_answer(response: Response, data = Body()):
    if await User_Tg.exists(id=data["id"]):
        session = await Meet_Session.filter(tg_id=data["id"], close = False).first()
        curent_question = session.curent_question
        if age_valid(data, (await Meet_Question.get(id=curent_question)).recomended_answer):
            if session.close_question == None:
                session.close_question = [session.curent_question]
            else:
                session.close_question.append(session.curent_question) #не работает с пустой записью
            if await Meet_Question.all().count() == len(session.close_question):
                session.curent_question = 0
            else:
                session.curent_question = (await Meet_Question.all().offset(len(session.close_question)).first()).id
            await session.save()
            user = await User_Tg.get(id=data["id"])
            await user.update_from_dict(data)
            await user.save()
            response.status_code = 201
            return {"answer_to_answer":(await Meet_Question.get(id=curent_question)).answer_to_answer}
        else:
            question = await Meet_Question.get(id=curent_question)
            return {"error":"not valid", "question":{"question":question.question, "recom_answer": question.recomended_answer}}
    else:
        response.status_code = 404
        return response
    

@app.get("/get_meet_question")
async def get_meet_auestion(response: Response, tg_id: int):
    if await Meet_Session.exists(tg_id=tg_id, close = False):
        session = await Meet_Session.filter(tg_id=tg_id, close = False).first()
        if session.curent_question == 0:
            session.close = True
            session.date_close = datetime.now()
            await session.save()
            return {"session":"close"}
        question = await Meet_Question.get(id=session.curent_question)
        return {"question":question.question, "recom_answer": question.recomended_answer}
    else:
        question = await Meet_Question.all().first()
        await Meet_Session.create(
            tg_id = tg_id,
            curent_question = question.id,
        )
        return {"question":question.question, "recom_answer": question.recomended_answer}


@app.get("/get_tag")
async def get_tag(response: Response, tg_id: int):
    if await Meet_Session.exists(tg_id=tg_id, close = False):
        session = await Meet_Session.filter(tg_id=tg_id, close = False).first()
        question = await Meet_Question.get(id=session.curent_question)
        response.status_code = 200
        return {"tag":question.tag}
    else:
        response.status_code = 404
        return response


@app.get("/get_main_question")
async def get_main_question(response: Response, tg_id: int, new:bool):
    recom_answer = []
    if new:
        if (session := await Main_Session.filter(tg_id=tg_id, close=False).first())!= None:
            session.date_close = datetime.now()
            session.close = True
            await session.save()
        question = await Question.all().first()
        await Main_Session.create(
            tg_id = tg_id,
            curent_question = question.id,
        )
        for el in await question.variable.all():
            recom_answer.append(el.answer)
        return {"question":question.question, "recom_answer": recom_answer}
    if await Main_Session.exists(tg_id=tg_id, close = False):
        session = await Main_Session.filter(tg_id=tg_id, close = False).first()
        if session.curent_question == 0:
            await session.save()
            return {"main_question":"end"}
        question = await Question.get(id=session.curent_question)
        for el in await question.variable.all():
            recom_answer.append(el.answer)
        return {"question":question.question, "recom_answer": recom_answer}
    else:
        question = await Question.all().first()
        await Main_Session.create(
            tg_id = tg_id,
            curent_question = question.id,
        )
        for el in await question.variable.all():
            recom_answer.append(el.answer)
        return {"question":question.question, "recom_answer": recom_answer}

#{"id":"314786366", "answer":"весело"}
@app.post("/main_answer")
async def main_answer(response: Response, data = Body()):
    if await Main_Session.exists(tg_id=data["id"], close = False):
        session = await Main_Session.filter(tg_id=data["id"], close = False).first()
        
        answer_variable = await New_Variable.filter(answer=data['answer'])
        question = await Question.get(id=session.curent_question)
        if my_exist(await question.variable.all(), data['answer']):
            if session.close_question == None:
                session.close_question = [session.curent_question]
            else:
                session.close_question.append(session.curent_question) #не работает с пустой записью
            if session.answers == None:
                session.answers = [data["answer"]]
            else:
                session.answers.append(data["answer"])
            if len(await answer_variable[0].ques) != 0:
                session.curent_question = (await answer_variable[0].ques)[0].id
            else:
                session.curent_question = 0
                session.tag = data["answer"]
            await session.save()
            response.status_code = 201
            return {"ok":"ok"}
        else:
            recom_answer = []
            for el in await question.variable.all():
                recom_answer.append(el.answer)
            return {"error":"not valid", "question":{"question":question.question, "recom_answer": recom_answer}}     
    else:
        response.status_code = 404
        return response


@app.get("/get_filter_question")
async def get_filter_question(response: Response, tg_id: int):
    session = await Main_Session.filter(tg_id=tg_id, close = False).first()
    if session.curent_filter_question == 0:
        return {"filter_question":"end"}
    if session.curent_filter_question == None:
        question = await Filter_Question.all().first()
        session.curent_filter_question = question.id
        await session.save()
        return {"question": question.question, "recom_answer":question.answer}
    else:
        question = await Filter_Question.filter(id=session.curent_filter_question).first()
        return {"question": question.question, "recom_answer":question.answer}


@app.post("/filter_answer")
async def filter_answer(response: Response, data = Body()):
    if await Main_Session.exists(tg_id=data["id"], close = False):
        session = await Main_Session.filter(tg_id=data["id"], close = False).first()
        question = await Filter_Question.filter(id=session.curent_filter_question).first()
        if data['answer'] in question.answer:
            if session.filter_param == None:
                session.filter_param = {question.question : data["answer"]}
            else:
                session.filter_param.update({question.question : data["answer"]})
            if session.close_filter_question == None:
                session.close_filter_question = [session.curent_filter_question]
            else:
                session.close_filter_question.append(session.curent_filter_question)
            if await Filter_Question.all().count() == len(session.close_filter_question):
                session.curent_filter_question = 0
            else:
                session.curent_filter_question = (await Filter_Question.all().offset(len(session.close_filter_question)).first()).id
            await session.save()
            return {"answer_to_answer": question.answer_to_answer}
        else:
            return {"error":"not valid", "question":{"question": question.question, "recom_answer": question.answer}} 
    else:
        response.status_code = 404
        return response


@app.get("/get_stat_question")
async def get_stat_question(response: Response, tg_id: int):
    session = await Main_Session.filter(tg_id=tg_id, close = False).first()
    if session.curent_stat_question == 0:
            session = await Main_Session.filter(tg_id=tg_id, close = False).first()
            session.close = True
            session.date_close = datetime.now()
            await session.save()
            return{"session":"end"}
    if session.curent_stat_question == None:
        question = await Statistic_Question.all().first()
        if question == None:
            session = await Main_Session.filter(tg_id=tg_id, close = False).first()
            session.close = True
            session.date_close = datetime.now()
            await session.save()
            return{"session":"end"}
        session.curent_stat_question = question.id
        await session.save()
        return {"question": question.question, "recom_answer":question.answer}
    else:
        question = await Statistic_Question.filter(id=session.curent_stat_question).first()
        return {"question": question.question, "recom_answer":question.answer}


@app.post("/stat_answer")
async def stat_answer(response: Response, data = Body()):
    if await Main_Session.exists(tg_id=data["id"], close = False):
        session = await Main_Session.filter(tg_id=data["id"], close = False).first()
        question = await Statistic_Question.filter(id=session.curent_stat_question).first()
        if data['answer'] in question.answer:
            if session.stat_answer == None:
                session.stat_answer = {question.question : data["answer"]}
            else:
                session.stat_answer.update({question.question : data["answer"]})
            if session.close_stat_question == None:
                session.close_stat_question = [session.curent_stat_question]
            else:
                session.close_stat_question.append(session.curent_stat_question)
            if await Statistic_Question.all().count() == len(session.close_stat_question):
                session.curent_stat_question = 0
            else:
                session.curent_stat_question = (await Statistic_Question.all().offset(len(session.close_stat_question)).first()).id
            await session.save()
            return {"answer_to_answer": question.answer_to_answer}
        else:
            return {"error":"not valid", "question":{"question": question.question, "recom_answer": question.answer}}
    else:
        response.status_code = 404
        return response


@app.get('/get_suggestion')
async def get_suugestion(tg_id: int):
    session = await Main_Session.filter(tg_id=tg_id).order_by("-date_close").first()
    r_sug = await Ready_Suggestion.filter(session=session).first()
    sug = await Suggestion.filter(id = r_sug.sended_suggestion).first()
    return {"sug":await edit_ref(sug, tg_id, r_sug.id), "len":len(r_sug.ready_suggestions), "index" : r_sug.ready_suggestions.index(sug.id)+1}


@app.get('/gen_suggestion')
async def gen_suggestion(tg_id: int):
    session = await Main_Session.filter(tg_id=tg_id).order_by("-date_close").first()
    r_sug = await Ready_Suggestion.create(
        tg_id = tg_id,
        session = session
    )
    advance_sug = []
    not_advance_sug = []
    exclude_sug = []
    for rs in await Suggestion.filter(tag=session.tag, deleted=False, active=True, filter_param__contains=list(session.filter_param.values())):
        today = datetime.now(tz=pytz.UTC)
        if rs.advance_date_start != None:
            if rs.advance and rs.advance_date_start <= today <= rs.advance_date_end:
                advance_sug.append(rs)
                exclude_sug.append(rs.id)
            elif rs.advance_date_end <=today:
                rs.advance_date_start = None
                rs.advance_date_end = None
                rs.advance = False
                await rs.save()
        if rs.id not in exclude_sug:
            not_advance_sug.append(rs)
        for ex in rs.similar_sug:
            exclude_sug.append(ex)
    ready_sug = random.sample(advance_sug, len(advance_sug))
    for non_adv in random.sample(not_advance_sug, len(not_advance_sug)):
        ready_sug.append(non_adv)
    for sg in ready_sug:
        if r_sug.ready_suggestions == None:
            r_sug.ready_suggestions = [sg.id]
        else:
            r_sug.ready_suggestions.append(sg.id)
    if r_sug.ready_suggestions != None:
        first_sug = await Suggestion.get(id=r_sug.ready_suggestions[0])
        r_sug.sended_suggestion = first_sug.id
        first_sug.real_view_counter += 1
        await first_sug.save()
        for count in r_sug.ready_suggestions:
            check_sug = await Suggestion.get(id=count)
            check_sug.view_counter += 1
            await check_sug.save()
        r_sug.view_suggestions = [r_sug.sended_suggestion]
        await r_sug.save()
        return {"sug":await edit_ref(first_sug, tg_id,r_sug.id), "len":len(r_sug.ready_suggestions), "index" : r_sug.ready_suggestions.index(first_sug.id)+1}
    else:
        await r_sug.save()
        return {"sug":"Not Found"}


@app.get('/next_suggestion')
async def next_sug(tg_id: int):
    session = await Main_Session.filter(tg_id=tg_id).order_by("-date_close").first()
    r_sug = await Ready_Suggestion.filter(session=session).first()
    if r_sug.ready_suggestions.index(r_sug.sended_suggestion)+1 < len(r_sug.ready_suggestions):
        sug = await Suggestion.filter(id=r_sug.ready_suggestions[r_sug.ready_suggestions.index(r_sug.sended_suggestion)+1]).first()
        r_sug.sended_suggestion = sug.id
        if r_sug.sended_suggestion not in r_sug.view_suggestions:
            r_sug.view_suggestions.append(r_sug.sended_suggestion)
            sug.real_view_counter += 1
            await sug.save()
        await r_sug.save()
        return {"sug":await edit_ref(sug, tg_id,r_sug.id), "len":len(r_sug.ready_suggestions), "index" : r_sug.ready_suggestions.index(sug.id)+1}
    elif r_sug.ready_suggestions.index(r_sug.sended_suggestion)+1 >= len(r_sug.ready_suggestions):
        sug = await Suggestion.filter(id=r_sug.ready_suggestions[0]).first()
        r_sug.sended_suggestion = sug.id
        if r_sug.sended_suggestion not in r_sug.view_suggestions:
            r_sug.view_suggestions.append(r_sug.sended_suggestion)
            sug.real_view_counter += 1
            await sug.save()
        await r_sug.save()
        return {"sug":await edit_ref(sug, tg_id,r_sug.id), "len":len(r_sug.ready_suggestions), "index" : r_sug.ready_suggestions.index(sug.id)+1}


@app.get('/pref_suggestion')
async def pref_sug(tg_id: int):
    session = await Main_Session.filter(tg_id=tg_id).order_by("-date_close").first()
    r_sug = await Ready_Suggestion.filter(session=session).first()
    if r_sug.ready_suggestions.index(r_sug.sended_suggestion)-1 >= 0:
        sug = await Suggestion.filter(id=r_sug.ready_suggestions[r_sug.ready_suggestions.index(r_sug.sended_suggestion)-1]).first()
        r_sug.sended_suggestion = sug.id
        if r_sug.sended_suggestion not in r_sug.view_suggestions:
            r_sug.view_suggestions.append(r_sug.sended_suggestion)
            sug.real_view_counter += 1
            await sug.save()
        await r_sug.save()
        return {"sug":await edit_ref(sug, tg_id,r_sug.id), "len":len(r_sug.ready_suggestions), "index" : r_sug.ready_suggestions.index(sug.id)+1}
    elif r_sug.ready_suggestions.index(r_sug.sended_suggestion)-1 < 0:
        sug = await Suggestion.filter(id=r_sug.ready_suggestions[len(r_sug.ready_suggestions)-1]).first()
        r_sug.sended_suggestion = sug.id
        if r_sug.sended_suggestion not in r_sug.view_suggestions:
            r_sug.view_suggestions.append(r_sug.sended_suggestion)
            sug.real_view_counter += 1
            await sug.save()
        await r_sug.save()
        return {"sug":await edit_ref(sug, tg_id,r_sug.id), "len":len(r_sug.ready_suggestions), "index" : r_sug.ready_suggestions.index(sug.id)+1}


@app.get("/get_random_sug")
async def get_random_sug(tg_id: int):
    sugs = await Suggestion.filter(deleted=False).order_by("real_view_counter")
    session = await Main_Session.filter(tg_id=tg_id).order_by("-date_close").first()
    r_sug = await Ready_Suggestion.filter(session=session).first()
    ready_sug = []
    filter_param = {k:v for k, v in session.filter_param.items() if v != "Без разницы , самое главное классно провести время!" and v != "Покажите оба варианта :)"}
    for sug_f in sugs:
        if filter_param.items() <= sug_f.filter_param.items():
            ready_sug.append(sug_f)
    if len(ready_sug) >= 5:        
        ready_sugs=random.sample(ready_sug, 5) 
    else:
        ready_sugs=random.sample(ready_sug, len(ready_sug)) 
    for sug in ready_sugs:
        if r_sug.ready_suggestions == None:
            r_sug.ready_suggestions = [sug.id]
        else:
            r_sug.ready_suggestions.append(sug.id)
    first_sug = await Suggestion.get(id=r_sug.ready_suggestions[0])
    r_sug.sended_suggestion = first_sug.id
    for count in r_sug.ready_suggestions:
        check_sug = await Suggestion.get(id=count)
        check_sug.view_counter += 1
        await check_sug.save()
    r_sug.view_suggestions = [r_sug.sended_suggestion]
    await r_sug.save()
    return {"sug":await edit_ref(first_sug, tg_id), "len":len(r_sug.ready_suggestions), "index" : r_sug.ready_suggestions.index(first_sug.id)+1}
        


@app.get("/get_test_sug")
async def get_test():
    sug = await Suggestion.all().first()
    return sug


@app.post("/get_photo_name")
async def get_name_images(response: Response, data = Body()):
    name_hex = await Id_Images.create(
        images = data['photo_id'],
        id_post = secrets.token_hex(24)
    )
    return {"name":name_hex.id_post}


@app.get("/get_photo_id")
async def get_photo_id(name:str):
    images = await Id_Images.get(id_post=name)
    images_list = images.images
    await images.delete()
    return {"id":images_list}


@app.get('/global_statistic')
async def global_statistic(response: Response, send_message:str, tg_id:int, button_id:str):
    await Global_Send.create(
        send_name = send_message,
        tg_id=tg_id,
        button_id=button_id
    )
    response.status_code = 201
    return response


@app.post('/showed_phone_number')
async def showed_phone_number(request:Request, response:Response, data = Body()):
    r_sug = await Ready_Suggestion.filter(tg_id=data["tg_id"]).order_by("-id").first()
    if not await Showed_Phone_Number.exists(sug_id=r_sug.sended_suggestion, r_sug_id = r_sug.id):
        await Showed_Phone_Number.create(
            sug_id = r_sug.sended_suggestion,
            r_sug_id = r_sug.id,
            tg_id = data["tg_id"]
        )
    response.status_code = 201
    return response


@app.get("/start_advert_sug")
async def start_advert_sug(response: Response, tg_id: int, key_button: str):
    advert_dict = {'1':[34,122,15,46,23,45,100,26]}
    if (session := await Main_Session.filter(tg_id=tg_id, close = False).first()) != None:
            session.close = True
            session.date_close = datetime.now()
            await session.save()
    session = await Main_Session.create(
        tg_id = tg_id,
        close = True,
        date_close = datetime.now()
    )
    r_sug = await Ready_Suggestion.create(
        tg_id = tg_id,
        session = session,
        ready_suggestions = random.sample(advert_dict.get('1'), len(advert_dict.get('1')))
    )
    first_sug = await Suggestion.get(id=r_sug.ready_suggestions[0])
    r_sug.sended_suggestion = first_sug.id
    first_sug.real_view_counter += 1
    await first_sug.save()
    for count in r_sug.ready_suggestions:
        check_sug = await Suggestion.get(id=count)
        check_sug.view_counter += 1
        await check_sug.save()
    r_sug.view_suggestions = [r_sug.sended_suggestion]
    await r_sug.save()
    await Advert_Send.create(
        tg_id = tg_id,
        r_sug_id = r_sug.id,
        group_id = key_button
    )
    return {"sug":await edit_ref(first_sug, tg_id,r_sug.id), "len":len(r_sug.ready_suggestions), "index" : r_sug.ready_suggestions.index(first_sug.id)+1}


@app.get('/lottery')
async def lottery(tg_id: int):
    if await Lottery_Participants.exists(tg_id=tg_id):
        return{"ref_link":None}
    else:
        await Lottery_Participants.create(tg_id=tg_id)
        link = await get_user_reflink(tg_id)
        return link
