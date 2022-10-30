"""Aplicatie Flask care afiseaza valorile din excelurile unui dosar
gen:
OL1 --- 3 euro
    P1- 1 EUR
    P2- 2 EUR
OL5 --- 5 EUR
    P3- 4 EUR

"""
# import csv

# SomeDay -- https://www.youtube.com/watch?v=iO0sL6Vyfps&ab_channel=PrettyPrinted




# https://www.odoo.com/documentation/14.0/developer/misc/api/odoo.html -- l-am facut pana la urma
# TODO 2 -- sa verific daca un produs exista si daca nu sa il creez

# TODO 5 -- sa fac un buton in oferta care sa incarce toate produsele care corespund (gen dosar 22540)
# TODO 6 -- sa fac mai multe verificari
#TODO 7 -- sa fac deviz pe google drive , sa copiez fisierul xls acolo si sa afisez linkul pe consolidare
# adica asta --
# https://apps.odoo.com/apps/modules/14.0/gt_mass_pro_selection/
import os
import Deviz
import openpyxl
import re
import base64

from flask import Flask, render_template, request, redirect, url_for,render_template_string
from flask_bootstrap import Bootstrap5
from flask_basicauth import BasicAuth
from flask_sqlalchemy import SQLAlchemy

from PIL import Image

from xmlrpc import client

import config
import src.testSaleOrder as SaleOrder
from ProductData import ProductData

common = client.ServerProxy('%s/xmlrpc/2/common' %
    config.server_url,allow_none=True)
user_id = common.authenticate(config.db_name, config.username,config.password, {})

if user_id:
   print("Success: User id is", user_id)
else:
   print("Failed: wrong credentials")

# import pandas as pd

app = Flask(__name__)
bootstrap = Bootstrap5(app)
#Bootstrap(app)
import data.appLogin

app.config['BASIC_AUTH_USERNAME']=data.appLogin.app.config['BASIC_AUTH_USERNAME']
app.config['BASIC_AUTH_PASSWORD'] = data.appLogin.app.config['BASIC_AUTH_PASSWORD']
app.config['BASIC_AUTH_FORCE'] = True


import urllib

basic_auth = BasicAuth(app)
params = urllib.parse.quote_plus('DRIVER={ODBC+Driver+17+for+SQL+Server};SERVER=192.168.2.6;DATABASE=Metal;DATABASE=test;UID=bogdan;PWD=HELPAN123$')
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params
app.config['SERVER_NAME'] = "exodus.helpan.ro"
#app.config["SQLALCHEMY_DATABASE_URI"] = "mssql+pyodbc://user:pwd@server/database?driver=SQL+Server"

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

db.create_all()


class Dosare(db.Model):
    DosarId = db.Column(db.Integer, primary_key=True,index=True)
    Firma = db.Column(db.String(64), index=True)
    Referinta = db.Column(db.String(64),index=True)
    DataCrearii = db.Column(db.String(64))
    #age = db.Column(db.Integer, index=True)
    #address = db.Column(db.String(256))
    #phone = db.Column(db.String(20))
    #email = db.Column(db.String(120))

    def to_dict(self):
        return {
            'name': self.Firma,
            'id': self.DosarId,
            'referinta':self.Referinta,
            'link': '<a class="btn btn-dark" href="/dosar/'+str(self.DosarId)+'">Deschide</a>',
            'datacrearii':self.DataCrearii,
            #'DosarID': self.DosarID,
            #'phone': self.phone,
            #'email': self.email
        }

@app.route('/secret')
@basic_auth.required
def secret_view():
    return render_template('secret.html')


@app.route('/')
def index():
   # return render_template('base.html', status=True)
   return render_template('server_table.html', title='Tabel cu dosarele HELPAN')



def uploadProductOdoo(dosar, Devize,upload2OdooSeturi=False):
    i=0
    models = client.ServerProxy('{}/xmlrpc/2/object'.format(config.server_url),allow_none=True)
    result = (models.execute_kw(config.db_name, user_id, config.password,
                                'helpan.dosar', 'search_read',
                                [[['internal_identify', '=', dosar]]],
                                {'fields': ['name', 'id']}))
    if len(result)==1:
        dosar=result[0]["id"]
        print(dosar)
    else:
        return False
        dosar=1
        print("default")

    from datetime import datetime, timedelta

    d = datetime.today() - timedelta(hours=3)

    for count,Deviz in enumerate(Devize):
        if upload2OdooSeturi:
            pass# print("Urcam doar devizele")
        else:
            # print("Urcam {} produse noi".format(i))
            yield from ParcurgeDevizul(Deviz, Devize, count, d, dosar, i, models, result)
    return True


