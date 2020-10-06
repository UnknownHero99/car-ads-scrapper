from run import main,analyze_data, send_mail
import smtplib

gmail_user = "mail_for_sending@gmail.com"
gmail_password = "password"
to = ["mail1@gmail.com", "mail2@email.com"]

name = "example_rent"
scrap_urls = ["https://www.avto.net/Ads/results.asp?znamka=%8Akoda&model=&modelID=&tip=katerikoli%20tip&znamka2=&model2=&tip2=katerikoli%20tip&znamka3=&model3=&tip3=katerikoli%20tip&cenaMin=0&cenaMax=999999&letnikMin=0&letnikMax=2090&bencin=0&starost2=999&oblika=0&ccmMin=0&ccmMax=99999&mocMin=&mocMax=&kmMin=0&kmMax=9999999&kwMin=0&kwMax=999&motortakt=&motorvalji=&lokacija=0&sirina=&dolzina=&dolzinaMIN=&dolzinaMAX=&nosilnostMIN=&nosilnostMAX=&lezisc=&presek=&premer=&col=&vijakov=&EToznaka=&vozilo=&airbag=&barva=&barvaint=&EQ1=1000000000&EQ2=1000000000&EQ3=1000000000&EQ4=100000000&EQ5=1000000000&EQ6=1000000000&EQ7=1000000120&EQ8=1010000001&EQ9=100000000&KAT=1010000000&PIA=&PIAzero=&PSLO=&akcija=&paketgarancije=&broker=&prikazkategorije=&kategorija=&zaloga=&arhiv=&presort=&tipsort=&stran="]
distance_from = "Kongresni trg, Ljubljana, Slovenija"
ignore_list = ["oddamo sob","oddam sob","oddaja se sob", "oddajam sobo", "študentsko sobo", "oddaja se postelj","oddaja postelj","oddamo postelj", "oddamo dvoposteljno", "souporab","delit", "skupno", "že stanuje", "oddamo posteljo", "postelji oddamo", "https://www.nepremicnine.net/oglasi-oddaja/lj-siska-stanovanje_6360581/", "https://www.nepremicnine.net/oglasi-oddaja/jezica-bezigrad-ruski-car-stanovanje_6359280/", "https://www.nepremicnine.net/oglasi-oddaja/lj-vic-sibeniska-ulica-5-stanovanje_6309122/", "https://www.nepremicnine.net/oglasi-oddaja/lj-vic-rozna-dolina-stanovanje_6203756/", "https://www.nepremicnine.net/oglasi-oddaja/lj-moste-stanovanje_6323521/","https://www.nepremicnine.net/oglasi-oddaja/lj-vic-stanovanje_6359292/"]
scrape_file = "scraped_data/" + name + ".csv"
archive_data_file = "archive_data/" + name + ".csv"
print_columns = ["points", "location", "price", "size", "distance", "captured_today", "url"]


def calculate_points(Ad):
    if not Ad["active"]:
        return 0
    if not Ad["captured_today"]:
        old = -50
    else:
        old = 0

    # if Ad['size'] < 10:
    #     size_points = 0
    # elif Ad['size'] < 20:
    #     size_points = 30
    # elif Ad['size'] < 30:
    #     size_points = 60
    # elif Ad['size'] < 50:
    #     size_points = 70
    # elif Ad['size'] < 60:
    #     size_points = 80
    # else:
    #     size_points = 0

    if Ad["price"] < 100:
        price_points = 100
    elif Ad["price"] < 150:
        price_points = 200
    elif Ad["price"] < 200:
        price_points = 150
    elif Ad["price"] < 250:
        price_points = 100
    elif Ad["price"] < 300:
        price_points = 50
    elif Ad["price"] < 350:
        price_points = 30
    elif Ad["price"] < 400:
        price_points = 10
    else:
        price_points = 0

    if Ad['distance'] ==  -1:
        distance_points = 20
    elif Ad['distance'] < 1:
        distance_points = 70
    elif Ad['distance'] < 2:
        distance_points = 100
    elif Ad['distance'] < 3:
        distance_points = 80
    elif Ad['distance'] < 4:
        distance_points = 60
    elif Ad['distance'] < 5:
        distance_points = 40
    else:
        distance_points = 0

    return distance_points + price_points + old



data = main(name, scrap_urls, ignore_list, calculate_points, distance_from,scrape_file, archive_data_file, print_columns )
message = "#####NEW: \n" +data["new"] +  "\n######TOP 20:\n" + data["top20"]
send_mail(gmail_user, gmail_password,to, message)
