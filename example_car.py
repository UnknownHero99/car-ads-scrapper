from run import main,analyze_data, send_mail
import smtplib

gmail_user = "mail_for_sending@gmail.com"
gmail_password = "password"
to = ["mail1@gmail.com", "mail2@email.com"]

name = "example_car"
scrap_urls = ["https://www.avto.net/Ads/results.asp?znamka=&model=&modelID=&tip=&znamka2=&model2=&tip2=&znamka3=&model3=&tip3=&cenaMin=2000&cenaMax=3500&letnikMin=2007&letnikMax=2090&bencin=201&starost2=999&oblika=&ccmMin=0&ccmMax=99999&mocMin=&mocMax=&kmMin=0&kmMax=250000&kwMin=0&kwMax=999&motortakt=&motorvalji=&lokacija=0&sirina=&dolzina=&dolzinaMIN=&dolzinaMAX=&nosilnostMIN=&nosilnostMAX=&lezisc=&presek=&premer=&col=&vijakov=&EToznaka=&vozilo=&airbag=&barva=&barvaint=&EQ1=1000000000&EQ2=1000000000&EQ3=1002340000&EQ4=100000000&EQ5=1000000000&EQ6=1000000000&EQ7=1110100020&EQ8=1010000001&EQ9=100000000&KAT=1010000000&PIA=&PIAzero=&PSLO=&akcija=&paketgarancije=0&broker=&prikazkategorije=&kategorija=&ONLvid=&ONLnak=&zaloga=10&arhiv=&presort=&tipsort=&stran="]
distance_from = "Kongresni trg, Ljubljana, Slovenija"
ignore_list = ["Mercedes"]
scrape_file = "scraped_data/" + name + ".csv"
archive_data_file = "archive_data/" + name + ".csv"
print_columns = ["points","manufacturer","model", "price","manufacturing_year","kilometrage","avtolog_url","location", "captured_today", "url"]

scoring_map = {
    "price": {
        "type": "reverse",
        "points_per_unit": 1
    },
    "manufacturing_year": {
        "type": "normal",
        "points_per_unit": 200
        },
    "kilometrage": {
        "type": "reverse",
        "points_per_unit": 50/10000,
        },
    "is_dealership": {
        "type": "map",
        "points_map": {False:0,True:200}
        },
    "manufacturer": {
        "type": "contains",
        "values": ["chevrolet","citroen"],
        "points":-1500
        },
    "model": {
        "type": "contains",
        "values": ["clio", "getz", "megane","207","modus","107","i10","aygo","colt", "fiesta","grand modus"],
        "points": -1500
        },
    "model": {
        "type": "contains",
        "values": ["ceed","i30"],
        "points": 750
        },
    "captured_today": {
        "type": "map",
        "points_map": {False:-200,True:0}
        },
    "distance": {
        "type": "reverse",
        "points_per_unit": 200/50,
        },
    "active": {
        "type": "cutoff",
        },
    }

calculate_points = None
data = main(name, scrap_urls, ignore_list, distance_from,scrape_file, archive_data_file, print_columns ,calculate_points = calculate_points, scoring_map = scoring_map )
data = analyze_data(name, ignore_list, distance_from, scrape_file, archive_data_file, print_columns, calculate_points = calculate_points, scoring_map = scoring_map)


#message = "#####NEW: \n" +data["new"] +  "\n######TOP 20:\n" + data["top20"]
#send_mail(gmail_user, gmail_password,to, message)
