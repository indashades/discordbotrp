import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import json
import time
import threading
from datetime import datetime
import re
import asyncio
from ka import keep_alive




try:
    def economy_loop():
        last_run = 16

        while True:
            now = datetime.now()
            print("uhhh...", now.hour)
            if now.hour in [2, 6, 10, 14, 18, 22]: #server-[2, 6, 10, 14, 18, 22]: me-[0, 4, 8, 12, 16, 20]
                slot = now.hour
                print("now in slot: ", slot)

                if slot != last_run:
                    countries = []
                    with open("countries.json", "r") as f:
                        countries = json.load(f)
                    for  nam in countries:
                        nam["money"]=nam["money"]+nam["gra+"]+nam["pop"]*(((50/1)*nam["tax"])/(nam["food+"]+nam["lux+"]+nam["timber+"]+nam["stone+"]+nam["nobleMetals+"]+nam["strategicMetals+"])) #1 was nam["moncon"] but now tax is debuffed
                        nam["pop"]=nam["pop"]*nam["pop+"]
                        nam["food"]=nam["food"]+nam["food+"]
                        nam["lux"]=nam["lux"]+nam["lux+"]
                        nam["timber"]=nam["timber"]+nam["timber+"]
                        nam["stone"]=nam["stone"]+nam["stone+"]
                        nam["nobleMetals"]=nam["nobleMetals"]+nam["nobleMetals+"]
                        nam["strategicMetals"]=nam["strategicMetals"]+nam["strategicMetals+"]
                        nam["livestock"]=nam["livestock"]*nam["pop+"]
                        nam["rideAnimals"]=nam["rideAnimals"]*nam["pop+"]
                        if nam["food"]<0:
                            nam["pop+"]=0.9
                            nam["food"]=0

                        if nam["pop+"]<=1.001:
                            nam["pop+"]=nam["pop+"]+0.002+(((nam["lux"]+nam["food"])/nam["pop"]) ** 0.5) * 0.01#(((nam["lux"]+nam["food"])/1000)/10000)
                        elif nam["pop+"]>1.001:
                            nam["pop+"]=nam["pop+"]-0.002+(((nam["lux"]+nam["food"])/nam["pop"]) ** 0.5) * 0.01#(((nam["lux"]+nam["food"])/1000)/10000)
                        if nam["pop+"]>1.3:
                            nam["pop+"]=nam["pop+"]-0.05
                    m="time progressed!"
                    print(m)
                    

                    with open("temp.txt", "w") as f:
                        json.dump(countries, f, indent=4)

                    os.replace("temp.txt", "countries.json")
                    #!progressTimeNow
                    last_run = slot

            time.sleep(120)

    # start background thread
    thread = threading.Thread(target=economy_loop)
    thread.start()
except Exception as e:
            print("🔥 THREAD CRASH:", repr(e))
            time.sleep(5)



keep_alive()



load_dotenv()
token=os.getenv("DT")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)



@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

tradevar1=0
tradevar2=0
p1=""
p2=""
trade1=""
trade2=""
z=()

countries = []



#save
#with open("countries.json", "w") as f:
#    json.dump(countries, f, indent=4)

#load
with open("countries.json", "r") as f:
    countries = json.load(f)


    


