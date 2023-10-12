from pathlib import Path
import os
import secrets
from PIL import Image, ExifTags
import boto3
from botocore.client import Config
from DataBase import *
from typing import List
import xlsxwriter
import datetime
import pytz


BUCKET = {'Name': 'cr28942-botstorage'}

# генератов случайного названия файла и замена оригинального
def random_name(file) -> str:
    random_hex = secrets.token_hex(16)
    _, f_ext = os.path.splitext(file.filename)
    return (random_hex + f_ext)


def compress_img(image_name) -> str:
    img = Image.open(image_name)
    exif = img._getexif()
    img.thumbnail(size = (1920, 1080))
    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation] == 'Orientation':
            break
    if exif != None and orientation in exif.keys():
        if exif[orientation] == 3:
            img = img.rotate(180, expand=True)
        elif exif[orientation] == 6:
            img = img.rotate(270, expand=True)
        elif exif[orientation] == 8:
            img = img.rotate(90, expand=True)
    filename, ext = os.path.splitext(image_name)
    img.save(f"{filename}{ext}")
    return (filename + ext)


def s3_uploader(picture_path) -> str:
    s3 = boto3.client(
        's3',
        endpoint_url='https://s3.timeweb.com',
        region_name='ru-1',
        aws_access_key_id='cr28942',
        aws_secret_access_key='7fddfc015d172e3cde01e5aa92250e2d',
        config=Config(s3={'addressing_style': 'path'})
    )
    picture_name = picture_path[14:]
    s3.upload_file(Filename=picture_path, Bucket=BUCKET['Name'], Key=picture_name)
    url = "https://s3.timeweb.com/cr28942-botstorage/" + picture_name
    os.remove(picture_path)
    return (url)



# функция сохранения обложки
def save_image(image) -> str:
    if image.filename != "":
        picture_name = random_name(image)
        picture_path = Path("../BotStorage", picture_name)
        with open(picture_path, 'wb') as f:
            f.write(image.file.read())
        picture_path = s3_uploader(compress_img(image_name=picture_path))
        return str(picture_path)
    else:
        return None


async def new_system(ques1) -> List[str]:
    final_list = []
    for var1 in await ques1.variable:
        for ques2 in await var1.ques:
            for var2 in await ques2.variable:
                if len(await var2.ques) == 0:
                    if var2.answer not in final_list:
                        final_list.append(var2.answer)
                for ques3 in await var2.ques:
                    for var3 in await ques3.variable:
                        if len(await var3.ques) == 0:
                            if var3.answer not in final_list:
                                final_list.append(var3.answer)
    return final_list                  

