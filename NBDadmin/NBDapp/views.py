from datetime import date, datetime, timezone, timedelta
import time
import secrets
import uuid
from NBDapp import app
from DataBase import *
from fastapi import Request, Form, UploadFile, File, Cookie, Response, Body
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, FileResponse
from typing import List
from .utils import save_image, Stat, All_Statistic, new_system
from loguru import logger
from starlette.background import BackgroundTasks
from aiogram import Bot
from asyncio import sleep
import json
import os


def info_only(record):
    return record["level"].name == "INFO"


templates = Jinja2Templates(directory="templates")
logger.remove()
logger.add("logs/log_{time:DD-MM-YYYY}.log", rotation="00:00", retention="1 months", filter=info_only,
           format="{time:HH:mm:ss} | {level} | <level>{message}</level>")
logger.add("logs/log_error_{time:DD-MM-YYYY}.log", rotation="00:00", retention="1 months", level=30,
           format="{time:HH:mm:ss} | {level} | <level>{message}</level>")


@logger.catch(message="Error:")
async def authenticate_user(username: str, password: str):
    if await User.exists(login=username):
        user = await User.get(login=username)
        if not user:
            return False
        if user.password != password:
            return False
        return user
    return False


@app.middleware("http")
@logger.catch(message="Error:")
async def log_middle(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    logger.info(f"Params: {request.query_params}")
    logger.info("Headers:")
    for name, value in request.headers.items():
        logger.info(f"\t{name}: {value}")
    logger.info("Request:")
    for name in request:
        if name != "headers":
            logger.info(f"\t{name} : {request[name]}")

    response = await call_next(request)
    if request.url.path == '/questions/delete/filter/':
        response.background = delete_filter_sug
    logger.info(f"Response Body={response.status_code}")
    return response


async def delete_filter_sug():
    f_ques = await Suggestion.all()
    logger.info(f_ques)


@app.get('/login')
async def login(request: Request):
    return templates.TemplateResponse("login.html", context={"request": request, "page_title": "Логин"})


@app.post('/login', response_class=RedirectResponse)
async def login(request: Request) -> RedirectResponse:
    request_dict = await request.form()
    user = await authenticate_user(request_dict._dict['username'], request_dict._dict['password'])
    if not user:
        return RedirectResponse("/login", status_code=302)
    random_token = uuid.uuid4().hex
    user.password_token = random_token
    await user.save()
    response = RedirectResponse("/", status_code=302)
    response.set_cookie(key="token", value=random_token)
    response.set_cookie(key="username", value=user.login)
    templates.env.globals["role"] = user.role
    return response


@app.get('/')
async def homepage(request: Request, token: str = Cookie(None)):
    if await User.exists(password_token=token) and token != None:
        return templates.TemplateResponse("homepage.html", context={"request":request, "page_title": "Главная"})
    else:
        return RedirectResponse("/login", status_code=307)


@app.post('/allstatistic')
async def all_statistic(request:Request, response:Response, token: str = Cookie(None)):
    if await User.exists(password_token=token) and token != None:
        stat_form = await request.form()
        statistic = All_Statistic(startpoint=datetime.strptime(stat_form['datestart'], '%Y-%m-%dT%H:%M'), endpoint=datetime.strptime(stat_form['dateend'], '%Y-%m-%dT%H:%M'))
        path = await statistic.start()
        return FileResponse(path)
    else:
        return RedirectResponse("/login", status_code=307)


@app.post('/promostatistic')
async def promostatistic(request:Request, response:Response, token: str = Cookie(None)):
    if await User.exists(password_token=token) and token != None:
        stat_form = await request.form()
        ref_link = ""
        if "https://" in stat_form['reflink']:
            ref_link = (stat_form['reflink'])[36:]
        else:
            ref_link = stat_form['reflink']
        if await Promoter.exists(ref_link = ref_link):
            path = await Stat(link=ref_link, start=datetime.strptime(stat_form['datestart'], '%Y-%m-%dT%H:%M'), finish=datetime.strptime(stat_form['dateend'], '%Y-%m-%dT%H:%M')).stat()
            return FileResponse(path)
        else:
            response.status_code = 404
            return response
    else:
        return RedirectResponse("/login", status_code=307)



@app.get('/texts/')
async def get_texts(request: Request, token: str = Cookie(None)):
    if await User.exists(password_token=token) and token != None:
        texts = await Text.all()
        return templates.TemplateResponse("texts.html", context={"request":request, "texts":texts})
    else:
        return RedirectResponse("/login", status_code=307)


@app.get('/texts/{id}')
async def method_name(request: Request, id:int):
    text = await Text.get(id=id)
    return templates.TemplateResponse("text.html", context={"request":request, "text":text})


@app.post('/texts/add')
async def add_text(request: Request):
    req_form = await request.form()
    text = await Text.create(
        text = req_form['text'],
        description = req_form['description'],
        func = req_form['func'],
        variable = req_form['variable']
    )
    return dict(text)


@app.post('/texts/edit/')
async def edit_text(request: Request):
    req_form = await request.form()
    text = await Text.get(id=req_form['id'])
    text.text = req_form['text']
    text.description = req_form['description']
    await text.save()
    return dict(text)


@app.post('/texts/delete')
async def delete_text(request: Request, data = Body()):
    text = await Text.get(id=data['id'])
    await text.delete()


@app.get('/promoters/')
async def all_promoters(request: Request, token: str = Cookie(None)):
    if await User.exists(password_token=token) and token != None:
        proms = await Promoter.all().order_by("-id")
        link_template = os.environ.get("LINK_TEMPLATE")
        return templates.TemplateResponse("promoters.html", context={"request":request, "proms":proms, "link_template":link_template})
    else:
        return RedirectResponse("/login", status_code=307)


@app.get('/promoters/{id}')
async def promoter(request: Request, id:int, token: str = Cookie(None)):
    if await User.exists(password_token=token) and token != None:
        prom = await Promoter.get(id=id)  
        return templates.TemplateResponse("promoter.html", context={"request":request, "prom":prom})
    else:
        return RedirectResponse("/login", status_code=307)


@app.post('/promoters/add/')
async def add_promoters(request: Request):
    req_form = await request.form()
    ref_link = ""
    if (req_form['ref_link']).strip() == "":
        ref_link = secrets.token_urlsafe(10)
    else:
        ref_link = (req_form['ref_link']).strip()
    prom = await Promoter.create(
        full_name = req_form['full_name'],
        distribution_chanell = req_form['distribution_chanell'],
        ref_link = ref_link,
        people_counter = 0
    )
    return prom


@app.post('/promoters/edit/')
async def method_name(request: Request):
    req_form = await request.form()
    prom = await Promoter.get(id=req_form['id'])
    prom.full_name = req_form['full_name']
    prom.distribution_chanell = req_form['distribution_chanell']
    prom.ref_link = req_form['ref_link']
    prom.people_counter = req_form['people_counter']
    await prom.save()
    return dict(prom)


@app.post('/promoters/delete')
async def delete_prom(request: Request):
    req_form = await request.form()
    prom = await Promoter.get(id=req_form['id'])
    await prom.delete()


@app.post('/promoters/datestat')
async def date_stat(request:Request):
    stat_form = await request.form()
    stat = All_Statistic(startpoint=datetime.strptime(stat_form['datestart'], '%Y-%m-%dT%H:%M'), endpoint=datetime.strptime(stat_form['dateend'], '%Y-%m-%dT%H:%M'))
    path = await stat.promoters_date()
    return FileResponse(path)


@app.post('/promoters/stat')
async def promo_stat(request:Request):
    path = await All_Statistic().all_promoters()
    return FileResponse(path)


@app.get("/sendmessage")
async def sendmessage(request: Request, token: str = Cookie(None)):
    if await User.exists(password_token=token) and token != None:
        messages = await Send_Message.all()
        message_list = []
        for message in messages:
            message_list.append({"user": message.user, "text_message": message.text_message,
                                "send_date": message.send_date.strftime("%d.%m.%Y %H:%M"), "status":message.status})
        return templates.TemplateResponse("tg_send_message.html", context={"request": request, "messages": message_list, "user": await User.get(password_token=token)})
    else:
        return RedirectResponse("/login", status_code=307)


@app.post('/sendmessage')
async def tgsendmessage(request: Request, token: str = Cookie(None)):
    if await User.exists(password_token=token) and token != None:
        config = await Bot_Config.get(id=1)
        bot = Bot(token= config.bot_token)
        users = await User_Tg.all()
        message = await request.form()
        blocked_user = 0
        msg = await Send_Message.create(
            user = (await User.get(password_token=token)).login,
            text_message = message.get('message'),
            status="В процессе"
        )
        for user in users:
            try:
                await sleep(0.04)
                await bot.send_message(user.id, message.get('message'))
            except Exception as ex:
                blocked_user += 1
                logger.opt(exception=False).error(f"TG send message exception \"{ex}\", user_id:{user.id}")
        msg.status="Выполнено"
        await msg.save()
        return {"blocked_user":blocked_user, "all_users":len(users)}
    else:
        return RedirectResponse("/login", status_code=307)
    


@app.get('/suggestions')
async def suggestions(request: Request, token: str = Cookie(None)):
    if await User.exists(password_token=token) and token != None:
        tags = await new_system(ques1=await Question.all().first())
        tags.append("Скрыто")
        tags_counter= {}
        for tag in tags:
            counter = await Suggestion.filter(tag=tag).exclude(deleted=True, active=False).order_by("-id")
            tags_counter.update({tag:counter})
        sugs_count = await Suggestion.exclude(deleted=True).count()
        tags_counter.update({"Скрыто":await Suggestion.filter(active=False).exclude(deleted=True).order_by("-id")})
        return templates.TemplateResponse(name="suggestions.html",
                                          context={"request": request, "tags":tags, "sugs_count":sugs_count, "tags_counter":tags_counter, "page_title": "Предложения"})
    else:
        return RedirectResponse("/login", status_code=307)


@app.get("/addsuggestion")
async def addsuggestion(request: Request, token: str = Cookie(None)):
    if await User.exists(password_token=token) and token != None:
        tags = await new_system(ques1=await Question.all().first())
        filter_tags = await Filter_Question.all()
        return templates.TemplateResponse('addsug.html', context={'request': request, "tags": tags,"filter_tags":filter_tags, "page_title": "Новое Предложение"})
    else:
        return RedirectResponse("/login", status_code=307)

@app.post("/get_similar_sug")
async def get_similar_sug(request: Request, token: str = Cookie(None)):
    if await User.exists(password_token=token) and token != None:
        form_data = await request.form()
        similar = await Suggestion.filter(tag = form_data['tag'])
        return templates.TemplateResponse('checkbox_similar.html', context={'request': request,"similar":similar})
    else:
        return RedirectResponse("/login", status_code=307)

@app.post("/addsuggestion")
async def addsuggestion(
        request: Request,
        title: str = Form(),
        description: str = Form(),
        price: str = Form(),
        contact: str = Form(),
        address: str = Form(),
        tag: str = Form(),
        cover: UploadFile = File(),
        images: List[UploadFile] = File(),
        token: str = Cookie(None)
):
    if await User.exists(password_token=token) and token != None:
        user = await User.get(password_token=token)
        cover_path = save_image(cover)
        form_data = await request.form()
        images_path = []
        for image in images:
            image_path = save_image(image)
            images_path.append(image_path)

        short_desc = ""
        if form_data.get('short_desc') == None:
            short_desc = description[:100]
        else:
            short_desc = form_data.get('short_desc')
        
        similar_sug = []
        filter_param = []
        for fltr in form_data.keys():
            if "filter_tag" in fltr:
                filter_param.append(form_data[fltr])
            if "similar_sug" in fltr:
                similar_sug.append(int(form_data[fltr]))
        suggestion = await Suggestion.create(
            title=title,
            description=description,
            short_desc = short_desc,
            price=price,
            contact=contact,
            address=address,
            cover=cover_path,
            images=images_path,
            author=user,
            tag = tag,
            filter_param = filter_param,
            similar_sug = similar_sug
        )
        if form_data.get('premstart'):
            if form_data['dateend'] and form_data['datestart'] and form_data['dateend'] >= form_data['datestart']:
                if datetime.strptime(form_data['dateend'], '%Y-%m-%d') >= datetime.today():
                    suggestion.advance_date_start = datetime.strptime(form_data['datestart'], '%Y-%m-%d')
                    suggestion.advance_date_end = datetime.strptime(form_data['dateend'], '%Y-%m-%d')
                    suggestion.advance = form_data.get('premstart')
                    await suggestion.save()
        for sim in similar_sug:
            sug = await Suggestion.get(id=sim)
            if sug.similar_sug == None:
                sug.similar_sug = [suggestion.id]
            elif suggestion.id not in sug.similar_sug:
                sug.similar_sug.append(suggestion.id)
            await sug.save()
        return RedirectResponse(f"/suggestions/{str(suggestion.id)}", status_code=302)
    else:
        return RedirectResponse("/login", status_code=307)


@app.get("/suggestions/{id}")
async def view_suggestion(request: Request, id: int, token: str = Cookie(None)):
    if await User.exists(password_token=token) and token != None:
        sug = await Suggestion.filter(id=id).first()
        similar = []
        if sug.similar_sug != None:
            similar = [s.title for s in await Suggestion.filter(id__in=sug.similar_sug)]
        if sug.advance:
            sug.advance_date_start = sug.advance_date_start.replace(tzinfo=timezone(timedelta(hours=-3))).astimezone(timezone.utc).strftime("%d.%m.%Y")
            sug.advance_date_end = sug.advance_date_end.replace(tzinfo=timezone(timedelta(hours=-3))).astimezone(timezone.utc).strftime("%d.%m.%Y")
        return templates.TemplateResponse(name="viewsug.html",
                                          context={"request": request, "sug": sug, "similar": similar, "page_title": sug.title})
    else:
        return RedirectResponse("/login", status_code=307)


@app.get("/suggestions/edit/{id}")
async def edit_suggestion(request: Request, id: int, token: str = Cookie(None)):
    if await User.exists(password_token=token) and token != None:
        sugs = await Suggestion.get(id=id)
        if sugs.advance_date_start:
            sugs.advance_date_start = sugs.advance_date_start.replace(tzinfo=timezone(timedelta(hours=-3))).astimezone(timezone.utc).strftime("%Y-%m-%d")
            sugs.advance_date_end = sugs.advance_date_end.replace(tzinfo=timezone(timedelta(hours=-3))).astimezone(timezone.utc).strftime("%Y-%m-%d")
        tags = await new_system(ques1=await Question.all().first())
        filter_tags = await Filter_Question.all()
        similar = await Suggestion.filter(tag=sugs.tag)
        return templates.TemplateResponse('editsug.html',
                                          context={'request': request,
                                                   'sugs': sugs,
                                                   "tags": tags,
                                                   "filter_tags": filter_tags,
                                                   "similar": similar,
                                                   "page_title": sugs.title})
    else:
        return RedirectResponse("/login", status_code=307)


@app.post("/suggestions/edit/{id}")
async def edit_suggestion(
        request: Request,
        id: int,
        title: str = Form(),
        description: str = Form(),
        price: str = Form(),
        address: str = Form(),
        contact: str = Form(),
        cover: UploadFile = File(),
        images: List[UploadFile] = File(),
        tag: str = Form(),
        token: str = Cookie(None)
):
    if await User.exists(password_token=token) and token != None:
        sug = await Suggestion.get(id=id)
        history = await Edit_History.create(
            sug_id = sug,
            old_version = json.dumps(dict(sug), default=str)
        )
        form_data = await request.form()
        images_path = []
        del_images = []
        cover_path = save_image(cover)
        if cover_path != None:
            sug.cover = cover_path

        for el in form_data._list:
            if "/BotStorage" in el[0] or "botstorage" in el[0]:
                del_images.append(el[0])
        """ for el in del_images:
            os.remove(el) """
        images_path = (list(set(del_images) ^ set(sug.images)))
        for image in images:
            image_path = save_image(image)
            if image_path != None:
                images_path.append(image_path)

        if form_data.get('short_desc') == None or form_data.get('short_desc') == "" or form_data.get('short_desc') == "None":
            sug.short_desc = description[:200] + "..."
        else:
            sug.short_desc = form_data.get('short_desc')
        filter_param = []
        similar_sug = []
        for fltr in form_data.keys():
            if "filter_tag" in fltr:
                filter_param.append(form_data[fltr])
            if "similar_sug" in fltr:
                similar_sug.append(int(form_data[fltr]))
        for sim in similar_sug:
            suggestion = await Suggestion.get(id=sim)
            if sug.similar_sug == None:
                suggestion.similar_sug = [sug.id]
            elif suggestion.id not in sug.similar_sug:
                suggestion.similar_sug.append(sug.id)
            await suggestion.save()
        sug.filter_param = filter_param
        sug.similar_sug = similar_sug
        sug.title = title
        sug.price = price
        sug.description = description
        sug.contact = contact
        sug.address = address
        sug.images = images_path
        sug.author_edit = await User.get(password_token=token)
        sug.tag = tag
        sug.active = bool(form_data.get("active"))
        if form_data.get('premstart'):
            if form_data['dateend'] and form_data['datestart'] and form_data['dateend'] >= form_data['datestart']:
                if datetime.strptime(form_data['dateend'], '%Y-%m-%d') >= datetime.today():
                    sug.advance_date_start = datetime.strptime(form_data['datestart'], '%Y-%m-%d')
                    sug.advance_date_end = datetime.strptime(form_data['dateend'], '%Y-%m-%d')
                    sug.advance = form_data.get('premstart')
        if form_data.get('verif') == None:
            sug.verif = False
        else:
            sug.verif = True
        sug.last_modified_time = datetime.now()

        await sug.save()
        history.new_version = json.dumps(dict(sug), default=str)
        history.author_edit = await User.get(password_token=token)
        await history.save()
        return RedirectResponse(f"/suggestions/{sug.id}", status_code=302)
    else:
        return RedirectResponse("/login", status_code=307)


@app.get("/suggestions/delete/{id}")
async def delete_suggestion(id: int, token: str = Cookie(None)):
    if await User.exists(password_token=token) and token != None:
        sug = await Suggestion.get(id=id)
        sug.deleted = True
        sug.deleted_time = datetime.now()
        await sug.save()
        """ os.remove(sug.cover)
        for el in sug.images:
            os.remove(el) """

        return RedirectResponse("/suggestions", status_code=302)
    else:
        return RedirectResponse("/login", status_code=307)


@app.get('/questions')
async def question(request: Request, token: str = Cookie(None)):
    if await User.exists(password_token=token) and token != None:
        question = await Question.all()
        variable = await New_Variable.all()
        return templates.TemplateResponse("/questions/questions.html", context={'request': request, 'question':question, 'variable':variable})
    else:
        return RedirectResponse("/login", status_code=307)


""" BLOCK MAIN QUESTION """


@app.get("/questions/edit/main/{id}")
async def question(request: Request, id: int):
    ques = await Main_Question.get(id=id)
    var_ques = {ques.id: await ques.variable.all()}
    return templates.TemplateResponse("/questions/edit_main.html", context={'request': request, 'ques': ques, 'var_ques': var_ques})


@app.get("/questions/new/main/")
async def new_question(request: Request):
    return templates.TemplateResponse("/questions/new_main.html", context={'request': request})


@app.get("/questions/newanswer/main/{id}")
async def new_main_answer(request: Request, id: int):
    ques = await Main_Question.get(id=id)
    return templates.TemplateResponse("/questions/add_answer_main.html", context={'request': request, "ques": ques})


@app.get("/questions/newanswer/main/newques/{counter}")
async def new_main_answer(request: Request, counter: int):
    return templates.TemplateResponse("/questions/add_answer_main_in_new_ques.html", context={'request': request, "counter": counter})


@app.get("/questions/edit/answer/main/{id}")
async def edit_answer_main(request: Request, id: int):
    ans = await Variable.get(id=id)
    return templates.TemplateResponse("/questions/edit_main_ans.html", context={'request': request, 'ans': ans})


@app.post("/questions/delete/answer/main/")
async def delete_answer_main(request: Request, response: Response):
    q = await request.form()
    ans = await Variable.get(id=q._dict['id'])
    await ans.delete()
    response.status_code = 200
    return response


@app.post("/questions/delete/main/")
async def delete_main(request: Request, response: Response):
    q = await request.form()
    ques = await Main_Question.get(id=q._dict['id'])
    var = await ques.variable.all()
    for el in var:
        await el.delete()
    await ques.delete()
    response.status_code = 200
    return response


@app.post("/questions/addedit/main/{id}")
async def add_main_ques(request: Request, id: int, response: Response, question=Form()):
    ques = await Main_Question.get(id=id)
    ques.question = question
    var_ques = {ques.id: await ques.variable.all()}
    await ques.save()
    response.status_code = 200
    return templates.TemplateResponse("/questions/main_block.html", context={'request': request, 'main_ques': ques, 'var_ques': var_ques})


@app.post("/questions/addedit/main/answer/{id}")
async def add_main_ques(request: Request, id: int, response: Response):
    var = await Variable.get(id=id)
    var_form = await request.form()
    var.update_from_dict(var_form._dict)
    await var.save()
    ques = await var.main_question
    var_ques = {ques[0].id: await ques[0].variable.all()}
    response.status_code = 200
    return templates.TemplateResponse("/questions/main_block.html", context={'request': request, 'main_ques': ques[0], 'var_ques': var_ques})


@app.post("/questions/add/main/answer/{id}")
async def add_main_answer(request: Request, id: int, response: Response):
    var_form = await request.form()
    var = await Variable.create(
        answer=var_form._dict['answer'],
        answer_to_answer=var_form._dict['answer_to_answer'],
        intellect=var_form._dict['intellect'],
        phys=var_form._dict['phys'],
        skill=var_form._dict['skill']
    )
    ques = await Main_Question.get(id=id)
    await ques.variable.add(var)
    var_ques = {ques.id: await ques.variable.all()}
    response.status_code = 200
    return templates.TemplateResponse("/questions/main_block.html", context={'request': request, 'main_ques': ques, 'var_ques': var_ques})


@app.post('/questions/create/main/')
async def new_main_ques(request: Request, response: Response):
    ques_form = await request.form()
    ques = await Main_Question.create(
        question=ques_form._dict['question']
    )
    ans_keys = ques_form._dict.keys()
    counter = []
    for el in ans_keys:
        if "answer" in el and "answer_" not in el:
            counter.append(el[6:])
    for count in counter:
        var = await Variable.create(
            answer=ques_form._dict[f'answer{count}'],
            answer_to_answer=ques_form._dict[f'answer_to_answer{count}'],
            intellect=ques_form._dict[f'intellect{count}'],
            phys=ques_form._dict[f'phys{count}'],
            skill=ques_form._dict[f'skill{count}']
        )
        await ques.variable.add(var)
    var_ques = {ques.id: await ques.variable.all()}
    response.status_code = 200
    return templates.TemplateResponse("/questions/main_block.html", context={'request': request, 'main_ques': ques, 'var_ques': var_ques})

""" END BLOCK MAIN QUESTION """

""" BLOCK FILTER QUESTION """


@app.get("/questions/edit/filter/{id}")
async def f_question(request: Request, id: int):
    f_ques = await Filter_Question.get(id=id)
    return templates.TemplateResponse("/questions/edit_filter.html", context={'request': request, 'f_ques': f_ques})


@app.get("/questions/new/filter/")
async def new_f_question(request: Request):
    return templates.TemplateResponse("/questions/new_filter.html", context={'request': request})


@app.get("/questions/newanswer/fs/{counter}")
async def new_fs_answer(request: Request, counter: int):
    return templates.TemplateResponse("/questions/add_answer_f_s.html", context={'request': request, "counter": counter})


@app.get("/questions/newanswertoanswer/fs/{counter}")
async def new_fs_answer(request: Request, counter: int):
    return templates.TemplateResponse("/questions/add_answer_to_answer_f_s.html", context={'request': request, "counter": counter})


@app.get("/questions/edit/answer/filter/{id}")
async def edit_answer_filter(request: Request, id: int):
    ques = await Filter_Question.get(id=id)
    return templates.TemplateResponse("/questions/edit_f_ans.html", context={'request': request, 'ques': ques, "counter": len(ques.answer)})


@app.get("/questions/edit/answertoanswer/filter/{id}")
async def edit_answer_filter(request: Request, id: int):
    ques = await Filter_Question.get(id=id)
    return templates.TemplateResponse("/questions/edit_f_ans_to_ans.html", context={'request': request, 'ques': ques, "counter": len(ques.answer)})


@app.post("/questions/addedit/filter/{id}")
async def add_filter_ques(request: Request, id: int, response: Response, question=Form()):
    ques = await Filter_Question.get(id=id)
    ques.question = question
    await ques.save()
    return templates.TemplateResponse("/questions/filter_block.html", context={'request': request, 'f_ques': ques})


@app.post("/questions/addedit/filter/answer/{id}")
async def add_main_ques(request: Request, id: int, response: Response):
    ques = await Filter_Question.get(id=id)
    ques_form = await request.form()
    answers = []
    for k, v in ques_form._dict.items():
        if v.strip() == '':
            response.status_code = 400
            return response
        if "answer" in k:
            answers.append(ques_form._dict[k])
    ques.answer = answers
    await ques.save()
    return templates.TemplateResponse("/questions/filter_block.html", context={'request': request, 'f_ques': ques})


@app.post("/questions/addedit/filter/answertoanswer/{id}")
async def add_main_ques(request: Request, id: int,  response: Response):
    ques = await Filter_Question.get(id=id)
    ques_form = await request.form()
    answers = []
    for k, v in ques_form._dict.items():
        if v.strip() == '':
            response.status_code = 400
            return response
        if "answer" in k:
            answers.append(ques_form._dict[k])
    ques.answer_to_answer = answers
    await ques.save()
    return templates.TemplateResponse("/questions/filter_block.html", context={'request': request, 'f_ques': ques})


@app.post('/questions/create/filter/')
async def new_main_ques(request: Request, response: Response):
    ques_form = await request.form()
    answers = []
    answer_to_answers = []
    for k, v in ques_form._dict.items():
        if v.strip() == '':
            response.status_code = 400
            return response
        if "answer" in k and "answer_to_answer" not in k:
            answers.append(ques_form._dict[k])
        elif "question" not in k:
            answer_to_answers.append(ques_form._dict[k])
    ques = await Filter_Question.create(
        question=ques_form._dict['question'],
        answer=answers,
        answer_to_answer=answer_to_answers
    )
    return templates.TemplateResponse("/questions/filter_block.html", context={'request': request, 'f_ques': ques})


@app.post('/questions/delete/filter/')
async def delete_filter_ques(request: Request, response: Response):
    ques_form = await request.form()
    ques = await Filter_Question.get(id=ques_form._dict['id'])
    await ques.delete()
    background_tasks = BackgroundTasks()
    background_tasks.add_task(delete_filter_sug)
    response.status_code = 200
    return response

""" END BLOCK FILTER QUESTION """

""" BLOCK STATISTIC QUESTION """


@app.get("/questions/new/stat/")
async def new_s_question(request: Request):
    return templates.TemplateResponse("/questions/new_stat.html", context={'request': request})


@app.get("/questions/edit/stat/{id}")
async def s_question(request: Request, id: int):
    s_ques = await Statistic_Question.get(id=id)
    return templates.TemplateResponse("/questions/edit_stat.html", context={'request': request, 's_ques': s_ques})


@app.get("/questions/newanswer/stat/{counter}")
async def new_s_answer(request: Request, counter: int):
    return templates.TemplateResponse("/questions/add_answer_f_s.html", context={'request': request, "counter": counter})


@app.get("/questions/newanswertoanswer/stat/{counter}")
async def new_s_answer(request: Request, counter: int):
    return templates.TemplateResponse("/questions/add_answer_to_answer_f_s.html", context={'request': request, "counter": counter})


@app.get("/questions/edit/answer/stat/{id}")
async def edit_answer_filter(request: Request, id: int):
    s_ques = await Statistic_Question.get(id=id)
    return templates.TemplateResponse("/questions/edit_s_ans.html", context={'request': request, 's_ques': s_ques, "counter": len(s_ques.answer)})


@app.get("/questions/edit/answertoanswer/stat/{id}")
async def edit_answer_filter(request: Request, id: int):
    s_ques = await Statistic_Question.get(id=id)
    return templates.TemplateResponse("/questions/edit_s_ans_to_ans.html", context={'request': request, 'ques': s_ques, "counter": len(s_ques.answer)})


@app.post("/questions/addedit/stat/{id}")
async def add_main_ques(request: Request, id: int, response: Response, question=Form()):
    ques = await Statistic_Question.get(id=id)
    ques.question = question
    await ques.save()
    return templates.TemplateResponse("/questions/stat_block.html", context={'request': request, 's_ques': ques})


@app.post("/questions/addedit/stat/answer/{id}")
async def add_main_ques(request: Request, id: int, response: Response):
    ques = await Statistic_Question.get(id=id)
    ques_form = await request.form()
    answers = []
    for k, v in ques_form._dict.items():
        if v.strip() == '':
            response.status_code = 400
            return response
        if "answer" in k:
            answers.append(ques_form._dict[k])
    ques.answer = answers
    await ques.save()
    return templates.TemplateResponse("/questions/stat_block.html", context={'request': request, 's_ques': ques})


@app.post("/questions/addedit/stat/answertoanswer/{id}")
async def add_main_ques(request: Request, id: int, response: Response):
    ques = await Statistic_Question.get(id=id)
    ques_form = await request.form()
    answers = []
    for k, v in ques_form._dict.items():
        if v.strip() == '':
            response.status_code = 400
            return response
        if "answer" in k:
            answers.append(ques_form._dict[k])
    ques.answer_to_answer = answers
    await ques.save()
    return templates.TemplateResponse("/questions/stat_block.html", context={'request': request, 's_ques': ques})


@app.post('/questions/create/stat/')
async def new_main_ques(request: Request, response: Response):
    ques_form = await request.form()
    answers = []
    answer_to_answers = []
    for k, v in ques_form._dict.items():
        if v.strip() == '':
            response.status_code = 400
            return response
        if "answer" in k and "answer_to_answer" not in k:
            answers.append(ques_form._dict[k])
        elif "question" not in k:
            answer_to_answers.append(ques_form._dict[k])
    ques = await Statistic_Question.create(
        question=ques_form._dict['question'],
        answer=answers,
        answer_to_answer=answer_to_answers
    )
    return templates.TemplateResponse("/questions/stat_block.html", context={'request': request, 's_ques': ques})


@app.post('/questions/delete/stat/')
async def delete_filter_ques(request: Request, response: Response):
    ques_form = await request.form()
    ques = await Statistic_Question.get(id=ques_form._dict['id'])
    await ques.delete()
    response.status_code = 200
    return response

""" END BLOCK STATISTIC QUESTION """
