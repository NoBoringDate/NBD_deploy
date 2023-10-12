from NBDapp import app
from DataBase import *
from loguru import logger
from fastapi import Body, Response, Request
from fastapi.templating import Jinja2Templates
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
@app.get("/")
async def rel_redirect(request: Request, response: Response, ref: str = None, id: int = None, session: int = None):
    logger.info(f"{request.method} {request.url}")
    logger.info(f"Request Body: {request.query_params}")
    logger.info("Headers:")
    for name, value in request.headers.items():
        logger.info(f"\t{name}: {value}")
    if ref == None or id == None or session == None:
        return templates.TemplateResponse("index.html", context={"request": request})
    if await Ref_Links.exists(ref_link=ref):
        link = await Ref_Links.get(ref_link=ref)
        link_dict = dict(link)
        link_dict.update({"session":session})
        if not await Ref_User.exists(r_sug_id = session, ref_link = link.ref_link):
            await Ref_User.create(
                ref_link=link.ref_link,
                user_id=id,
                r_sug_id = session
            )
            link.ref_counter += 1
            await link.save()
        return templates.TemplateResponse("relink.html", context={"request": request, "link": link_dict})
    else:
        response.status_code = 404
        return response


@app.get('/ref/{ref}')
async def tg_ref(request: Request, ref: str):
    if await Promoter.exists(ref_link=ref) or await User_Ref_Link.exists(ref_link=ref):
        if not await Promo_Ref_Link.exists(tg_link = ref):
            await Promo_Ref_Link.create(
                tg_link = ref
            )
        else:
            promo = await Promo_Ref_Link.get(tg_link = ref)
            promo.counter += 1
            await promo.save()
    link = os.environ.get("PROMO_TG_LINK") + ref
    return templates.TemplateResponse("promo_relink.html", context={"request": request, "link": link})


@app.get("/success")
async def rel_redirect(request: Request, id: str, session: int, response: Response):
    link = await Ref_Links.get(id=id)
    user = await Ref_User.filter(r_sug_id = session, ref_link = link.ref_link).first()
    if not user.relink:
        link.sug_counter += 1
        user.relink = True
        await user.save()
        await link.save()