class Stat():
    def __init__(self, link:str, start:datetime.datetime, finish:datetime.datetime) -> None:
        self.link:str = link
        self.start:datetime.datetime = start.replace(tzinfo=pytz.UTC)
        self.finish:datetime.datetime = finish.replace(tzinfo=pytz.UTC)
        self.staff_id = [704274508,158628518,76867900,314786366,437535160,461281008,885512832,974717720]

    
    async def counter2(self, main:List[Main_Session], session_number:int, statistic_dict:dict)->dict:
        for el in main:
            if el.date_create >= self.start and el.date_create <= self.finish:
                if statistic_dict.get(session_number) == None:
                    statistic_dict.update({session_number : {'Поменять ответы':0, 'Вопрос 1':0, 'Вопрос 2' : 0, 'Вопрос 3' : 0, 'Вопрос 4' : 0, "sessions" : []}})
                
                if el.close_question != None:
                    if len(el.close_question) == 2:
                        statistic_dict[session_number]['Вопрос 1'] += 1
                        statistic_dict[session_number]['Вопрос 2'] += 1
                        statistic_dict[session_number]['Поменять ответы'] += 1
                        
                    if len(el.close_question) == 1:
                        statistic_dict[session_number]['Вопрос 1'] += 1
                        statistic_dict[session_number]['Поменять ответы'] += 1
                        
                    if len(el.close_question) == 3:
                        statistic_dict[session_number]['Вопрос 1'] += 1
                        statistic_dict[session_number]['Вопрос 2'] += 1
                        statistic_dict[session_number]['Вопрос 3'] += 1
                        statistic_dict[session_number]['Поменять ответы'] += 1
                
                if el.curent_question == 1:
                    statistic_dict[session_number]['Поменять ответы'] += 1
                    
                
                    
                if el.curent_filter_question == 0:
                    statistic_dict[session_number]['Вопрос 4'] += 1

                if el.close == True:
                    statistic_dict[session_number]['sessions'].append(el.id)
                session_number += 1
        return statistic_dict


    async def counter(self, users:List[User_Tg], statistic_dict:dict)->dict:
        session_number = 1
        statistic_dict.update({session_number : {'Поменять ответы':0, 'Вопрос 1':0, 'Вопрос 2' : 0, 'Вопрос 3' : 0, 'Вопрос 4' : 0, "sessions" : []}})
        for user in users:
            main = await Main_Session.filter(tg_id = user.id).order_by("date_create")
            session_number=1
            statistic_dict.update(await Stat.counter2(self, main, session_number , statistic_dict))
        return statistic_dict


    async def users_len(self, users:List[User_Tg])->int:
        counter = 0
        for user in users:
            if user.date_create >= self.start and user.date_create <= self.finish:
                counter +=1
        return counter


    async def stat(self):
        workbook = xlsxwriter.Workbook('stat/promo_statistic.xlsx')
        worksheet = workbook.add_worksheet("Первый опрос")
        worksheet2 = workbook.add_worksheet(self.link)
        percent = workbook.add_format()
        percent.set_num_format(10)
        worksheet.write(0, 0, f"{self.start}-{self.finish}")
        worksheet.write(1, 0, "Ссылка")
        worksheet.write(2, 0, self.link)
        ref = await Promoter.get(ref_link = self.link)
        clicks = await Promo_Ref_Link.filter(tg_link=self.link).first()
        worksheet.write(1, 1, "Клики")
        worksheet.write(2, 1, clicks.counter if clicks != None else 0)
        users = await User_Tg.filter(ref_link_id = ref.id).exclude(id__in = self.staff_id)
        worksheet.write(1, 2, "/start")
        worksheet.write(2, 2, await Stat.users_len(self, users=users))
        users = await User_Tg.filter(ref_link_id = ref.id).exclude(id__in = self.staff_id, curent_state_id = 1)
        worksheet.write(1, 3, "Погнали")
        worksheet.write(2, 3, await Stat.users_len(self, users=users))
        worksheet.write(3, 3, "=C3/B3", percent)
        users = await User_Tg.filter(ref_link_id = ref.id).exclude(id__in = self.staff_id, gender = None)
        worksheet.write(1, 4, "Пол")
        worksheet.write(2, 4, await Stat.users_len(self, users=users))
        worksheet.write(3, 4, "=D3/C3", percent)
        users = await User_Tg.filter(ref_link_id = ref.id).exclude(id__in = self.staff_id, age = None)
        worksheet.write(1, 5, "Возраст")
        worksheet.write(2, 5, await Stat.users_len(self, users=users))
        worksheet.write(3, 5, "=E3/D3", percent)
        users = await User_Tg.filter(ref_link_id = ref.id).exclude(id__in = self.staff_id, advert = None)
        worksheet.write(1, 6, "Источник")
        worksheet.write(2, 6, await Stat.users_len(self, users=users))
        worksheet.write(3, 6, "=F3/E3", percent)
        users = await User_Tg.filter(ref_link_id = ref.id).exclude(id__in = self.staff_id, curent_state_id__in = [1, 2, 3])
        interes_btn = await Stat.users_len(self, users=users)
        worksheet.write(1, 7, "Интересно")
        worksheet.write(2, 7, interes_btn)
        worksheet.write(3, 7, "=G3/F3", percent)
        statistic_dict = {}
        statistic_dict = await Stat.counter(self, users, statistic_dict)
        worksheet2.write(0, 0, f"{self.start}-{self.finish}")
        worksheet2.write(0, 1, "Сессия")
        worksheet2.write(0, 2, "Ссылка")
        for k, v in statistic_dict.items():

            if k == 1:
                i = 8
                pref_cell = interes_btn
                r_sugs = await Ready_Suggestion.filter(session_id__in = statistic_dict[k]['sessions'])
                for key in v:
                    if key != 'sessions' and key != 'Поменять ответы':
                        worksheet.write(1, i, key)
                        worksheet.write(2, i, v[key])
                        worksheet.write(3, i, v[key]/pref_cell, percent)
                        pref_cell = v[key]
                        i+=1
                    elif key != 'Поменять ответы':
                        worksheet.write(1, i, "Финал")
                        worksheet.write(2, i, len(r_sugs))
                        worksheet.write(3, i, len(r_sugs)/pref_cell, percent)
            else:
                r_sugs = await Ready_Suggestion.filter(session_id__in = statistic_dict[k]['sessions'])
                i = 3
                for key in v:
                    if key != 'sessions':
                        worksheet2.write(k-1, 1, k)
                        worksheet2.write(k-1, 2, self.link)
                        worksheet2.write(0, i, key)
                        worksheet2.write(k-1, i, v[key])
                        i+=1
                    else:
                        worksheet2.write(0, i, "Финал")
                        worksheet2.write(k-1, i, len(r_sugs))
        workbook.close()
        return 'stat/promo_statistic.xlsx'