def ParcurgeDevizul(Deviz, Devize, count, d, dosar, i, models, result):
    for Reper in Deviz.Repere:
        ProductX = ProductData()
        ResultCautaProductTemplate,idX = DateProdus(ProductX, Reper, dosar, models)

#        models.execute_kw(config.db_name, user_id, config.password, 'sale.order.line', 'write', )

        if (idX is None):
            yield from AdaugareProdusNou(Deviz, Devize, Reper, count, d, dosar, models)
        else:
            if (len(idX) == 1):
                dictionar={"pret":Reper.pret,"cantitate":Reper.NrBuc}


                # print(f"Actualizez datele unui reper {Reper.nume} {result[0]['id']}   {type(result[0]['id'])}")
                # print(f'idx {idX["id"]}')
                with open(Reper.CalePozaBMPServer, "rb") as img:
                    b64_image = base64.b64encode(img.read())
                    data = {'image_1920': b64_image.decode('ascii')}
                # print("The type of imageBase64 is ", type(b64_image))
                # TODO: trebuie inserat ca product.product!

                print(f"Am actualizat preturile la ProductProduct {ProductX.ProductProductID}")
                print(f'{Reper.nume},{Reper.MasaEfectiva},{dosar}')
                print(idX)
                idX = idX[0]
                idX.update(dictionar)
                try:
                    idProdusVechi = (models.execute_kw(config.db_name, user_id, config.password,
                                                   'product.product', 'write', [ProductX.ProductProductID, {
                        # material,grosimea, Material+grosime
                        # nrbuc
                        # 'name': Reper.nume,
                        # 'type': "consu",
                        # 'list_price': 0,
                        # 'company_id': 1,
                        # 'weight': Reper.MasaEfectiva,
                        # 'sale_ok': True,
                        # "product_tmpl_id": 10266,
                        # 'image_1920': b64_image.decode('ascii'),
                        # 'dosar_id': dosar,
                        # 'team_id': 2,
                        'cantitate': Reper.NrBuc
                    }]))
                except:
                    #TODO: de adaugat cantitate in produs.produs
                    print(f'WARN 101: exceptie la scrierea produsului cu id {ProductX.ProductProductID}')
                # product_tmpl_id daaca e product_template
                resultPret = (models.execute_kw(config.db_name, user_id, config.password,
                                                'product.pricelist.item', 'search_read',
                                                [[['product_id', '=', ProductX.ProductProductID]]],
                                                {'limit': 5}))
                print(f'Avem {len(resultPret)} preturi pentru acest id {ProductX.ProductProductID} nume {ProductX.Name} ')
                if (len(resultPret) == 1):
                    print(f'Actualizez produsul {ProductX.Name} avand id {ProductX.ProductProductID} cu {Reper.pret} ')
                    models.execute_kw(config.db_name, user_id, config.password,
                                      'product.pricelist.item', 'write', [resultPret[0]['id'], {
                            "applied_on": "0_product_variant",
                            "base": "list_price",
                            "compute_price": "fixed",
                            "name": Reper.nume,
                            "pricelist_id": 2,
                            "currency_id": 1,
                            # "company_id": 1,
                            # "product_tmpl_id": result[0]['id'],
                            'product_id': ProductX.ProductProductID,
                            "fixed_price": Reper.pret,
                            "min_quantity": Reper.NrBuc,
                           # 'date_start': d.strftime('%Y-%m-%d %H:%M:%S'),
                            'active': True
                        }])
                elif (len(resultPret) == 0):
                    print(f'Aplicam date {ProductX.ProductProductID}')
                    models.execute_kw(config.db_name, user_id, config.password,
                                      'product.pricelist.item', 'create', [{
                            "applied_on": "0_product_variant",
                            "base": "list_price",
                            "compute_price": "fixed",
                            "pricelist_id": 2,
                            "currency_id": 1,
                            # "company_id": 1,
                            #"product_tmpl_id": ProductX.ProductTemplateID,
                             'product_id': ProductX.ProductProductID,
                            "fixed_price": Reper.pret,
                            "min_quantity": Reper.NrBuc,
                            #'date_start': d.strftime('%Y-%m-%d %H:%M:%S'),
                            'active': True

                        }])


            else:
                print("ERR101: Avem mai multe rezultate - skipping {}".format(idX))
            yield (idX)
            continue

        # print(models.execute_kw(config.db_name, user_id, config.password,
        #                   'product.template', 'search_read',
        #                   [[['name', '=', Reper.nume]]],
        #                   {'fields': ['name', 'type', 'list_price'], 'limit': 5}))
        i += 1


