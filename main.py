from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.responses import JSONResponse
from starlette.background import BackgroundTasks
from models import Users
import uvicorn
from urllib import parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import requests
from tortoise.contrib.starlette import register_tortoise

templates = Jinja2Templates(directory='templates')

async def send_noti_email():
    appid = ''
    city = 'Moscow'
    res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                 params={'q': city, 'units': 'metric', 'lang': 'ru', 'APPID': appid})

    data = res.json()
    conditions = "conditions:", data['weather'][0]['description']
    temp = "temp:", data['main']['temp']

    msg = MIMEMultipart()
    message = "Погода в Москве на сегодня\n{}\n{}".format(conditions, temp)
    password = ''
    msg['From'] = ""
    msg['To'] = email
    msg['Subject'] = "Погода"

    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(msg['From'], password)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

async def homepage(request):
    template = "index.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context)

async def reg(request):
    template = "index.html"
    context = {"request": request}

    res = await request.form()
    email = res['email']
    password = res['password']

    await Users.create(email=email)
    return templates.TemplateResponse(template, context)

async def noti(request):
    tasks = BackgroundTasks()
    tasks.add_task(send_noti_email)
    message = {'status': True}
    return JSONResponse(message, background=tasks)

routes = [
    Route('/', endpoint=homepage),
    Route('/registration', endpoint=reg, methods=['POST']),
    Route('/noti', endpoint=noti, methods=['POST']),
    Mount('/static', StaticFiles(directory='statics'), name='static')
]

app = Starlette(debug=True, routes=routes)

register_tortoise(
    app, db_url="mysql://root:123456@localhost:3306/reg",
    modules={"models": ["models"]},
    generate_schemas=True
)

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)