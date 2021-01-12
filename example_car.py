from run import main,analyze_data, send_mail
import smtplib

gmail_user = "mail_for_sending@gmail.com"
gmail_password = "password"
to = ["mail1@gmail.com", "mail2@email.com"]

name = "example_car"
scrap_urls = ["https://www.avto.net/Ads/results.asp?znamka=&model=&modelID=&tip=&znamka2=&model2=&tip2=&znamka3=&model3=&tip3=&cenaMin=2000&cenaMax=3500&letnikMin=2009&letnikMax=2090&bencin=201&starost2=999&oblika=0&ccmMin=0&ccmMax=99999&mocMin=&mocMax=&kmMin=0&kmMax=200000&kwMin=0&kwMax=999&motortakt=0&motorvalji=0&lokacija=0&sirina=0&dolzina=&dolzinaMIN=0&dolzinaMAX=100&nosilnostMIN=0&nosilnostMAX=999999&lezisc=&presek=0&premer=0&col=0&vijakov=0&EToznaka=0&vozilo=&airbag=&barva=&barvaint=&EQ1=1000000000&EQ2=1000000000&EQ3=1002340000&EQ4=100000000&EQ5=1000000000&EQ6=1000000000&EQ7=1110100020&EQ8=1010000001&EQ9=1000000000&KAT=1010000000&PIA=&PIAzero=&PSLO=&akcija=0&paketgarancije=&broker=0&prikazkategorije=0&kategorija=0&ONLvid=0&ONLnak=0&zaloga=10&arhiv=0&presort=3&tipsort=DESC&stran=1&subSORT=2&subTIPSORT=DESC"]
distance_from = "Kongresni trg, Ljubljana, Slovenija"
ignore_list = ["Mercedes"]
scrape_file = "scraped_data/" + name + ".csv"
archive_data_file = "archive_data/" + name + ".csv"
print_columns = ["points","manufacturer","model", "price","manufacturing_year","kilometrage","avtolog_url","location", "captured_today", "url"]


def calculate_points(Ad):
    if not Ad["active"]:
        return 0
    points = 0
    if Ad["is_dealership"]:
        points += 10
    if Ad["vin"]:
        points += 10
    points += (Ad.get("price",3500) - 2000)/1500 * -50
    points += (Ad.get("manufacturing_year",2009) - 2010) * 20
    points += (200000 - Ad.get("kilometrage",200000))/10000 * 4

    if Ad.get("distance",60) > 50:
        points += -20

    if Ad["manufacturer"].lower() in ("chevrolet","citroen") or Ad["model"].lower() in ("clio", "getz", "megane","207","modus","107","i10","Aygo",""):
        points += -100

    if Ad["manufacturer"].lower() in ("") or Ad["model"].lower() in ("ceed","i30"):
        points += 50


    if not Ad["captured_today"]:
        old = -50
    else:
        old = 0


    return points


data = main(name, scrap_urls, ignore_list, calculate_points, distance_from,scrape_file, archive_data_file, print_columns )
message = "#####NEW: \n" +data["new"] +  "\n######TOP 20:\n" + data["top20"]
#send_mail(gmail_user, gmail_password,to, message)