class All_Statistic:
    
    def __init__(self, startpoint=None, endpoint=None) -> None:
        self.startpoint = startpoint
        self.endpoint = endpoint
        self.staff_id = [704274508,158628518,76867900,314786366,437535160,461281008,885512832,974717720]

    async def statistic_sug(self):
        worksheet = self.workbook.add_worksheet("Статистика предложений")
        worksheet.set_column(0, 5, 25)
        worksheet.write(0, 0, "Предложения")
        worksheet.write(0, 1, "Кол-во выдач")
        worksheet.write(0, 2, "Кол-во просмотров")
        worksheet.write(0, 3, "Кол-во нажатий на \"Связатся\"")
        worksheet.write(0, 4, "Тип связи")
        worksheet.write(0, 5, "Общее кол-во пользователей")
        users = await User_Tg.exclude(id__in = self.staff_id).count()
        worksheet.write(1, 5, users)
        sugs = await Suggestion.exclude(deleted=True).order_by("id")
        i=1
        for sug in sugs:
            ref_link = await Ref_Links.filter(sug_title=sug.title).first()
            ref_phone = await Showed_Phone_Number.filter(sug_id=sug.id).exclude(tg_id__in=self.staff_id).count()
            worksheet.write(i, 0, sug.title)
            worksheet.write(i, 1, sug.view_counter)
            worksheet.write(i, 2, sug.real_view_counter)
            if ref_link != None:
                worksheet.write(i, 3, ref_link.ref_counter)
                worksheet.write(i, 4, "ссылка")
            else:
                worksheet.write(i, 3, ref_phone)
                worksheet.write(i, 4, "телефон")
            i+=1


    async def statistic_sug_date(self):
        worksheet = self.workbook.add_worksheet("Предложения(за период)")
        worksheet.set_column(0, 4, 25)
        worksheet.write(1, 0, "Предложения")
        worksheet.write(1, 1, "Кол-во выдач")
        worksheet.write(1, 2, "Кол-во просмотров")
        worksheet.write(1, 3, "Кол-во нажатий на \"Связатся\"")
        worksheet.write(1, 4, "Тип связи")
        merge_format = self.workbook.add_format({
            'bold':     True,
            'align':    'center',
            'num_format': 'dd/mm/yy'
        })
        worksheet.merge_range(0,0,0,3,f"{str(self.startpoint.date())} - {str(self.endpoint.date())}", merge_format)
        sugs = await Suggestion.filter(deleted=False).order_by("id")
        sugs_counters = {sug.id:{"title":sug.title,"view":0, "real":0, "phone":0} for sug in sugs}
        sessions = await Main_Session.filter(date_close__range = [self.startpoint, self.endpoint])
        for session in sessions:
            r_sug = await Ready_Suggestion.filter(session_id = session.id).first()
            if r_sug != None:
                for sug_id in r_sug.ready_suggestions:
                    if sugs_counters.get(sug_id) != None:
                        sugs_counters[sug_id]["view"] += 1
                for sug_id in r_sug.view_suggestions:
                    if sugs_counters.get(sug_id) != None:
                        sugs_counters[sug_id]["real"] += 1
                phone_counter = await Showed_Phone_Number.filter(r_sug_id=r_sug.id).exclude(tg_id__in=self.staff_id)
                for sug_id in phone_counter:
                    if sugs_counters.get(sug_id.sug_id) != None:
                        sugs_counters[sug_id.sug_id]["phone"] += 1
        i=2
        for id, count in sugs_counters.items():
            ref = await Ref_Links.filter(sug_title=count['title']).first()
            ref_count = 0
            worksheet.write(i, 0, count['title'])
            worksheet.write(i, 1, count['view'])
            worksheet.write(i, 2, count['real'])
            if ref != None:
                ref_count = await Ref_User.filter(ref_link=ref.ref_link, date_create__range = [self.startpoint, self.endpoint]).count()
                worksheet.write(i, 3, ref_count)
                worksheet.write(i, 4, "ссылка")
            else:
                worksheet.write(i, 3, count['phone'])
                worksheet.write(i, 4, "телефон")
            i+=1


    async def age_stat(self):
        worksheet = self.workbook.add_worksheet("Статистика возрастов")
        num = self.workbook.add_format()
        num.set_num_format(2)
        worksheet.write(0, 0, "Возраст")
        worksheet.write(0, 1, "Мужской")
        worksheet.write(0, 2, "Прошли этап знакомства")
        worksheet.write(0, 3, "Женский")
        worksheet.write(0, 4, "Прошли этап знакомства")
        worksheet.write(0, 5, "Всего")
        worksheet.write(0, 6, "Прошли этап знакомства")
        worksheet.write(0, 7, "Общее кол-во сессий")
        worksheet.write(0, 8, "Среднее кол-во сессий")
        i = 2
        for age in range(10, 100):
            users = await User_Tg.filter(age=age).exclude(id__in = self.staff_id)
            if len(users) != 0:
                male = await User_Tg.filter(age=age, gender = "Мужской").exclude(id__in = self.staff_id)
                female = await User_Tg.filter(age=age, gender = "Женский").exclude(id__in = self.staff_id)
                male_advert = 0
                female_advert = 0
                for m in male:
                    if m.advert != None:
                        male_advert += 1
                for f in female:
                    if f.advert != None:
                        female_advert += 1
                session = await Main_Session.filter(tg_id__in = [dict(v)["id"] for v in users if "id" in dict(v).keys()])
                worksheet.write(i, 0, age)
                worksheet.write(i, 1, len(male))
                worksheet.write(i, 2, male_advert)
                worksheet.write(i, 3, len(female))
                worksheet.write(i, 4, female_advert)
                worksheet.write(i, 5, len(male)+len(female))
                worksheet.write(i, 6, male_advert+female_advert)
                worksheet.write(i, 7, len(session))
                worksheet.write(i, 8, len(session)/(len(male)+len(female)), num)
                i+=1
        worksheet.write(1, 1, f"=СУММ(B3: B{i+1})")
        worksheet.write(1, 2, f"=СУММ(C3: C{i+1})")
        worksheet.write(1, 3, f"=СУММ(D3: D{i+1})")
        worksheet.write(1, 4, f"=СУММ(E3: E{i+1})")
        worksheet.write(1, 5, f"=СУММ(F3: F{i+1})")
        worksheet.write(1, 6, f"=СУММ(G3: G{i+1})")
        worksheet.write(1, 7, f"=СУММ(H3: H{i+1})")
        worksheet.write(1, 8, f"=СУММ(I3: I{i+1})")
    
    
    async def ques_combo(self):
        worksheet = self.workbook.add_worksheet("Комбо 1 и 2")
        worksheet2 = self.workbook.add_worksheet("Вопрос 4")
        worksheet.write(0, 0, "Вопрос 1")
        worksheet.write(0, 1, "Вопрос 2")
        worksheet.write(0, 2, "Кол-во")
        worksheet2.write(0, 0, "Вопрос 4")
        worksheet2.write(0, 1, "Кол-во")
        sessions = await Main_Session.exclude(tg_id__in = self.staff_id)
        combo = {}
        comdo_stat_answer = {}
        for session in sessions:
            if session.answers != None:
                if len(session.answers) == 2:
                    if combo.get(tuple(session.answers)) == None:
                        combo.update({tuple(session.answers) : 0})
                    combo[tuple(session.answers)] += 1
            if session.stat_answer != None:
                if comdo_stat_answer.get(session.stat_answer["Кого ты хочешь пригласить?"]) == None:
                    comdo_stat_answer.update({session.stat_answer["Кого ты хочешь пригласить?"] : 0})
                comdo_stat_answer[(session.stat_answer)["Кого ты хочешь пригласить?"]] += 1
        sorted_combo = dict(sorted(combo.items()))
        i = 1
        for k, v in sorted_combo.items():
            worksheet.write(i, 0, k[0])
            worksheet.write(i, 1, k[1])
            worksheet.write(i, 2, v)
            i+=1
        i = 1
        for k, v in comdo_stat_answer.items():
            worksheet2.write(i, 0, k)
            worksheet2.write(i, 1, v)
            i+=1
    
    async def promoters_date(self):
        filepath = 'stat/promo_date_stat.xlsx'
        promoters = await Promoter.all().order_by("distribution_chanell")
        workbook = xlsxwriter.Workbook(filepath)
        worksheet = workbook.add_worksheet('Статистика промоутеров')
        worksheet.set_column(0, 0, 30)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 60)
        merge_format = workbook.add_format({
            'bold':     True,
            'align':    'center',
            'num_format': 'dd/mm/yy'
        })
        worksheet.merge_range(0,0,0,3,f"{str(self.startpoint.date())} - {str(self.endpoint.date())}", merge_format)
        worksheet.write(1, 0, 'Ссылка/Никнейм')
        worksheet.write(1, 1, 'Платформа')
        worksheet.write(1, 2, 'Реф. ссылка')
        worksheet.write(1, 3, 'Счётчик')
        i = 2
        for promo in promoters:
            users = await User_Tg.filter(date_create__range = [self.startpoint, self.endpoint], ref_link_id=promo.id).exclude(id__in=self.staff_id)
            counter = len(users)
            worksheet.write(i, 0, promo.full_name)
            worksheet.write(i, 1, promo.distribution_chanell)
            worksheet.write(i, 2, f"https://t.me/Noboringdate_bot?start={promo.ref_link}")
            worksheet.write(i, 3, counter)
            i+=1
        workbook.close()
        return filepath


    @staticmethod
    async def all_promoters():
        filepath = 'stat/all_promoters.xlsx'
        promoters = await Promoter.all().order_by("distribution_chanell")
        workbook = xlsxwriter.Workbook(filepath)
        worksheet = workbook.add_worksheet('Статистика промоутеров')
        worksheet.set_column(0, 0, 30)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 60)
        worksheet.write(0, 0, 'Ссылка/Никнейм')
        worksheet.write(0, 1, 'Платформа')
        worksheet.write(0, 2, 'Реф. ссылка')
        worksheet.write(0, 3, 'Счётчик')
        i = 1
        for promo in promoters:
            worksheet.write(i, 0, promo.full_name)
            worksheet.write(i, 1, promo.distribution_chanell)
            worksheet.write(i, 2, f"https://t.me/Noboringdate_bot?start={promo.ref_link}")
            worksheet.write(i, 3, promo.people_counter)
            i+=1
        workbook.close()
        return filepath

    async def start(self):
        filepath = 'stat/all_statistic.xlsx'
        self.workbook = xlsxwriter.Workbook(filepath)
        await self.statistic_sug()
        await self.age_stat()
        await self.ques_combo()
        await self.statistic_sug_date()
        self.workbook.close()
        return filepath