def AdaugareProdusNou(Deviz, Devize, Reper, count, d, dosar, models):
    print("adaug un nou produs")
    with open(Reper.CalePozaBMPServer, "rb") as img:
        b64_image = base64.b64encode(img.read())
        data = {'image_1920': b64_image.decode('ascii')}
        print("The type of imageBase64 is ", type(b64_image))
    idProdusNou = (models.execute_kw(config.db_name, user_id, config.password,
                                     'product.product', 'create', [{
            'name': Reper.nume,
            'type': "consu",
            'list_price': 0,
            # 'company_id':1,
            'weight': Reper.MasaEfectiva,
            'sale_ok': True,
            'image_1920': b64_image.decode('ascii'),
            'dosar_id': dosar,
            'team_id': 2,

        }]))
    print(f'INFO 102: Am creat idul nou Product {idProdusNou}')
    models.execute_kw(config.db_name, user_id, config.password,
                      'product.pricelist.item', 'create', [{
            "applied_on": "0_product_variant",
            "base": "list_price",
            "compute_price": "fixed",
            "pricelist_id": 3,
            "currency_id": 1,
            # "company_id":1,
            #"product_tmpl_id": idProdusNou,
            'product_id':idProdusNou,
            "fixed_price": Reper.pret,
            "min_quantity": Reper.NrBuc,
            'date_start': d.strftime('%Y-%m-%d %H:%M:%S'),

        }])
    # product.pricelist.item
    dictionarProdus = {"id":idProdusNou,"pret": Reper.pret, "cantitate": Reper.NrBuc,"Deviz.Nume":Deviz.nume}
    Devize[count].status = "OK"
    print(f'setam status pentru {Deviz.nume} -- {Devize[count].status}')

    yield (dictionarProdus)


def DateProdus(ProductX, Reper, dosar, models):
    ResultCautaProductTemplate = (models.execute_kw(config.db_name, user_id, config.password,
                                                    'product.template', 'search_read',
                                                    [[['name', '=ilike', Reper.nume],
                                                      ]],
                                                    {'fields': ['name', 'type', 'list_price'], 'limit': 5}))
    #['dosar_id', '=', dosar]
    print(f'INFO 101: Rezultate produse conform denumire {Reper.nume} si dosar {dosar}: {len(ResultCautaProductTemplate)}')
    ResultCautaProductProduct=None
    if len(ResultCautaProductTemplate)>0:
        ProductX.ProductTemplateID = ResultCautaProductTemplate[0]['id']
        ProductX.Name = ResultCautaProductTemplate[0]['name']
        ResultCautaProductProduct = (models.execute_kw(config.db_name, user_id, config.password,
                                                   'product.product', 'search_read',
                                                   [[['product_tmpl_id', '=',
                                                      ResultCautaProductTemplate[0]['id']]]],
                                                   {'fields': ['name', 'type', 'list_price'], 'limit': 5}))
        if len(ResultCautaProductProduct) > 0:
            ProductX.ProductProductID = ResultCautaProductProduct[0]['id']
    return ResultCautaProductTemplate,ResultCautaProductProduct


