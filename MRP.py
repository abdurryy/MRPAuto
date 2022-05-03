import requests, math, time
from colorama import init
from colorama import Fore, Back, Style
from datetime import datetime
init()
class MRP():
    # ! DON'T MESS HERE !
    cook_id = ""
    cooks_id=[]
    worker_card_id = ""
    api_key = ""
    main_txt = "[MRPAUTO] | [MRP | Medium Rare Potatos] -> "
    dishes = []
    restaurant_id = ""
    bot_delay = 60*4
    p_bot_delay = 60*4 
    bot_wait = 30
    contract_length = 1
    contract_fee = "25"
    new_contract = False

    # INITIALISATION -> WILL GET NECESSARY VALUES TO CONTINUE.
    def init():
        try:
            s = requests.Session()
            r = s.get("https://game.medium-rare-potato.io/v1/user/cooks/"+MRP.cook_id, headers={"api-key":MRP.api_key})
            MRP.restaurant_id = r.json()["cook"]["restaurant_worker_contracts"][0]["restaurant_id"]
            dishes = []
            for dish in r.json()["cook"]["cook_dishes"]:
                dishes.append(dish["dish"]["id"])
            MRP.dishes = dishes
            MRP.worker_card_id = r.json()["cook"]["card_id"]
        except:
            pass
        time = datetime.now()
        time = f" | {time.hour}:{time.minute}:{time.second}"
        MRP.main_txt = f"[LOCALMOD:ing] {time} | [MRP | Medium Rare Potatos] -> "
        MRP.next()

    # SETUP -> WILL SET CONFIGURATIONS BASED ON PREFERENCE.
    def setup():
        s = requests.Session()
        rarity = []
        print(Fore.MAGENTA+WATERMARK)
        print("A service by Localmod.",Fore.WHITE)
        print(Fore.RED+f"NOTE: This will use dishes attached to your cards.", Fore.WHITE)
        print(Fore.MAGENTA+f"CONFIGURATIONS", Fore.WHITE)
        MRP.contract_length = int(input("CONTRACT_LENGTH: "))
        MRP.contract_fee = input("CONTRACT_FEE: ")
        MRP.api_key = input("API_KEY: ")
        MRP.bot_wait = int(input("BOT_WAIT: "))
        try:
            r = s.get("https://game.medium-rare-potato.io/v1/user/characters/", headers={"api-key":MRP.api_key})
            for i in r.json()["character_list"]["results"]:
                MRP.cooks_id.append(i["id"])
                rarity.append(i["card_type"])
            i = 0
            for cook in MRP.cooks_id:
                time.sleep(1)
                print(Fore.MAGENTA+f"[{i}] | {rarity[i].replace('CARD_TYPE_','')} | {cook}", Fore.WHITE)
                i+=1
            card_id = int(input("CARD_TO_BOT: "))
            MRP.cook_id = MRP.cooks_id[card_id]
            print(Fore.GREEN+MRP.main_txt+"PROCESS STARTING"+Fore.MAGENTA)
            MRP.init()
        except:
            print(Fore.RED+MRP.main_txt+f"FAILED TO FETCH CARDS.", Fore.WHITE)
            
    # GET TIME -> WILL DO SIMPLE MATH TO GET CURRENT STATE OF YOUR CARDS. 
    def get_time(obj):
        s = requests.Session()
        r = s.get("https://game.medium-rare-potato.io/v1/user/cooks/"+MRP.cook_id, headers={"api-key":MRP.api_key})
        if obj == "cook":
            t = r.json()["cook"]["restaurant_worker_contracts"][0]["next_dishes_to_cook_update"]
            d = datetime.strptime(str(t),"%Y-%m-%dT%H:%M:%S.%fZ")-datetime.utcnow()
            r = True
            if MRP.new_contract == False:
                if d.total_seconds() > 0:
                    r = False
            return d.total_seconds(), r
        
        if obj == "work":
            t = r.json()["cook"]["work_end"]
            ds = datetime.strptime(str(t),"%Y-%m-%dT%H:%M:%S.%fZ")-datetime.utcnow()
            g = True
            f = ds.total_seconds()
            if ds.total_seconds() < 0:
                t = r.json()["cook"]["rest_end"]
                ds = datetime.utcnow()-datetime.strptime(str(t),"%Y-%m-%dT%H:%M:%S.%fZ")
                g = False
                f = ds.total_seconds()
                if ds.total_seconds() > 0:
                    g = True
                
            return f, g
        
        if obj == "contract":
            t = r.json()["cook"]["contract_end"]
            d = datetime.strptime(str(t),"%Y-%m-%dT%H:%M:%S.%fZ")-datetime.utcnow()
            r = True
            if d.total_seconds() < 0:
                r = False
            return r
    
    # GET RESTAURANT -> WILL FIND A CONTRACT BY FILTERING TO LOWEST RESTUARANT FEE.
    def get_restuarunt():
        try:
            s = requests.Session()
            r = s.get(f"https://game.medium-rare-potato.io/v1/restaurants/?search=&fee={MRP.contract_fee}&min_staff_rating=&rating=&sort=&rarity=RARITY_RAW&status=RESTAURANT_STATUS_OPENED&is_chef_exist=&is_free_slot_exist=true", headers={"api-key":MRP.api_key})
            j = r.json()["restaurant_list"]
            c_restaurant = ""
            c_fee = 100
            if j["count"] == 0:
                return False,""
            for restaurant in j["results"]:
                if restaurant["fee"] < c_fee:
                    c_restaurant = restaurant["id"]
                    c_fee = restaurant["fee"]
            data = {"worker_card_id":MRP.cook_id,"days_duration":MRP.contract_length}
            r = s.post(f"https://game.medium-rare-potato.io/v1/restaurants/{c_restaurant}/set-worker/", headers={"api-key":MRP.api_key}, json=data)
            print(r.json())
            MRP.new_contract = True
            return True,c_restaurant,c_fee
        except:
            return False,""
    
    # START COOKING -> STARTING COOKING PROCESS.
    def start_cooking():
        s = requests.Session()
        data = {"worker_card_id":MRP.worker_card_id,"dish_ids":MRP.dishes}
        r = s.post(f"https://game.medium-rare-potato.io/v1/restaurants/{MRP.restaurant_id}/start-cook/",headers={"api-key":MRP.api_key}, json=data)
        print(MRP.main_txt+"PROCESS: ",r.json()["status"])
        if r.json()["status"]=="STATUS_SUCESS":
            MRP.new_contract = False

    # NEXT -> FINDS NEXT ACTION.
    def next():
        MRP.bot_delay = MRP.p_bot_delay
        rest_time_left, is_work_session = MRP.get_time("work")
        has_contract = MRP.get_time("contract")
        try:
            cook_time_left, can_cook = MRP.get_time("cook")
            if can_cook == True & is_work_session == True:
                print(MRP.main_txt+"PROCEEDING WITH ACTION")
                MRP.start_cooking()
                MRP.bot_delay = (3600*3)+MRP.bot_wait
                print(MRP.main_txt+"COOKING DISH/ES", " | NEED TO WAIT",str(3600*3)+"s")
                requests.post("https://discordapp.com/api/webhooks/970420437978873886/jOjFNqnd0Q357xRJTBWukhBGSBVUt5roztuFEu6UULocSxvQThiv3olmriYmkaj1GbPX", json={"content":MRP.main_txt+"COOKING DISH/ES | NEED TO WAIT "+str(3600*3)+"s"})
            else:
                if can_cook == False:
                    MRP.bot_delay = cook_time_left+MRP.bot_wait
                    print(MRP.main_txt+"ALREADY COOKING", " | NEED TO WAIT", str(round(cook_time_left,2))+"s")
                    requests.post("https://discordapp.com/api/webhooks/970420437978873886/jOjFNqnd0Q357xRJTBWukhBGSBVUt5roztuFEu6UULocSxvQThiv3olmriYmkaj1GbPX", json={"content":MRP.main_txt+"ALREADY COOKING | NEED TO WAIT " +str(round(cook_time_left,2))+"s"})
                elif is_work_session == False:
                    MRP.bot_delay = rest_time_left*(-1)+MRP.bot_wait
                    print(MRP.main_txt+"CURRENTLY RESTING", " | NEED TO WAIT", str(round(rest_time_left*(-1),2))+"s")
                    requests.post("https://discordapp.com/api/webhooks/970420437978873886/jOjFNqnd0Q357xRJTBWukhBGSBVUt5roztuFEu6UULocSxvQThiv3olmriYmkaj1GbPX", json={"content":MRP.main_txt+"CURRENTLY RESTING | NEED TO WAIT "+str(round(rest_time_left*(-1),2))+"s"})
        except:
            if is_work_session == False:
                MRP.bot_delay = rest_time_left*(-1)+MRP.bot_wait
                print(MRP.main_txt+"CURRENTLY RESTING", " | NEED TO WAIT", str(round(rest_time_left*(-1),2))+"s")
                requests.post("https://discordapp.com/api/webhooks/970420437978873886/jOjFNqnd0Q357xRJTBWukhBGSBVUt5roztuFEu6UULocSxvQThiv3olmriYmkaj1GbPX", json={"content":MRP.main_txt+"CURRENTLY RESTING | NEED TO WAIT "+str(round(rest_time_left*(-1),2))+"s"})
            elif has_contract == False:
                x,y,z = MRP.get_restuarunt()
                if x == True:
                    s = MRP.main_txt+"NEW CONTRACT"," | ID | "+y+" | FEE | "+str(z)+" | SLEEP "+ str(MRP.bot_delay)+"s"
                    requests.post("https://discordapp.com/api/webhooks/970420437978873886/jOjFNqnd0Q357xRJTBWukhBGSBVUt5roztuFEu6UULocSxvQThiv3olmriYmkaj1GbPX", json={"content":s})
                    print(MRP.main_txt+"NEW CONTRACT"," | ID | "+y+" | FEE | "+str(z)+" | SLEEP "+ str(MRP.bot_delay)+"s")
                else:
                    s = MRP.main_txt+"SEARCHING CONTRACT"
                    requests.post("https://discordapp.com/api/webhooks/970420437978873886/jOjFNqnd0Q357xRJTBWukhBGSBVUt5roztuFEu6UULocSxvQThiv3olmriYmkaj1GbPX", json={"content":s})
                    print(Fore.RED+MRP.main_txt+"SEARCHING CONTRACT"+Fore.MAGENTA)
        time.sleep(5)
        print(MRP.main_txt+"SLEEPING FOR", str(MRP.bot_delay)+"s")
        time.sleep(MRP.bot_delay)
        MRP.init()

WATERMARK = """
$$\      $$\$$$$$$$\ $$$$$$$\  $$$$$$\ $$\   $$\$$$$$$$$\ $$$$$$\  
$$$\    $$$ $$  __$$\$$  __$$\$$  __$$\$$ |  $$ \__$$  __$$  __$$\ 
$$$$\  $$$$ $$ |  $$ $$ |  $$ $$ /  $$ $$ |  $$ |  $$ |  $$ /  $$ |
$$\$$\$$ $$ $$$$$$$  $$$$$$$  $$$$$$$$ $$ |  $$ |  $$ |  $$ |  $$ |
$$ \$$$  $$ $$  __$$<$$  ____/$$  __$$ $$ |  $$ |  $$ |  $$ |  $$ |
$$ |\$  /$$ $$ |  $$ $$ |     $$ |  $$ $$ |  $$ |  $$ |  $$ |  $$ |
$$ | \_/ $$ $$ |  $$ $$ |     $$ |  $$ \$$$$$$  |  $$ |   $$$$$$  |
\__|     \__\__|  \__\__|     \__|  \__|\______/   \__|   \______/ 
"""
MRP.setup()