@bot.event
async def on_message(msg):
    if msg.author.id != bot.user.id and msg.content.startswith('!'):
        try:

            
            if "!y" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                with open("trade.json", "r") as f:
                    trade = json.load(f)

                p1 = trade["from"]          # sender country
                p2 = trade["to"]            # receiver country

                tradevar1 = float(trade["send_amount"])
                trade1 = trade["send_item"]

                tradevar2 = float(trade["receive_amount"])
                trade2 = trade["receive_item"]

                if msg.author.display_name == p2:

                    sender = None
                    receiver = None

                    # Find both countries
                    for country in countries:
                        if country["name"] == p1:
                            sender = country
                        elif country["name"] == p2:
                            receiver = country

                    if sender and receiver:

                        # ---- Sender gives item ----
                        if trade1 == "money":

                            # remove sender money
                            sender["money"] -= tradevar1

                            # convert sender currency -> base -> receiver currency
                            base_value = tradevar1 * sender["moncon"]
                            converted_money = base_value / receiver["moncon"]

                            receiver["money"] += converted_money

                        else:
                            sender[trade1] -= tradevar1
                            receiver[trade1] += tradevar1

                        # ---- Receiver gives item ----
                        if trade2 == "money":

                            # remove receiver money
                            receiver["money"] -= tradevar2

                            # convert receiver currency -> base -> sender currency
                            base_value = tradevar2 * receiver["moncon"]
                            converted_money = base_value / sender["moncon"]

                            sender["money"] += converted_money

                        else:
                            receiver[trade2] -= tradevar2
                            sender[trade2] += tradevar2

                        m = "trade accepted"
                        await msg.channel.send(m)
                        with open("countries.json", "w") as f:
                            json.dump(countries, f, indent=4)

            if "!n" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                m="trade denied"
                await msg.channel.send(m)


            
            if "!expand" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"]:
                        nam["food"]=nam["food"]-2000
                        nam["food+"]=nam["food+"]+50
                        nam["strategicMetals+"]=nam["strategicMetals+"]+10

                        with open("countries.json", "w") as f:
                            json.dump(countries, f, indent=4)
                        await msg.channel.send("you expanded succesfully probably")

            #tech things
            #addTech name: name, foodcost: value, moneycost: value, luxurycost: value, timbercost: value, stonecost: value, valuableMetalcost: value, strategicMetalcost: value --- foodproduction: value, moneyproduction: value, luxuryproduction: value, timberproduction: value, stoneproduction: value, valuableMetalproduction: value, strategicMetalproduction: value, techId: id, role: role
            if "!addTech" in msg.content and any(role.name == "Collaborators" for role in msg.author.roles): #add and progress time need the correct roles
                ##splits=msg.content.split(" name: ",", foodcost: ",", moneycost: ",", luxurycost: ",", timbercost: ",", stonecost: ",", valuableMetalcost: ",", strategicMetalcost: "," --- foodproduction: ",", moneyproduction: ",", luxuryproduction: "+", timberproduction: "+", stoneproduction: "+", valuableMetalproduction: ",", strategicMetalproduction: ",", techId: ",", role: ")
                
                splits = re.split(
                    r'name: |, foodcost: |, moneycost: |, luxurycost: |, timbercost: |, stonecost: |, valuableMetalcost: |, strategicMetalcost: | --- foodproduction: |, moneyproduction: |, luxuryproduction: |, timberproduction: |, stoneproduction: |, valuableMetalproduction: |, strategicMetalproduction: |, techId: |, role: ',
                    msg.content
                    
                )
                print(splits)
                text = '''if "!'''+splits[1]+'''" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"] and nam["t'''+splits[16]+'''"]==0 and any(role.name == "'''+splits[17]+'''" for role in msg.author.roles):
                        if nam["food"]>='''+splits[2]+''' and nam["money"]>='''+splits[3]+''' and nam["lux"]>='''+splits[4]+''' and nam["timber"]>='''+''' and nam["stone"]>='''+splits[5]+''' and nam["nobleMetals"]>='''+splits[6]+''' and nam["strategicMetals"]>='''+splits[7]+''':
                            nam["food"]=nam["food"]-'''+splits[2]+'''
                            nam["money"]=nam["money"]-'''+splits[3]+'''
                            nam["lux"]=nam["lux"]-'''+splits[4]+'''
                            nam["timber"]=nam["timber"]-'''+splits[5]+'''
                            nam["stone"]=nam["stone"]-'''+splits[6]+'''
                            nam["nobleMetals"]=nam["nobleMetals"]-'''+splits[7]+'''
                            nam["strategicMetals"]=nam["strategicMetals"]-'''+splits[8]+'''
                            nam["food+"]=nam["food+"]+'''+splits[9]+'''
                            nam["gra+"]=nam["gra+"]+'''+splits[10]+'''
                            nam["lux+"]=nam["lux+"]+'''+splits[11]+'''
                            nam["timber+"]=nam["timber+"]+'''+splits[12]+'''
                            nam["stone+"]=nam["stone+"]+'''+splits[13]+'''
                            nam["nobleMetals+"]=nam["nobleMetals+"]+'''+splits[14]+'''
                            nam["strategicMetals+"]=nam["strategicMetals+"]+'''+splits[15]+'''
                            nam["t'''+splits[16]+'''"]='''+splits[16]+'''
                            await msg.channel.send("crop rotation researched!")
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
                        else:
                            await msg.channel.send("you cannot afford that!")'''

                with open("output.txt", "a", encoding="utf-8") as f:
                    f.write(text + "\n\n")
                    '''
                    "money": float(parts[2]), #name of money/treasury
                "gra+": float(0), #money that goes +
                "moncon": float(parts[19]), #currency exchange rate
                "pop": float(parts[3]), #population
                "pop+": float(parts[4]), #pop modifer
                "food": float(parts[5]), #food stockpile
                "food+": float(parts[6]), #food production
                "lux": float(parts[7]), #luxury goods
                "lux+": float(parts[8]), #lux production
                "timber": float(parts[9]), #timber stockpile
                "timber+": float(parts[10]), #timber production
                "stone": float(parts[11]), #stone stockpile
                "stone+": float(parts[12]), #stone production
                "nobleMetals": float(parts[13]), #gold/silver stockpile
                "nobleMetals+": float(parts[14]), #gold/silver mining
                "strategicMetals": float(parts[15]), #brass/copper/bronze/iron
                "strategicMetals+": float(parts[16]), #iron/copper etc mining
                "livestock": float(parts[17]), #livestock (pretty useless right now)
                "rideAnimals"
                '''

            if "!tech" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                await msg.channel.send("technologies that can be researched are: \n"
                                       +"!cropRotation - costs: 10k food, earns: +500 food production\n"+
                                       "!aqueducts - costs: 10k money and 500 stone, earns: +200 food production\n"+
                                       "!roads - costs: 10k stone, 10k money and 10k timber, earns: +500 income x currencyValue money from road tolls\n"+
                                       "!metallurgy - costs 10k money, 5k precious metals and 15k strategic metals earns: +500 strategic metals production \n"+
                                       "!standardizedTaxation - costs: 100k money and 10k precious metals earns: +1k income x currencyValue  \n"+
                                       "!smallIrrigation - costs: 12k money and 6k stone, earns: +250 food production \n"+
                                       "!basicLogging - costs: 10k money and 3k strategic metals, earns: +200 timber production\n"+
                                       "!smallQuarries - costs: 10k money, 3k timber and 3k strategic metals, earns: +200 stone production\n"+
                                       "!simpleSmelting - costs: 10k money, 5k strategic metals and 2k precious metals, earns: +200 strategic metals production\n"+
                                       "!smallMarket - costs: 10k money, 5k stone and 3k timber, earns: +2k income x currencyValue \n"+
                                       "!basicWinePress - costs: 12k money, 5k food and 3k timber, earns: +200 luxury goods production\n"+
                                       "!simpleOilPress - costs: 10k money, 3k timber and 3k luxury goods, earns: +150 luxury goods production \n"+
                                       "!dirtRoads - costs: 10k money, 5k stone and 5k timber, earns: +300 income x currencyValue treasury\n"
                                        "coming soon: \n"+
                                       "!horseTraining - costs: 10k money, 3k food and 2k livestock, earns: +15 ride animals production\n"
                                       )
                
            if "!cropRotation" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"] and nam["t1"]==0:
                        if nam["food"]>=10000:
                            nam["food"]=nam["food"]-10000
                            nam["food+"]=nam["food+"]+500
                            nam["t1"]=1
                            await msg.channel.send("crop rotation researched!")
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
                        else:
                            await msg.channel.send("you cannot afford that!")
            if "!aqueducts" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"] and nam["t2"]==0:
                        if nam["money"]>=10000 and nam["stone"]>=500:
                            nam["money"]=nam["money"]-10000
                            nam["stone"]=nam["stone"]-500
                            nam["food+"]=nam["food+"]+200
                            nam["t2"]=1
                            await msg.channel.send("aqueducts researched!")
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
                        else:
                            await msg.channel.send("you cannot afford that!")
            if "!roads" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"] and nam["t3"]==0:
                        if nam["money"]>=10000 and nam["stone"]>=10000 and nam["timber"]>=10000:
                            nam["money"]=nam["money"]-10000
                            nam["stone"]=nam["stone"]-10000
                            nam["timber"]=nam["timber"]-10000
                            nam["gra+"]=nam["gra+"]+500*nam["moncon"]
                            nam["t3"]=1
                            await msg.channel.send("roads researched!")
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
                        else:
                            await msg.channel.send("you cannot afford that!")
            if "!metallurgy" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"] and nam["t4"]==0:
                        if nam["money"]>=10000 and nam["nobleMetals"]>=5000 and nam["timber"]>=15000:
                            nam["money"]=nam["money"]-10000
                            nam["nobleMetals"]=nam["nobleMetals"]-5000
                            nam["strategicMetals"]=nam["strategicMetals"]-15000
                            nam["strategicMetals+"]=nam["strategicMetals+"]+500
                            nam["t4"]=1
                            await msg.channel.send("metallurgy researched!")
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
                        else:
                            await msg.channel.send("you cannot afford that!")
            if "!standardizedTaxation" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"] and nam["t5"]==0:
                        if nam["money"]>=100000 and nam["nobleMetals"]>=10000:
                            nam["money"]=nam["money"]-100000
                            nam["nobleMetals"]=nam["nobleMetals"]-10000
                            nam["gra+"]=nam["gra+"]+500*nam["moncon"]
                            nam["t5"]=1
                            await msg.channel.send("standardized taxation researched!")
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
                        else:
                            await msg.channel.send("you cannot afford that!")
            if "!smallIrrigation" in msg.content: #costs: 12k money and 6k stone, earns: +250 food production
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"] and nam["t6"]==0:
                        if nam["money"]>=12000 and nam["stone"]>=6000:
                            nam["money"]=nam["money"]-12000
                            nam["stone"]=nam["stone"]-6000
                            nam["food+"]=nam["food+"]+250
                            nam["t6"]=1
                            await msg.channel.send("small irrigation researched!")
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
                        else:
                            await msg.channel.send("you cannot afford that!")
            #!basicLogging - costs: 10k money and 3k strategic metals, earns: +200 timber production\n
            if "!basicLogging" in msg.content: 
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"] and nam["t7"]==0:
                        if nam["money"]>=10000 and nam["strategicMetals"]>=3000:
                            nam["money"]=nam["money"]-10000
                            nam["strategicMetals"]=nam["strategicMetals"]-3000
                            nam["timber+"]=nam["timber+"]+200
                            nam["t7"]=1
                            await msg.channel.send("basic logging researched!")
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
                        else:
                            await msg.channel.send("you cannot afford that!")
            #"!smallQuarries - costs: 10k money, 3k timber and 3k strategic metals, earns: +200 stone production\n"+
            if "!smallQuarries" in msg.content: 
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"] and nam["t8"]==0:
                        if nam["money"]>=10000 and nam["strategicMetals"]>=3000 and nam["timber"]>=3000:
                            nam["money"]=nam["money"]-10000
                            nam["strategicMetals"]=nam["strategicMetals"]-3000
                            nam["timber"]=nam["timber"]-3000
                            nam["stone+"]=nam["stone+"]+200
                            nam["t8"]=1
                            await msg.channel.send("small quarries researched!")
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
                        else:
                            await msg.channel.send("you cannot afford that!")
            #"!simpleSmelting - costs: 10k money, 5k strategic metals and 2k precious metals, earns: +200 strategic metals production\n"+
            if "!simpleSmelting" in msg.content: 
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"] and nam["t9"]==0:
                        if nam["money"]>=10000 and nam["strategicMetals"]>=5000 and nam["nobleMetals"]>=2000:
                            nam["money"]=nam["money"]-10000
                            nam["strategicMetals"]=nam["strategicMetals"]-5000
                            nam["nobleMetals"]=nam["nobleMetals"]-2000
                            nam["strategicMetals+"]=nam["strategicMetals+"]+200
                            nam["t9"]=1
                            await msg.channel.send("simple smelting researched!")
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
                        else:
                            await msg.channel.send("you cannot afford that!")
            #"!smallMarket - costs: 10k money, 5k stone and 3k timber, earns: +2000 treasury income\n"+
            if "!smallMarket" in msg.content: 
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"] and nam["t10"]==0:
                        if nam["money"]>=10000 and nam["stone"]>=5000 and nam["timber"]>=3000:
                            nam["money"]=nam["money"]-10000
                            nam["stone"]=nam["stone"]-5000
                            nam["timber"]=nam["timber"]-3000
                            nam["gra+"]=nam["gra+"]+2000*nam["moncon"]
                            nam["t10"]=1
                            await msg.channel.send("small markets researched!")
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
                        else:
                            await msg.channel.send("you cannot afford that!")
            #"!basicWinePress - costs: 12k money, 5k food and 3k timber, earns: +200 luxury goods production\n"+
            if "!basicWinePress" in msg.content: 
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"] and nam["t11"]==0:
                        if nam["money"]>=12000 and nam["food"]>=5000 and nam["timber"]>=3000:
                            nam["money"]=nam["money"]-12000
                            nam["food"]=nam["food"]-5000
                            nam["timber"]=nam["timber"]-3000
                            nam["lux+"]=nam["lux+"]+200
                            nam["t11"]=1
                            await msg.channel.send("basic wine press researched!")
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
                        else:
                            await msg.channel.send("you cannot afford that!")
            #"!simpleOilPress - costs: 10k money, 3k timber and 3k luxury goods, earns: +150 luxury goods production \n"+
            if "!simpleOilPress" in msg.content: 
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"] and nam["t12"]==0:
                        if nam["money"]>=10000 and nam["lux"]>=3000 and nam["timber"]>=3000:
                            nam["money"]=nam["money"]-10000
                            nam["lux"]=nam["lux"]-3000
                            nam["timber"]=nam["timber"]-3000
                            nam["lux+"]=nam["lux+"]+150
                            nam["t12"]=1
                            await msg.channel.send("simple Oil Press researched!")
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
                        else:
                            await msg.channel.send("you cannot afford that!")
            #"!dirtRoads - costs: 10k money, 5k stone and 5k timber, earns: +150 treasury income\n")
            if "!dirtRoads" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"] and nam["t13"]==0:
                        if nam["money"]>=10000 and nam["stone"]>=5000 and nam["timber"]>=5000:
                            nam["money"]=nam["money"]-10000
                            nam["stone"]=nam["stone"]-5000
                            nam["timber"]=nam["timber"]-5000
                            nam["gra+"]=nam["gra+"]+300*nam["moncon"]
                            nam["t13"]=1
                            await msg.channel.send("roads researched!")
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
                        else:
                            await msg.channel.send("you cannot afford that!")
            





            if "!resources" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                await msg.channel.send("here is a list explaining all the resources: \ntreasury/money = money in the form of your national currency keep currency exchange rates in mind when trading using these \npop/population = the amount of citizens you have in your nation \n"
                +"food = the stockpiles of what your population consumes to survive \nlux/luxury goods = the luxury goods like sugar, tobacco, honey etc that no one really needs but everyone still wants. These are vital for your nation to prosper \n"
                +"timber = your stockpiles of wood which is useful for fortifying and building ships \n stone = your stockpile of stone used for building walled cities, castles and forts \n"
                +"nobleMetals/precious metals = the valuable metals like gold and silver. The measure of prosperity is how much gold you have \nstrategicMetals/strategic metals = the other metals like iron, copper and bronze\n"
                +"livestock = domesticated animals like goats or cows. These keep your population fed and are good for trading probably \nrideAnimals/ride animals = camels, horses and elephants. These are useful for wars mainly\n"
                +"---\nthe + at the end of your economy signify the amount you will be gaining in the upcoming timeskip")




            #here the players select what to mobilize, these are mobilized only next timeskip
            if "!mob" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"]:


                        nam["us"] = "mobMenu"
                        with open("countries.json", "w") as f:
                            json.dump(countries, f, indent=4)

                        await msg.channel.send(
                            "mobilization menu:\n"
                            "write !1 to: mobilize hoplites\n"
                            "write !2 to: mobilize war elephants\n"
                            "write !3 to: mobilize slingers\n"
                            "write !4 to: mobilize archers\n"
                            "write !5 to: mobilize militia\n"
                            "write !6 to: mobilize horse archers\n"
                            "write !7 to: mobilize light cavalry\n"
                            "write !8 to: mobilize mercenary cavalry\n"
                            "write !9 to: mobilize mercenary infantery\n"
                            "write !10 to: build triemes\n"
                            "write !11 to: build war canoes \n"
                            "write !12 to: build patrol boats \n"
                            "write !13 to: build longships \n"
                        )
                        '''
                        ARMY
                        hoplites - 0.7m
                        warel - 15.0m
                        sling - 0.4r
                        arch - 0.7r
                        milit - 0.5m
                        harch - 0.9r
                        ligcav - 1.0m
                        merccav - 1.2m
                        mercinf - 0.8m
                        NAVY
                        triemes - 1.0a - 1.0d
                        canoes - 0.1a - 0.2d
                        patrol - 0.1a - 0.9d
                        longships - 2.0a - 0.5d
                        '''
            if "!1" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"]:
                        if nam["us"]=="mobMenu":
                            await msg.channel.send("how many?")
                            nam["us"]="hoplitemob"
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
            if msg.content.replace("!", "").isdigit():
                with open("countries.json", "r") as f:
                        countries = json.load(f)
                for  nam in countries:
                    if nam["us"] == "hoplitemob":

                        try:
                            amount = int(msg.content.replace("!", ""))
                        except:
                            await msg.channel.send("Write !number")
                            return
                        with open("countries.json", "r") as f:
                            countries = json.load(f)
                        for  nam in countries:
                            if msg.author.display_name==nam["name"]:
                                nam["hoplites+"]+=amount
                        nam["us"] = ""
                        with open("countries.json", "w") as f:
                                    json.dump(countries, f, indent=4)
            if "!2" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"]:
                        if nam["us"]=="mobMenu":
                            await msg.channel.send("how many?")
                            nam["us"]="warelmob"
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
            if msg.content.replace("!", "").isdigit():
                with open("countries.json", "r") as f:
                        countries = json.load(f)
                for  nam in countries:
                    if nam["us"] == "warelmob":

                        try:
                            amount = int(msg.content.replace("!", ""))
                        except:
                            await msg.channel.send("Write !number")
                            return
                        with open("countries.json", "r") as f:
                            countries = json.load(f)
                        for  nam in countries:
                            if msg.author.display_name==nam["name"]:
                                nam["warel+"]+=amount
                        nam["us"] = ""
                        with open("countries.json", "w") as f:
                                    json.dump(countries, f, indent=4)
            if "!3" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"]:
                        if nam["us"]=="mobMenu":
                            await msg.channel.send("how many?")
                            nam["us"]="slingmob"
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
            if msg.content.replace("!", "").isdigit():
                with open("countries.json", "r") as f:
                        countries = json.load(f)
                for  nam in countries:
                    if nam["us"] == "slingmob":

                        try:
                            amount = int(msg.content.replace("!", ""))
                        except:
                            await msg.channel.send("Write !number")
                            return
                        with open("countries.json", "r") as f:
                            countries = json.load(f)
                        for  nam in countries:
                            if msg.author.display_name==nam["name"]:
                                nam["sling+"]+=amount
                        nam["us"] = ""
                        with open("countries.json", "w") as f:
                                    json.dump(countries, f, indent=4)
            if "!4" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"]:
                        if nam["us"]=="mobMenu":
                            await msg.channel.send("how many?")
                            nam["us"]="archmob"
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
            if msg.content.replace("!", "").isdigit():
                with open("countries.json", "r") as f:
                        countries = json.load(f)
                for  nam in countries:
                    if nam["us"] == "archmob":

                        try:
                            amount = int(msg.content.replace("!", ""))
                        except:
                            await msg.channel.send("Write !number")
                            return
                        with open("countries.json", "r") as f:
                            countries = json.load(f)
                        for  nam in countries:
                            if msg.author.display_name==nam["name"]:
                                nam["arch+"]+=amount
                        nam["us"] = ""
                        with open("countries.json", "w") as f:
                                    json.dump(countries, f, indent=4)
            if "!5" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"]:
                        if nam["us"]=="mobMenu":
                            await msg.channel.send("how many?")
                            nam["us"]="milmob"
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
            if msg.content.replace("!", "").isdigit():
                with open("countries.json", "r") as f:
                        countries = json.load(f)
                for  nam in countries:
                    if nam["us"] == "milmob":

                        try:
                            amount = int(msg.content.replace("!", ""))
                        except:
                            await msg.channel.send("Write !number")
                            return
                        with open("countries.json", "r") as f:
                            countries = json.load(f)
                        for  nam in countries:
                            if msg.author.display_name==nam["name"]:
                                nam["milit+"]+=amount
                        nam["us"] = ""
                        with open("countries.json", "w") as f:
                                    json.dump(countries, f, indent=4)
            if "!6" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"]:
                        if nam["us"]=="mobMenu":
                            await msg.channel.send("how many?")
                            nam["us"]="harchmob"
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
            if msg.content.replace("!", "").isdigit():
                with open("countries.json", "r") as f:
                        countries = json.load(f)
                for  nam in countries:
                    if nam["us"] == "harchmob":

                        try:
                            amount = int(msg.content.replace("!", ""))
                        except:
                            await msg.channel.send("Write !number")
                            return
                        with open("countries.json", "r") as f:
                            countries = json.load(f)
                        for  nam in countries:
                            if msg.author.display_name==nam["name"]:
                                nam["harch+"]+=amount
                        nam["us"] = ""
                        with open("countries.json", "w") as f:
                                    json.dump(countries, f, indent=4)
            if "!7" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"]:
                        if nam["us"]=="mobMenu":
                            await msg.channel.send("how many?")
                            nam["us"]="ligcavmob"
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
            if msg.content.replace("!", "").isdigit():
                with open("countries.json", "r") as f:
                        countries = json.load(f)
                for  nam in countries:
                    if nam["us"] == "ligcavmob":

                        try:
                            amount = int(msg.content.replace("!", ""))
                        except:
                            await msg.channel.send("Write !number")
                            return
                        with open("countries.json", "r") as f:
                            countries = json.load(f)
                        for  nam in countries:
                            if msg.author.display_name==nam["name"]:
                                nam["ligcav+"]+=amount
                        nam["us"] = ""
                        with open("countries.json", "w") as f:
                                    json.dump(countries, f, indent=4)
            if "!8" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"]:
                        if nam["us"]=="mobMenu":
                            await msg.channel.send("how many?")
                            nam["us"]="merccavmob"
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
            if msg.content.replace("!", "").isdigit():
                with open("countries.json", "r") as f:
                        countries = json.load(f)
                for  nam in countries:
                    if nam["us"] == "merccavmob":

                        try:
                            amount = int(msg.content.replace("!", ""))
                        except:
                            await msg.channel.send("Write !number")
                            return
                        with open("countries.json", "r") as f:
                            countries = json.load(f)
                        for  nam in countries:
                            if msg.author.display_name==nam["name"]:
                                nam["merccav+"]+=amount
                        nam["us"] = ""
                        with open("countries.json", "w") as f:
                                    json.dump(countries, f, indent=4)
            if "!9" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"]:
                        if nam["us"]=="mobMenu":
                            await msg.channel.send("how many?")
                            nam["us"]="mercinfmob"
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
            if msg.content.replace("!", "").isdigit():
                with open("countries.json", "r") as f:
                        countries = json.load(f)
                for  nam in countries:
                    if nam["us"] == "mercinfmob":

                        try:
                            amount = int(msg.content.replace("!", ""))
                        except:
                            await msg.channel.send("Write !number")
                            return
                        with open("countries.json", "r") as f:
                            countries = json.load(f)
                        for  nam in countries:
                            if msg.author.display_name==nam["name"]:
                                nam["mercinf+"]+=amount
                        nam["us"] = ""
                        with open("countries.json", "w") as f:
                                    json.dump(countries, f, indent=4)
            if "!10" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"]:
                        if nam["us"]=="mobMenu":
                            await msg.channel.send("how many?")
                            nam["us"]="btriemes"
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
            if msg.content.replace("!", "").isdigit():
                with open("countries.json", "r") as f:
                        countries = json.load(f)
                for  nam in countries:
                    if nam["us"] == "btriemes":

                        try:
                            amount = int(msg.content.replace("!", ""))
                        except:
                            await msg.channel.send("Write !number")
                            return
                        with open("countries.json", "r") as f:
                            countries = json.load(f)
                        for  nam in countries:
                            if msg.author.display_name==nam["name"]:
                                nam["triemes+"]+=amount
                        nam["us"] = ""
                        with open("countries.json", "w") as f:
                                    json.dump(countries, f, indent=4)
            if "!11" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"]:
                        if nam["us"]=="mobMenu":
                            await msg.channel.send("how many?")
                            nam["us"]="bcanoes"
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
            if msg.content.replace("!", "").isdigit():
                with open("countries.json", "r") as f:
                        countries = json.load(f)
                for  nam in countries:
                    if nam["us"] == "bcanoes":

                        try:
                            amount = int(msg.content.replace("!", ""))
                        except:
                            await msg.channel.send("Write !number")
                            return
                        with open("countries.json", "r") as f:
                            countries = json.load(f)
                        for  nam in countries:
                            if msg.author.display_name==nam["name"]:
                                nam["canoes+"]+=amount
                        nam["us"] = ""
                        with open("countries.json", "w") as f:
                                    json.dump(countries, f, indent=4)
            if "!12" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"]:
                        if nam["us"]=="mobMenu":
                            await msg.channel.send("how many?")
                            nam["us"]="bpatrol"
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
            if msg.content.replace("!", "").isdigit():
                with open("countries.json", "r") as f:
                        countries = json.load(f)
                for  nam in countries:
                    if nam["us"] == "bpatrol":

                        try:
                            amount = int(msg.content.replace("!", ""))
                        except:
                            await msg.channel.send("Write !number")
                            return
                        with open("countries.json", "r") as f:
                            countries = json.load(f)
                        for  nam in countries:
                            if msg.author.display_name==nam["name"]:
                                nam["patrol+"]+=amount
                        nam["us"] = ""
                        with open("countries.json", "w") as f:
                                    json.dump(countries, f, indent=4)
            if "!13" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"]:
                        if nam["us"]=="mobMenu":
                            await msg.channel.send("how many?")
                            nam["us"]="blongships"
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
            if msg.content.replace("!", "").isdigit():
                with open("countries.json", "r") as f:
                        countries = json.load(f)
                for  nam in countries:
                    if nam["us"] == "blongships":

                        try:
                            amount = int(msg.content.replace("!", ""))
                        except:
                            await msg.channel.send("Write !number")
                            return
                        with open("countries.json", "r") as f:
                            countries = json.load(f)
                        for  nam in countries:
                            if msg.author.display_name==nam["name"]:
                                nam["longships+"]+=amount
                        nam["us"] = ""
                        with open("countries.json", "w") as f:
                                    json.dump(countries, f, indent=4)
            '''
                        NAVY
                        triemes - 1.0a - 1.0d
                        canoes - 0.1a - 0.2d
                        patrol - 0.1a - 0.9d
                        longships - 2.0a - 0.5d
            '''


                



            if "!progressTimeNow" in msg.content and any(role.name == "Collaborators" for role in msg.author.roles):
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                print(msg.author.roles)
                parts = msg.content.split()
                for  nam in countries:
                    nam["money"]=nam["money"]+nam["gra+"]+nam["pop"]*(((50/nam["moncon"])*nam["tax"])/1000)
                    nam["pop"]=nam["pop"]*nam["pop+"]
                    nam["food"]=nam["food"]+nam["food+"]
                    nam["lux"]=nam["lux"]+nam["lux+"]
                    nam["timber"]=nam["timber"]+nam["timber+"]
                    nam["stone"]=nam["stone"]+nam["stone+"]
                    nam["nobleMetals"]=nam["nobleMetals"]+nam["nobleMetals+"]
                    nam["strategicMetals"]=nam["strategicMetals"]+nam["strategicMetals+"]
                    nam["livestock"]=nam["livestock"]*nam["pop+"]
                    nam["rideAnimals"]=nam["rideAnimals"]*nam["pop+"]
                    if nam["food"]<0:
                        nam["pop+"]=0.9
                        nam["food"]=0

                    if nam["pop+"]<=1.001:
                        nam["pop+"]=nam["pop+"]+0.002+(((nam["lux"]+nam["food"])/1000)/10000)
                    elif nam["pop+"]>1.001:
                        nam["pop+"]=nam["pop+"]-0.002+(((nam["lux"]+nam["food"])/1000)/10000) #50000/1000=5 5/1000=0.005
                    if nam["pop+"]>1.3:
                        nam["pop+"]=nam["pop+"]-0.05
                m="time progressed!"
                await msg.channel.send(m)
                with open("countries.json", "w") as f:
                    json.dump(countries, f, indent=4)
                #!progressTimeNow


            if "!time"  in msg.content:
                await msg.channel.send("time skips at: \n <t:1778968800:t> \n <t:1778983200:t> \n <t:1778997600:t> \n <t:1779012000:t> \n <t:1779026400:t> \n <t:1779040800:t>")
            
            if "!grass" in msg.content:
                await msg.channel.send('''Grass refers to various families of plants. The three major families of grasslike plants are true grasses (Poaceae), sedges (Cyperaceae), and rushes (Juncaceae). Lawns and pasturelands are typically composed of true grasses, five of which cover 46% of the world's arable land: rice, wheat, maize, barley, and sugar cane.[1][2]

"Grass" as a name has been applied to a wide group of unrelated plants including herbaceous plants whose leaves and stems are eaten by both domesticated and wild animals. The word may have its origin in the Proto-Indo-European root *gʰreh₁-, meaning 'to grow'.[3]

Grass can refer to a green area, such as a lawn, park, or a field, and is often used for recreation or for sports such as lawn tennis or bowls.[4] Beginning in the 1970s, some sports venues have installed artificial grass to reduce maintenance costs.''')



            if "!declareWar" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"] and nam["war?"]==0:
                        nam["pop+"]=nam["pop+"]-0.02
                        nam["gra+"]=nam["gra+"]-100
                        nam["strategicMetals+"]=nam["strategicMetals+"]-(nam["pop"]/10000) #1300000/10000=130 fair enough 50000/10000=5 i guess that works
                        nam["war?"]=1
                        with open("countries.json", "w") as f:
                            json.dump(countries, f, indent=4)
                        await msg.channel.send("war started")

            if "!declarePeace" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                for  nam in countries:
                    if msg.author.display_name==nam["name"] and nam["war?"]==1:
                        nam["gra+"]=nam["gra+"]+100
                        nam["pop+"]=nam["pop+"]+0.02
                        nam["strategicMetals+"]=nam["strategicMetals+"]+(nam["pop"]/10000)
                        nam["war?"]=0
                        with open("countries.json", "w") as f:
                            json.dump(countries, f, indent=4)
                        await msg.channel.send("war ended")



            if "!trade" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                parts=msg.content.split("|")
                p1 = msg.author.display_name
                trade1 = int(parts[1])
                tradevar1 = parts[2]

                p2 = parts[3]
                trade2 = int(parts[4])
                tradevar2 = parts[5]
                trade = {
                    "from": p1,
                    "to": p2,
                    "send_item": tradevar1,
                    "send_amount": float(trade1),
                    "receive_item": tradevar2,
                    "receive_amount": float(trade2)
                }
                

                with open("trade.json", "w") as f:
                    json.dump(trade, f, indent=4)
                
                #!trade|value to give|money/pop/food/lux/timber/stone/nobleMetals/strategicMetals/livestock/rideAnimals|other country|value to recieve|money/pop/food/lux/timber/stone/nobleMetals/strategicMetals/livestock/rideAnimals
                await msg.channel.send("KEEP CURRENCY EXCHANGE RATES IN MIND! accept trade @" + p2 + "\n!y/!n")

            if "!help" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                m="\n commands are:\n !printMoney amount - devalues your currency\n !economy - shows specifically your economy\n !economy all - shows all nations economies\n !trade|value to give|money/pop/food/lux/timber/stone/nobleMetals/strategicMetals/livestock/rideAnimals|other country|value to recieve|money/pop/food/lux/timber/stone/nobleMetals/strategicMetals/livestock/rideAnimals - automated trade between nations, use only when both are present or it will do the opposite of timing out \n !declareWar - enters your nation economically into a state of war \n !declarePeace - enters your nation economically into a state of peace\n !expand -expands i guess, costs: 2000 food earns: 50 food production"+"\n!progressTimeNow - progresses time (only for collaborators) \n !add|name|treasury|population|popgrowth|foodStockpile|foodsurplus|luxuryGoods|luxuryGoodsSurplus|timber|timbersurplus|stone|stonesurplus|PreciousMetals|PreciousMetalssurplus|strategicMetals|strategicMetalssurplus|livestock|rideAnimals|money conversion rate|average taxation ex: 0.3 - creates a new country (only for collaborators)\n !showExchangeRate - shows currency values which is very useful for trades \n !tech - shows what technology you may research\n !resources - gives a detailed explanation of all resources \n !deflateCurrency amountOfGoldToUse - adds value back to your currency at the cost of valuable metals \n !time - gives you time until next rp timeskip \n !leaderboard - shows the leaderboard of nations \n !mob - do not use, work in progress"
                await msg.channel.send(m)
                with open("countries.json", "w") as f:
                    json.dump(countries, f, indent=4)
                #!help
                #secret commands: !progressTimeNow \n "commands are: \n !add|name|treasury|population|popgrowth|foodStockpile|foodsurplus|luxuryGoods|luxuryGoodsSurplus|timber|timbersurplus|stone|stonesurplus|PreciousMetals|PreciousMetalssurplus|strategicMetals|strategicMetalssurplus|livestock|rideAnimals|money conversion rate"

            if "!printMoney" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                parts = msg.content.split()
                for  nam in countries:
                    if msg.author.display_name==nam["name"]:
                        temp=nam["money"]
                        nam["money"]=nam["money"]+float(parts[1])
                        nam["pop+"]=nam["pop+"]-0.00001*float(parts[1])
                        nam["moncon"]=nam["moncon"]*(temp / nam["money"])
                        m="money printed! \n treasury: "+str(nam["money"])
                
                        await msg.channel.send(m)
                        with open("countries.json", "w") as f:
                            json.dump(countries, f, indent=4)
                #!printMoney amount

            if "!deflateCurrency" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                parts = msg.content.split()
                for  nam in countries:
                    if msg.author.display_name==nam["name"]:
                        if nam["nobleMetals"]>=float(parts[1]):
                            temp = nam["money"]
                            nam["nobleMetals"]=nam["nobleMetals"]-float(parts[1])

                            infused = float(parts[1])   # amount of silver/gold added

                            # increase currency confidence/value
                            nam["moncon"] = nam["moncon"] * ((temp + infused) / temp)

                            m = "silver/gold infused into treasury!\ncurrency value: " + str(nam["moncon"])
                    
                            await msg.channel.send(m)
                            with open("countries.json", "w") as f:
                                json.dump(countries, f, indent=4)
                #!printMoney amount


            if "!economy" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                print(msg.author.display_name+" wants to know their economy")
                m="you are not on the list"
                def fmt(num):
                    num = float(num)

                    abs_num = abs(num)

                    if abs_num >= 1_000_000_000:
                        return f"{num/1_000_000_000:.3f}".rstrip("0").rstrip(".") + "B"
                    elif abs_num >= 1_000_000:
                        return f"{num/1_000_000:.3f}".rstrip("0").rstrip(".") + "M"
                    elif abs_num >= 1_000:
                        return f"{num/1_000:.3f}".rstrip("0").rstrip(".") + "K"
                    else:
                        return f"{num:.3f}".rstrip("0").rstrip(".")
                for  nam in countries:
                    if msg.author.display_name==nam["name"] or msg.content=="!economy all":
                        m = (
                            f'\n{nam["name"]}\n'
                            f'treasury: {fmt(nam["money"])} + {fmt(nam["gra+"])}\n'
                            f'population: {fmt(nam["pop"])} * {fmt(nam["pop+"])}\n'
                            f'food: {fmt(nam["food"])} + {fmt(nam["food+"])}\n'
                            f'luxury goods: {fmt(nam["lux"])} + {fmt(nam["lux+"])}\n'
                            f'timber: {fmt(nam["timber"])} + {fmt(nam["timber+"])}\n'
                            f'stone: {fmt(nam["stone"])} + {fmt(nam["stone+"])}\n'
                            f'precious metals: {fmt(nam["nobleMetals"])} + {fmt(nam["nobleMetals+"])}\n'
                            f'strategic metals: {fmt(nam["strategicMetals"])} + {fmt(nam["strategicMetals+"])}\n'
                            f'livestock: {fmt(nam["livestock"])} * {fmt(nam["pop+"])}\n'
                            f'ride animals: {fmt(nam["rideAnimals"])} * {fmt(nam["pop+"])}\n'
                            "--"
                            
                            
                            
                        )
                        """
                            f'\n{nam["name"]}\n'
                           f'treasury: {f"{nam["money"]:.3f}".rstrip("0").rstrip(".")} million + {f"{nam["gra+"]:.3f}".rstrip("0").rstrip(".")}\n'
                           f'population: {f"{nam["pop"]:.3f}".rstrip("0").rstrip(".")} million * {f"{nam["pop+"]:.3f}".rstrip("0").rstrip(".")}\n'
                            f'food: {f"{nam["food"]:.3f}".rstrip("0").rstrip(".")} + {f"{nam["food+"]:.3f}".rstrip("0").rstrip(".")}\n'
                            f'luxury goods: {f"{nam["lux"]:.3f}".rstrip("0").rstrip(".")} + {f"{nam["lux+"]:.3f}".rstrip("0").rstrip(".")}\n'
                            f'timber: {f"{nam["timber"]:.3f}".rstrip("0").rstrip(".")} + {f"{nam["timber+"]:.3f}".rstrip("0").rstrip(".")}\n'
                            f'stone: {f"{nam["stone"]:.3f}".rstrip("0").rstrip(".")} + {f"{nam["stone+"]:.3f}".rstrip("0").rstrip(".")}\n'
                            f'precious metals: {f"{nam["nobleMetals"]:.3f}".rstrip("0").rstrip(".")} + {f"{nam["nobleMetals+"]:.3f}".rstrip("0").rstrip(".")}\n'
                            f'strategic metals: {f"{nam["strategicMetals"]:.3f}".rstrip("0").rstrip(".")} + {f"{nam["strategicMetals+"]:.3f}".rstrip("0").rstrip(".")}\n'
                            f'livestock: {f"{nam["livestock"]:.3f}".rstrip("0").rstrip(".")} * {f"{nam["pop+"]:.3f}".rstrip("0").rstrip(".")}\n'
                            f'ride animals: {f"{nam["rideAnimals"]:.3f}".rstrip("0").rstrip(".")} * {f"{nam["pop+"]:.3f}".rstrip("0").rstrip(".")}\n'
                            "--" """
                        
                        await msg.channel.send(m)
                        #!economy or !economy all

            if "!leaderboard" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                print(msg.author.display_name+" wants rankings")
                m=""
                def fmt(num):
                    num = float(num)

                    abs_num = abs(num)

                    if abs_num >= 1_000_000_000:
                        return f"{num/1_000_000_000:.3f}".rstrip("0").rstrip(".") + "B"
                    elif abs_num >= 1_000_000:
                        return f"{num/1_000_000:.3f}".rstrip("0").rstrip(".") + "M"
                    elif abs_num >= 1_000:
                        return f"{num/1_000:.3f}".rstrip("0").rstrip(".") + "K"
                    else:
                        return f"{num:.3f}".rstrip("0").rstrip(".")
                countries2=countries
                def score(nam):
                    return (
                        nam["moncon"]*1000 +
                        nam["food"] +
                        nam["lux"] +
                        nam["timber"] +
                        nam["stone"] +
                        nam["nobleMetals"] +
                        nam["strategicMetals"] +
                        nam["pop"]/1000+
                        (nam["t1"]+nam["t2"]+nam["t3"]+nam["t4"]+nam["t5"]+nam["t6"]+nam["t7"]+nam["t8"]+nam["t9"]+nam["t10"]+nam["t11"]+nam["t12"]+nam["t13"]+nam["t14"]+nam["t15"])*1000+
                        nam["food+"] +
                        nam["lux+"] +
                        nam["timber+"] +
                        nam["stone+"] +
                        nam["nobleMetals+"] +
                        nam["strategicMetals+"] +
                        nam["money"]*nam["moncon"]/10000
                    )
                countries2 = sorted(countries, key=score, reverse=True)
                z=0
                for  nam in countries2:
                    z=z+1
                    if True:
                        m = (
                            f'ranking:\n{z}. {nam["name"]} - currency value: {fmt(nam["moncon"])}, total resources: {fmt(nam["food"]+nam["lux"]+nam["timber"]+nam["stone"]+nam["nobleMetals"]+nam["strategicMetals"])}, population: {fmt(nam["pop"])}, technology: {nam["t1"]+nam["t2"]+nam["t3"]+nam["t4"]+nam["t5"]+nam["t6"]+nam["t7"]+nam["t8"]+nam["t9"]+nam["t10"]+nam["t11"]+nam["t12"]+nam["t13"]+nam["t14"]+nam["t15"]}, total production: {fmt(nam["food+"]+nam["lux+"]+nam["timber+"]+nam["stone+"]+nam["nobleMetals+"]+nam["strategicMetals+"])}\n'
                            "--\n"
                        )
                        await msg.channel.send(m)
                        #!economy or !economy all


            if "!showExchangeRate" in msg.content:
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                m=""
                for  nam in countries:
                    m = m+ (
                        f'currency rates: {nam["name"]} --- {nam["moncon"]}'+"\n"
                            
                    )
                        
                await msg.channel.send(m)
                    #!showExchangeRate


            if "!add" in msg.content and any(role.name == "Collaborators" for role in msg.author.roles): #add and progress time need the correct roles
                with open("countries.json", "r") as f:
                    countries = json.load(f)
                parts = msg.content.split("|")
                countries.append({
                "name": parts[1], #name of country
                "money": float(parts[2]), #name of money/treasury
                "gra+": float(0), #money that goes +
                "moncon": float(parts[19]), #currency exchange rate
                "pop": float(parts[3]), #population
                "pop+": float(parts[4]), #pop modifer
                "food": float(parts[5]), #food stockpile
                "food+": float(parts[6]), #food production
                "lux": float(parts[7]), #luxury goods
                "lux+": float(parts[8]), #lux production
                "timber": float(parts[9]), #timber stockpile
                "timber+": float(parts[10]), #timber production
                "stone": float(parts[11]), #stone stockpile
                "stone+": float(parts[12]), #stone production
                "nobleMetals": float(parts[13]), #gold/silver stockpile
                "nobleMetals+": float(parts[14]), #gold/silver mining
                "strategicMetals": float(parts[15]), #brass/copper/bronze/iron
                "strategicMetals+": float(parts[16]), #iron/copper etc mining
                "livestock": float(parts[17]), #livestock (pretty useless right now)
                "rideAnimals": float(parts[18]), #horses/camels/elephants (also pretty useless right now)
                "war?": 0, #are you at war?
                "tax": float(parts[20]), #tax rate as 10%=0.1
                "t1": 0,         #this is all the research variables, they ensure 1 thing cannot be researched twice starting now
                "t2": 0,
                "t3": 0,
                "t4": 0,
                "t5": 0,
                "t6": 0,
                "t7": 0,
                "t8": 0,
                "t9": 0,
                "t10": 0,
                "t11": 0,
                "t12": 0,
                "t13": 0,
                "t14": 0,
                "t15": 0,
                "t16": 0,
                "t17": 0,
                "t18": 0,
                "t19": 0,
                "t20": 0,
                "t21": 0,
                "t22": 0,
                "t23": 0,
                "t24": 0,
                "t25": 0,
                "t26": 0,
                "t27": 0,
                "t28": 0,
                "t29": 0,
                "t30": 0,
                "us": "",
                "hoplites+": 0,
                "hoplites": 0,
                "warel+": 0,
                "warel": 0,
                "sling+": 0,
                "sling": 0,
                "arch+": 0,
                "arch": 0,
                "milit+": 0,
                "milit": 0,
                "harch+": 0,
                "harch": 0,
                "ligcav+": 0,
                "ligcav": 0,
                "merccav+": 0,
                "merccav": 0,
                "mercinf+": 0,
                "mercinf": 0,
                "triemes":0,
                "canoes":0,
                "patrol":0,
                "longships":0

                #current format => !add|name|treasury|population|popgrowth|foodStockpile|foodsurplus|luxuryGoods|luxuryGoodsSurplus|timber|timbersurplus|stone|stonesurplus|PreciousMetals|PreciousMetalssurplus|strategicMetals|strategicMetalssurplus|livestock|rideAnimals|moneyconversionate|tax


#Storhamn: !add|Kingdom of Storhamn|5200000000|1300000|1.001|50000|25000|10000|1000|50000|100|1000|500|0|700|1000|500|10000|5000|0.8|0.1
#Dutchy of Novo-Gorod: !add|Dutchy of Novo-Gorod|6500000000|50000|1.001|50000|100|10|1|50000|100|100|50|500|70|1000|100|1000|5000|1|0.25
#base: !add|name|10000|pop|1.001 or more if low pop|3000|100|pop/1000|<-/100|timber depends on region 5000-1000|timbersurplus depends on region 400-100|1000|50|500|100|500|200|2000|2000|0.7|tax



                })
                with open("countries.json", "w") as f:
                    json.dump(countries, f, indent=4)
                m="country added"
                await msg.channel.send(m)
        except Exception as e:
            m="ERROR something went wrong"
            print("🔥 CRASH:", repr(e))
            await msg.channel.send(m)
            





        







bot.run(token)