@app.route('/api/data')
def data():
    from sqlalchemy import desc
    query = Dosare.query.order_by(desc(Dosare.DosarId))

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            Dosare.Firma.like(f'%{search}%')
           # User.email.like(f'%{search}%')
        ))
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['Firma']:
            col_name = 'Firma'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'

        col = getattr(Dosare, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [user.to_dict() for user in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': Dosare.query.count(),
        'draw': request.args.get('draw', type=int),
    }

@app.route('/api/datadevize/<dosar>')
def datadevize(dosar):
    #returnam lista cu devizele de pe google avand idul referent
    import pydriveTest
    listaFisiere = pydriveTest.listaDevize(dosar)

    # search filter
    #search = request.args.get('search[value]')


    # response to_dict() alternateLink
    return {
        'data': [fisier['title'] for fisier in listaFisiere],
        'datalink': [fisier['alternateLink'] for fisier in listaFisiere],
        'draw': request.args.get('draw', type=int),
    }

@app.route('/deviz/<deviz>')
def deviz(deviz):
    import pydriveTest
    link=pydriveTest.deviz(deviz)
    print(link)
    print("RUNNINGX")
    #https://docs.google.com/spreadsheets/d/1hpgrEIOjlM4Htsh45g6C0vrjY2JaBbdeQaKYgi_4wIA
    return redirect(link)

@app.route('/dosar/<dosar>')
def dosar(dosar):
    # user_agent = request.headers.get('User-Agent')
    # return '<p>Your browser is %s</p>' % user_agent
    # cum trimit datele catre consolidarE?
    # for fname in os.listdir(path='/mnt/xLucru'):
    # Apply file type filter
    #    if fname.endswith(file_type):
    succes = request.args.get('succes',default=False)
    OdooURL = request.args.get('OdooURL', default="")
    upload2Odoo = request.args.get('gotoOdoo')
    upload2OdooSeturi = request.args.get('seturi')
    print(f'Am primit gotoOdoo {upload2Odoo} si seturi {upload2OdooSeturi}')
    i = 0
    DateFolder = ''
    observatii = ''
    filenames = []
    Devize = []
    modele = []
    CaleScanata = '/mnt/xLucru'
    subfolders = [f.path for f in os.scandir(CaleScanata) if f.is_dir()]
    for folder in subfolders:
        # nume=str(folder)
        if str(dosar) in str(folder):
            i += 1
            DateFolder = folder
            # folder.name
            DateFolderComplet = os.path.join(CaleScanata, folder)

    if i == 1:
        folder = DateFolder
        from pathlib import Path
        filenames = Path(folder).rglob('Deviz*.xlsx')  # face recursiv
        for filename in filenames:
            sarim = False
            wb = openpyxl.load_workbook(filename, data_only=True)
            WorkSheet = wb.worksheets[0]
            info = "General"
            numeDevizScanat = WorkSheet['A5'].value
            for DevizTemp in Devize:
                if DevizTemp.nume == numeDevizScanat:
                    if DevizTemp.mTime >= os.path.getmtime(filename):
                        print("IGNORAM si sarim")
                        sarim = True
                    else:
                        Devize.remove(DevizTemp)
                        print("DUPLICAT {} vs {}".format(DevizTemp.mTime, os.path.getmtime(filename)))
            if sarim == True:
                continue
            Devizul = Deviz.Deviz(numeDevizScanat)
            Devizul.setmTime(os.path.getmtime(filename))
            Devizul.setUoM(WorkSheet['B5'].value)
            Devizul.setNrBuc(WorkSheet['C5'].value)
            Devizul.setPret(WorkSheet['D5'].value)
            Devizul.filename = filename

            WorkSheetPiese = wb.worksheets[3]
            for i in range(1, 60):
                if WorkSheetPiese['A' + str(i)].value == None:
                    break
            NrRepere = i
            #print("VALUE is {}".format(i))
            Repere = []
            if NrRepere > 1:
                for reperTemp in range(2, NrRepere):
                    Reper = Deviz.Reper(WorkSheetPiese['B' + str(reperTemp)].value)
                    Reper.setPret(round(WorkSheetPiese['R' + str(reperTemp)].value, 2))
                    Reper.setNrBuc(WorkSheetPiese['D' + str(reperTemp)].value)
                    Reper.CalePozaBMPOriginala = WorkSheetPiese['AA' + str(reperTemp)].value
                    Reper.Lungime = WorkSheetPiese['E' + str(reperTemp)].value
                    Reper.Latime = WorkSheetPiese['F' + str(reperTemp)].value
                    Reper.Grosime = WorkSheetPiese['G' + str(reperTemp)].value
                    Reper.MasaEfectiva = WorkSheetPiese['H' + str(reperTemp)].value
                    from shutil import copyfile
                    file = (WorkSheetPiese['AA' + str(reperTemp)].value)
                    try:
                        if "file" in file:
                            compiled = re.compile(re.escape("file://///192.168.2.45/q/00 PRODUCTIE/00 COTATII IN LUCRU"),
                                                  re.IGNORECASE)
                            res = compiled.sub("{}".format(r"/mnt/xLucru"),
                                               file)
                        else:
                            compiled = re.compile(re.escape("\\\\192.168.2.45\\q\\00 PRODUCTIE\\00 COTATII IN LUCRU"),
                                              re.IGNORECASE)
                            res = compiled.sub("{}".format(r"/mnt/xLucru"),
                                           file)
                    except:
                        return
                    res = res.replace("\\", "/")
                    NumePoza = res[res.rindex("/"):]
                    copyfile(res, 'static/poze{}'.format(NumePoza))
                    img = Image.open('static/poze{}'.format(NumePoza))

                    NumePozaPNG = re.compile(re.escape('bmp'), re.IGNORECASE)
                    NumePozaPNG=NumePozaPNG.sub('png', NumePoza)
                    print(NumePozaPNG)
                    new_img = img
                    new_img.save('static/poze{}'.format(NumePozaPNG), 'png')
                    Reper.CalePozaBMPServer = 'static/poze{}'.format(NumePoza)
                    Reper.CalePozaPNGServer = 'static/poze{}'.format(NumePozaPNG)

                    Repere.append(Reper)

            Devizul.setCaleFisier(filename)
            Devizul.setRepere(Repere)
            Devize.append(Devizul)
        if len(Devize)==0:
            modele = Path(folder).rglob('*.stp')  # face recursiv
            Repere=[]
            for model in modele:
                if model.name.count('-')>3:
                    PartIndex=model.name.index("Part")
                    EndofPartIndex=model.name.index("-",PartIndex)
                    indexQnt = model.name.index("Qnt")
                    EndofQnt = model.name.index("-", indexQnt)
                    if PartIndex>0:
                        Reper = Deviz.Reper(model.name[PartIndex:EndofPartIndex])
                        print(model.name[indexQnt+3:EndofQnt])
                        Reper.setNrBuc(int(model.name[indexQnt+3:EndofQnt]))
                else:
                    Reper = Deviz.Reper(model.name)

                print("Model: {0}".format(str(model.name)))


                Repere.append(Reper)
            Devizul = Deviz.Deviz("test")
            Devizul.setRepere(Repere)
            Devize.append(Devizul)

            #Todo sa ii iau informatiile
            #1. proiect E-223851-207764
            #2. PartID Part407283
            #3. Qty Qty
            #4. Nume
        observatii = "Nr fisiere devize: {}".format(len(Devize))
    if upload2Odoo=='True':
        if upload2OdooSeturi=='True':
            upload2OdooSeturi=True
        else:
            upload2OdooSeturi=False
        print("Urcam Odoo: {} in cadrul dosarului {}".format(upload2OdooSeturi,dosar))
        SaleOrder.DosarCautat=dosar
        SaleOrder.ObtineIDDosar(SaleOrder.DosarCautat)
        SaleOrder.numePartener="%AVI%"
        SaleOrder.ObtineIDPartener()
        SaleOrder.ObtineIDOferta()
        print(f'ID Obtinut este {SaleOrder.OfertaID}')
        OdooURL=f'web#id={SaleOrder.OfertaID}&action=292&model=sale.order&view_type=form&cids=1&menu_id=176'

        listaIDs=uploadProductOdoo(dosar,Devize,upload2OdooSeturi)

        generator_list = list(listaIDs)
        for date in generator_list:
            print(f'Date: {date}')

            SaleOrder.AdaugaProdusInOferta(date['id'],date['pret'],date['cantitate'])
        return redirect(url_for('dosar', dosar=dosar,succes=True,OdooURL=OdooURL))
    else:
        js = render_js('static/js/form.js')
        return render_template('Consolidare.html', dosar=dosar, DateFolder=DateFolder,
                           observatii=observatii, Devize=Devize,succes=succes,OdooURL=OdooURL,js=js)
    # return '<h1>Hello, {}!</h1> Your browser is {}'.format(name , user_agent)

def render_js(fname, **kwargs):
    with open(fname) as fin:
        script = fin.read()
        rendered_script = render_template_string(script, **kwargs)
        return rendered_script
    
@app.route('/refresh')
def refresh():
    pass
    # nu`mi e clar ce sa fac
    # subprocess.call(["python3", "/opt/DaeDalusTools/getData.py"], shell=False)


if __name__ == '__main__':
    app.run(debug=True, port=8090, threaded=True, host="0.0.0.0")
