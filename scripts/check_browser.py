"""Реальная браузерная проверка. Дополнительно: pip install playwright;
python -m playwright install chromium. Запуск: python scripts/check_browser.py.
Использует отдельную временную SQLite и обновляет только проверочные материалы docs.
"""
import json, os, subprocess, sys, time, tempfile
from pathlib import Path
from urllib.request import urlopen
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:8000'
SHOTS=ROOT/'docs/screenshots'
log=[]; server=None
temporary_db = tempfile.TemporaryDirectory(prefix='autodetal-browser-')
DB_PATH=Path(temporary_db.name)/'browser.db'

def start_server():
    proc=subprocess.Popen([sys.executable,'-m','uvicorn','backend.app.main:app','--host','127.0.0.1','--port','8000'],cwd=ROOT,env={**os.environ,'DATABASE_URL':f'sqlite:///{DB_PATH.as_posix()}'},stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    time.sleep(.3)
    for _ in range(100):
        if proc.poll() is not None: raise RuntimeError(proc.stderr.read().decode())
        try:
            urlopen(BASE+'/api/health',timeout=1).close(); return proc
        except OSError: time.sleep(.1)
    proc.terminate(); raise RuntimeError('Backend не запустился')

def note(text): log.append(text);print('PASS:',text,flush=True)

def fill(page):
    for key,value in {'name':'Тестовая деталь','price':'790.50','description':'Запись для проверки интерфейса и сохранения в SQLite.','article':'UI-TEST-001','parameter':'Проверка браузером'}.items():page.locator('#item-'+key).fill(value)
    page.locator('#item-category').select_option('1')

try:
    server=start_server()
    with sync_playwright() as p:
        config=json.loads(Path(os.environ['BROWSER_LAUNCH_CONFIG']).read_text()) if os.getenv('BROWSER_LAUNCH_CONFIG') else {}
        browser=p.chromium.launch(headless=True,executable_path=config.get('executablePath'),args=config.get('args',[]))
        context=browser.new_context(viewport={'width':1440,'height':1400},device_scale_factor=1)
        page=context.new_page(); errors=[]; traffic=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('request',lambda req:traffic.append((req.method,req.url)) if '/api/' in req.url else None)
        page.goto(BASE)
        expect(page.locator('.card')).to_have_count(6)
        expect(page.locator('#api-state')).to_have_text('Данные получены из базы')
        note('6 исходных карточек загружены через API; категории получены с сервера')
        page.locator('#query').fill('AP-FL-001');expect(page.locator('.card')).to_have_count(1)
        page.locator('#query').fill('');page.locator('#category').select_option('1');expect(page.locator('.card')).to_have_count(2)
        page.locator('#category').select_option('all');page.locator('#sort').select_option('price-asc')
        expect(page.locator('.card h3').first).to_have_text('Масляный фильтр')
        page.locator('#sort').select_option('name-asc')
        note('Поиск, категории и сортировка ЛР2 работают')
        page.locator('#add-item-button').click();page.locator('#save-button').click()
        expect(page.locator('[data-error-for="name"]')).not_to_be_empty();fill(page)
        with page.expect_response(lambda r:r.url.endswith('/api/parts') and r.request.method=='POST') as response:page.locator('#save-button').click()
        assert response.value.status==201,response.value.text()
        item_id=response.value.json()['id']
        expect(page.locator('#modal')).to_be_hidden();expect(page.locator('.card')).to_have_count(7)
        note('Валидация пустой формы и создание через интерфейс: POST 201')
        server.terminate();server.wait(timeout=10);server=start_server();page.reload()
        card=page.locator(f'.card[data-id="{item_id}"]')
        expect(card).to_be_visible();note('После перезапуска backend запись остаётся в SQLite и на сайте')
        card.locator('[data-edit-id]').click();expect(page.locator('#item-name')).to_have_value('Тестовая деталь')
        page.locator('#item-price').fill('849.90');page.locator('#item-category').select_option('2')
        with page.expect_response(lambda r:r.url.endswith(f'/api/parts/{item_id}') and r.request.method=='PATCH') as changed:page.locator('#save-button').click()
        assert changed.value.status==200
        expect(page.locator('#modal')).to_be_hidden();page.reload()
        expect(card.locator('.price')).to_contain_text('849,90');expect(card.locator('.category')).to_have_text('Тормоза')
        note('GET одной записи и PATCH 200; новая цена и категория сохраняются после перезагрузки')
        page.locator('#add-item-button').click();fill(page);page.locator('#save-button').click()
        expect(page.locator('#form-error')).to_contain_text('уникальным')
        page.keyboard.press('Escape');expect(page.locator('#modal')).to_be_hidden()
        note('Повторный артикул отклоняется; сообщение видно в форме; Escape закрывает окно')
        page.once('dialog',lambda dialog:dialog.accept())
        with page.expect_response(lambda r:r.url.endswith(f'/api/parts/{item_id}') and r.request.method=='DELETE') as deleted:card.locator('[data-delete-id]').click()
        assert deleted.value.status==204
        expect(page.locator('.card')).to_have_count(6);page.reload();expect(page.locator('.card')).to_have_count(6)
        note('DELETE 204 из интерфейса; удалённая запись не возвращается')
        page.route('**/api/parts',lambda route:route.abort() if route.request.method=='GET' else route.continue_())
        page.locator('#reload-button').click();expect(page.locator('#app-message')).to_contain_text('Не удалось связаться')
        expect(page.locator('#api-state')).to_have_text('Нет связи с сервером')
        page.unroute('**/api/parts');page.locator('#reload-button').click()
        expect(page.locator('#api-state')).to_have_text('Данные получены из базы')
        note('Сообщение об ошибке сети и повторная загрузка работают')
        payload={'name':'Салонный фильтр','description':'Очищает воздух в салоне автомобиля от пыли. Добавлен через REST API при проверке ЛР3.','article':'AP-CB-007','price':'790.50','category_id':1,'parameter':'Угольный, 200 × 180 мм','image_url':'/assets/images/filter.svg'}
        demo=context.request.post(BASE+'/api/parts',data=payload);assert demo.status==201,demo.text()
        (ROOT/'docs/http-demonstration.json').write_text(json.dumps({'request':{'method':'POST','path':'/api/parts','body':payload},'response':{'status':demo.status,'body':demo.json()}},ensure_ascii=False,indent=2),encoding='utf-8')
        page.reload();expect(page.locator('.card')).to_have_count(7)
        page.locator('.connection-panel').scroll_into_view_if_needed();page.screenshot(path=str(SHOTS/'01-frontend.png'))
        page.set_viewport_size({'width':390,'height':844});page.goto(BASE+'/#catalog');expect(page.locator('.card')).to_have_count(7)
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        page.locator('#catalog').scroll_into_view_if_needed();page.screenshot(path=str(SHOTS/'04-mobile.png'));page.locator('#add-item-button').click()
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        expect(page.locator('#item-name')).to_be_visible();page.keyboard.press('Escape')
        note('Экран 390 px: горизонтальной прокрутки нет, модальная форма доступна')
        page.set_viewport_size({'width':1440,'height':1100});page.goto(BASE+'/docs')
        expect(page.locator('.opblock')).to_have_count(8)
        page.screenshot(path=str(SHOTS/'02b-swagger-overview.png'),full_page=True)
        get_list=page.locator('.opblock-get').filter(has=page.locator('[data-path="/api/parts"]')).first
        get_list.locator('.opblock-summary').click();get_list.get_by_role('button',name='Try it out').click()
        get_list.get_by_role('button',name='Execute',exact=True).click()
        expect(get_list.locator('.response-col_status').filter(has_text='200').first).to_be_visible()
        page.screenshot(path=str(SHOTS/'02-swagger.png'),full_page=True)
        note('Swagger UI: методы доступны, GET раскрыт и исполнен с ответом 200')
        subprocess.run([sys.executable,str(ROOT/'scripts/inspect_db.py'),'--db',str(DB_PATH),'--html',str(ROOT/'docs/database-view.html')],cwd=ROOT,check=True,capture_output=True)
        page.goto((ROOT/'docs/database-view.html').as_uri());expect(page.locator('td').filter(has_text='AP-CB-007')).to_be_visible()
        page.screenshot(path=str(SHOTS/'03-database.png'),full_page=True);page.locator('table').screenshot(path=str(SHOTS/'03b-database-table.png'))
        note('Скриншот реального SELECT SQLite содержит исходные и добавленную записи')
        frontend=subprocess.Popen([sys.executable,'-m','http.server','5500','--bind','127.0.0.1'],cwd=ROOT/'frontend',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try:
            for _ in range(100):
                try:urlopen('http://127.0.0.1:5500',timeout=1).close();break
                except OSError:time.sleep(.1)
            page.goto('http://127.0.0.1:5500');expect(page.locator('.card')).to_have_count(7)
            note('Отдельный frontend :5500 загружает данные с :8000; CORS проверен браузером')
        finally:frontend.terminate();frontend.wait(timeout=10)
        assert not errors,errors
        assert any(method=='GET' and url.endswith(f'/api/parts/{item_id}') for method,url in traffic)
        assert {'POST','PATCH','DELETE'} <= {method for method,url in traffic}
        note('Ошибок JavaScript нет, сетевой журнал содержит GET/POST/PATCH/DELETE')
        browser.close()
finally:
    if server and server.poll() is None:server.terminate();server.wait(timeout=10)
    temporary_db.cleanup()
    (ROOT/'docs/browser-tests.txt').write_text('\n'.join('PASS: '+line for line in log)+'\n',encoding='utf-8')
