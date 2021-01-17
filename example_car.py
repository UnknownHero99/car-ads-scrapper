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



#what is the expected range of values -> for normalization
value_ranges = {"price": [2000,3500],"manufacturing_year": [2007,2015],"kilometrage": [100000,250000]}
# how many points do we want one unit to give -> points more this will be based entirely on the value_ranges -Y if they are incorect this will be too.
points_evaluation = {"price": 1, "manufacturing_year": 200, "kilometrage": 50/10000}
# this means 1 € cheaper is 1 point, 1 year younger is 200 points more and 10000 kilometers less is 50 points more

points_reversal = {"price":True, "manufacturing_year":False, "kilometrage":True}# if true less is better

def normalize(value, value_range):
    return (value - value_range[0]) / (value_range[1] - value_range[0])

def reverse_value(value):
    return 1 - value

def get_points(value, value_range, points_per_unit, reverse = False):
    points = normalize(value,value_range)
    if reverse:
        points = reverse_value(points)
    points =  points * (value_range[1] - value_range[0]) * points_per_unit
    #print("Points: {}, value: {}, range: {}".format(points, value, str(value_range)))
    if points < 0:
        return 0
    return points

def calculate_points(Ad):
    points = 0
    if Ad["is_dealership"]:
        points += 200
    if Ad["vin"]:
        points += 200

    for c in value_ranges:
        i = 0
        if points_reversal[c]:
            i = 1
        points += get_points(Ad.get(c,value_ranges[c][1]),value_ranges[c], points_evaluation[c], points_reversal[c])

    if Ad.get("distance",60) > 50:
        points += -20

    if Ad["manufacturer"].lower() in ("chevrolet","citroen") or Ad["model"].lower() in ("clio", "getz", "megane","207","modus","107","i10","aygo","colt", "fiesta","grand modus"):
        points += -1500

    if Ad["manufacturer"].lower() in ("") or Ad["model"].lower() in ("ceed","i30"):
        points += 750


    if not Ad["captured_today"]:
        old = -50
    else:
        old = 0

    if not Ad["active"]:
        points -= 5000

    return points

calculate_points = None
data = main(name, scrap_urls, ignore_list, distance_from,scrape_file, archive_data_file, print_columns ,calculate_points = calculate_points, scoring_map = scoring_map )
data = analyze_data(name, ignore_list, distance_from, scrape_file, archive_data_file, print_columns, calculate_points = calculate_points, scoring_map = scoring_map)


#message = "#####NEW: \n" +data["new"] +  "\n######TOP 20:\n" + data["top20"]
#send_mail(gmail_user, gmail_password,to, message)
