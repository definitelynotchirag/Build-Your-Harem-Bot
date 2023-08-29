import logging
import os
from telethon import TelegramClient,events,Button
from telethon.tl.types import MessageEntityTextUrl
from telegraph import Telegraph,exceptions,upload_file
GODS = [1109460378]
from config import *
import keep_alive

from Texts import *

from mongo import db

cln = db.byh
sudos = db.sudo
numcount = db.waifunum
groupsdb = db.groups
users = db.users
Tempwaifu = db.tempwaifu


keep_alive.keep_alive()

op = numcount.find_one({'Waifus':True})
if not op:
    numcount.insert_one({'Waifus':True,'CurrentCount':0})
    CurrentCount = 0
else:
    CurrentCount = int(op['CurrentCount'])

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',level=logging.WARNING)

client = TelegramClient("BYH",API_ID,API_HASH)

print("STARTING BUILD YOUR HAREM BOT")

client.start(bot_token = BOT_TOKEN)
client.parse_mode = 'html'

print("CONNECTING TO TELEGRAPH")

telegraph = Telegraph()
data = telegraph.create_account(short_name="BYH")

print("BOT SUCESSFULLY CONNECTED")

sudolist = []
for sudo in sudos.find():
    sudoid = sudo['ID']
    sudolist.append(sudoid)
for god in GODS:
    sudolist.append(god)

print("GRABBING SUDOS")

print("GRABBING THOSE WAIFUS...")

def adduser(senderid):
    users.insert_one({'userid':senderid})
    return 

def isuser(userid):
    userr = users.find_one({'userid':userid})
    if userr:
        return userr
    else:
        return False
        
def is_sudo(senderid):
    is_sudo = sudos.find_one({'ID':senderid})
    if is_sudo:
        return True
    else:
        return False
m=1
def last(n):
    return n[m]

def sort(tuples):
    # We pass used defined function last
    # as a parameter.
    return sorted(tuples, reverse=True ,key = last)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    chat = await event.get_chat()
    sender = await event.get_sender()

    if not isuser(sender.id):
        adduser(sender.id)

    markup = client.build_reply_markup(buttons=
[[Button.url('Add Me To Your Groups',url='https://t.me/build_your_harem_bot?startgroup=true')],[
Button.url('Support Group',url='https://t.me/harembuilders'),
Button.url('Waifu Database',url='https://t.me/byhwaifupics')]])
    
    await client.send_message(chat, START_TEXTS, buttons = markup, file=START_IMG)


@client.on(events.NewMessage(pattern="/upload"))
async def upload(event):
    op = numcount.find_one({'Waifus':True})
    if not op:
        numcount.insert_one({'Waifus':True,'CurrentCount':0})
        CurrentCount = 0
    else:
        CurrentCount = int(op['CurrentCount'])

    sender = await event.get_sender()
    if not is_sudo(sender.id):
        await event.reply("You Need Sudo for Contributing!! Ask @chirag57 if you wanna Contribute. Thanks")
        return

    replymsg = await event.get_reply_message()
    if replymsg:
        arg = event.raw_text.split(" ")
        
    else :
        arg = event.raw_text.split(" ")
    print(arg)
    if len(arg) not in [3,4]:
        await event.reply('Invalid Syntax!\nTry <code>/upload [waifu name] [anime name] [rarity]\n</code>\n\nNote: Please use "-" instead of SPACE in anime and waifu name\nEXAMPLE - <code>/upload mikasa-ackerman attack-on-titan 1</code>')
    waifuname = arg[1].lower()
    animename = arg[2].lower()
    rarity = int(arg[3])
    try:
        category = arg[4]
    except Exception:
        category = "Normal"

    reversel = list(waifuname.split('-')).reverse()
    bc = []
    try:
        reversewaifuname = '-'.join(reversel)
        reversewaifus = cln.find({'name':f'{reversewaifuname}'})
        for x in reversewaifus:
            bc.append(x)
    except Exception:
        reversewaifus = None
        reversewaifuname = waifuname
        pass
    xd = []
    waifuss = cln.find({'name':f'{waifuname}'})
    for x in waifuss:
        xd.append(x)
    totalimages = int(len(xd))
    nextimagenum = totalimages + 1

    if replymsg:
        sender = await event.get_sender()
        filename = await replymsg.download_media(file = f'{waifuname}')
    else:
        sender = await event.get_sender()
        filename = await event.download_media(file = f'{waifuname}')
    try:
        media_urls = upload_file(filename)
    except exceptions.TelegraphException as exc:
        await event.reply(f"ERROR:{str(exc)}")
    os.remove(filename)
    imglink = f"https://te.legra.ph{media_urls[0]}"   
    if rarity == 1:
        rarrity = "common"
    elif rarity == 2:
        rarrity = "rare"
    elif rarity == 3:
        rarrity = "epic"
    elif rarity == 4:
        rarrity = "legendary"

    i = True
    while i == True:
        waifusid = int(random.randrange(550,5000))
        try:
            iswaifu = cln.find_one({"waifunum":waifusid})
        except Exception:
            continue
        i = False

    msg = await client.send_message(WAIFU_CHANNEL,f"#Waifu_added\nName - <code>{waifuname.upper()}</code>\nAnime - <code>{animename.upper()}</code>\nRarity - <code>{rarrity.upper()}</code>\nCategory - <code>{category}</code>\nAdded By - @{sender.username if sender.username else sender.id}",file=imglink,buttons = [Button.inline(f"WAIFU ID - {waifusid}", "cc"),Button.inline(f"👍 - 0",data="incinvite")])
    url = f"https://t.me/byhwaifupics/{msg.id}"

    print(url)
    waifudict = {'name':f'{waifuname}',
                 'reversename':f'{reversewaifuname}',
                 'waifunum':waifusid,
                 'imagenum':nextimagenum,
                 'anime':  f'{animename}',
                 'image1':f"https://te.legra.ph{media_urls[0]}",
                 'image1likes':0,
                 'image1likedby':[],
                 'channellink':url,
                 'addedby':f'{sender.username if sender.username else sender.id}',
                 'rarity':rarrity,
                 'category':category
                 }

    cln.insert_one(waifudict)
    if len(xd) or len(bc) != 0:
        buttons = []
        for waifus in xd:
            linkss = waifus['channellink']
            imagenum = waifus['imagenum']
            buttons.append(Button.url(f'Waifu - {imagenum}',url=f'{linkss}'))
            await event.reply("Your Waifu has been addded to database!\nThese Waifu is Added by others too so make sure to check them out!.\n",buttons=buttons)
    else:
        await event.reply(f"DONE! Waifu {waifuname} Added to Database. Thanks for Contributing :)\nCheck @byhwaifupics")

    global waifu_id
    waifu_id = CurrentCount+1
    
    numcount.update_one({'Waifus':True},{'$set':{'CurrentCount':CurrentCount+1}})
    x = sudos.find_one({'ID':sender.id})
    cont = x['Contributions']
    sudos.update_one({'ID':sender.id},{'$set':{'Contributions':cont+1}})
    # await client.send_message(1109460378,f'Choose Rarity for {waifuname.upper()}',buttons = [Button.url("WAIFU", f"{url}"),Button.inline("Common",data="r_common"),Button.inline("Rare",data="r_rare"),Button.inline("Epic",data="r_epic"),Button.inline("Legendary",data="r_legendary")])


@client.on(events.CallbackQuery(data=r"r_common"))
async def r_common(event):
        sender = await event.get_sender()
        xd = Tempwaifu.find_one({"sender":sender.id})
        name = xd['name']        
        cln.update_one({'name':name},{'$set':{'rarity':"common"}})
        Tempwaifu.update_one({'sender':sender.id},{'$set':{'name':None}})
        await event.edit(f"Done {name} is now  {event.data} ")

        # Tempwaifu.find_one_and_delete({"sender":sender.id})


@client.on(events.CallbackQuery(data=r"r_rare"))
async def r_rare(event):
        sender = await event.get_sender()
        xd = Tempwaifu.find_one({"sender":sender.id})
        name = xd['name']        
        cln.update_one({'name':name},{'$set':{'rarity':"rare"}})
        Tempwaifu.update_one({'sender':sender.id},{'$set':{'name':None}})
        await event.edit(f"Done {name} is now  {event.data} ")

@client.on(events.CallbackQuery(data=r"r_epic"))
async def r_epic(event):
        sender = await event.get_sender()
        xd = Tempwaifu.find_one({"sender":sender.id})
        name = xd['name']        
        cln.update_one({'name':name},{'$set':{'rarity':"epic"}})
        Tempwaifu.update_one({'sender':sender.id},{'$set':{'name':None}})
        await event.edit(f"Done {name} is now  {event.data} ")



@client.on(events.CallbackQuery(data=r"r_legendary"))
async def r_legendary(event):
        sender = await event.get_sender()
        xd = Tempwaifu.find_one({"sender":sender.id})
        name = xd['name']        
        cln.update_one({'name':name},{'$set':{'rarity':"legendary"}})
        Tempwaifu.update_one({'sender':sender.id},{'$set':{'name':None}})
        await event.edit(f"Done {name} is now  {event.data} ")



@client.on(events.NewMessage(pattern="/rarity"))
async def rarities(event):
    sender = await event.get_sender()
    list = cln.find({"addedby":sender.username})
    for waifus in list:                            
        name = waifus['name']
        anime = waifus['anime']
        link = waifus['channellink']
        image = waifus['image1']
        try:
            rarity = waifus['rarity']
        except Exception:
            rarity = None

        if rarity :
            continue    

        # global waifuid
        waifuid = waifus['waifunum']
        

        x = Tempwaifu.find_one({'sender':sender.id})
        if x:
            Tempwaifu.update_one({'sender':sender.id},{'$set':{'name':name}})
        else:
            Tempwaifu.insert_one({"sender":sender.id,"name":name})

        await event.reply(f'Choose Rarity for:\nName : {name}\nAnime : {anime}\n',file=image,buttons = [Button.url("WAIFU", f"{link}"),Button.inline("Common",data="r_common"),Button.inline("Rare",data="r_rare"),Button.inline("Epic",data="r_epic"),Button.inline("Legendary",data="r_legendary")])
        break
        
@client.on(events.NewMessage(pattern="/topsudos"))
async def topsudos(event): 
    msg = "Top Contributors:-\n\n"
    sudolist = sudos.find()
    sudoss = []
    limit = 0
    for sudo in sudolist:
        ids = str(sudo['ID'])
        username = str(sudo['username'])
        contri = sudo['Contributions']
        sudoss.append((ids,contri,username))
    reverselist = sort(sudoss)
    for id,contris,username in reverselist:
        if limit>9:
            break
        numb = limit + 1
        uu = str("https://t.me/")
        msg += f"{numb}. <a href='{uu + username}'>{(username)}</a> - <code>{contris} contris\n "
        limit += 1
    await event.reply(msg,file="https://telegra.ph/file/8b6a210fd07b9b0f8ecd2.jpg")

@client.on(events.NewMessage(pattern="/delwaifu"))
async def delwaifu(event):
    op = numcount.find_one({'Waifus':True})
    if not op:
        numcount.insert_one({'Waifus':True,'CurrentCount':0})
        CurrentCount = 0
    else:
        CurrentCount = int(op['CurrentCount'])

    sender = await event.get_sender()
    if not is_sudo(sender.id):
        await event.reply("You Need Sudo for Contributing!! Ask @chirag57 if you wanna Contribute. Thanks")
        return
    arg = event.raw_text.split(" ")

    if arg[1] == str:
        await event.reply("Sorry you can only delete waifus by using IDs for Now!\nFind it here @byhwaifupics")
    if len(arg) < 1:
        await event.reply("Baka Tell the Waifu ID to Delete")
        return

    try:
        waifuu = cln.find_one({'waifunum':int(arg[1])})
        waifuname = waifuu['name']
        linkk = waifuu['channellink']
        messageid = linkk.split("/")[4]
        cln.find_one_and_delete({'waifunum':int(arg[1])})
        # await event.reply("Removed!")
        # op = numcount.find_one({'Waifus':True})
        # CurrentCount = int(op['CurrentCount'])
        CurrentCount -= 1
        numcount.update_one({'Waifus':True},{'$set':{'CurrentCount':CurrentCount-1}})
        x = sudos.find_one({'ID':sender.id})
        cont = x['Contributions']
        sudos.update_one({'ID':sender.id},{'$set':{'Contributions':cont-1}})

        await client.delete_messages(WAIFU_CHANNEL,messageid)
        await event.reply(f"Done Removed {waifuname} From Database")

    except Exception as e:
        await event.reply("Waifu Not in Database. Perhaps check spelling or use the complete Name")
        print(e)



@client.on(events.NewMessage(pattern="/addsudo"))
async def addsudo(event):
    sender1 = await event.get_sender()
    # if sender1.id == 1109460378:
    #     pass
    if int(sender1.id) != 1109460378:
        await event.reply("You Aren't GOD!")
        return
    
    arg = event.raw_text.split(' ')
    repliedmsg = await event.get_reply_message()
    sender = repliedmsg.sender
    sudos.insert_one({'username':f'{sender.username}','ID':sender.id,'Contributions':0})
    await event.reply(f"{sender.username if sender.username else sender.id} is now a Sudo!")


@client.on(events.NewMessage(pattern='/reload'))
async def reload(event):
    sender = await event.get_sender()
    if sender.id not in GODS:
        await event.reply("You Aren't GOD!")
        return
    
    for sudo in sudos.find():
        sudoid = sudo['ID']
        sudolist.append(sudoid)

    await event.reply("Reloaded Sudo Cache!")

@client.on(events.NewMessage())
async def spawnwaifu(event):
    # if event.chat
    chat = event.chat.id
    ischat = groupsdb.find_one({'chatid':chat})
    if not ischat:
        groupsdb.insert_one({'chatid':chat,'spawntime':100,'Currentmsgcount':2})
        currentmsg = 2
        ischat = groupsdb.find_one({'chatid':chat})

    spawntime = int(ischat['spawntime'])
    currentmsg = int(ischat['Currentmsgcount'])
    if currentmsg == spawntime:
        waifuslist = []
        # waifuss = cln.find()
        randomwaifu = list(cln.aggregate([{'$sample': {'size':1} }]))[0]
        name = randomwaifu['name']
        anime = randomwaifu['anime']
        waifuidd = randomwaifu['waifunum']
        # rarity = randomwaifu['rarity']
        image = randomwaifu['image1']

        x = await client.send_message(chat,"A Waifu Has Spawned! Grab them by using /protecc [waifu name]",file=image)
        groupsdb.update_one({'chatid':chat},{'$set':{'Currentlyspawnedwaifu':waifuidd}})
        print(name)
        groupsdb.update_one({'chatid':chat},{'$set':{'Currentlyspawnedwaifumsgid':x.id}})
        groupsdb.update_one({'chatid':chat},{'$set':{'Currentmsgcount':currentmsg+1}})

    else:
        groupsdb.update_one({'chatid':chat},{'$set':{'Currentmsgcount':currentmsg+1}})

@client.on(events.NewMessage(pattern="/protecc"))
async def proteccwaifu(event):
    sender = await event.get_sender()
    chat = event.chat.id
    chatinfo = groupsdb.find_one({'chatid':chat})
    if not chatinfo:
        groupsdb.insert_one({'chatid':chat,'spawntime':100,'Currentmsgcount':2})
        ischat = groupsdb.find_one({'chatid':chat})
    try:
        lastspawnedwaifu = chatinfo['lastspawnedwaifu']
        lastgrabbedby = chatinfo['lastwaifugrabber']
    except Exception:
        lastspawnedwaifu = None

    try:
        spawnedwaifu = chatinfo['Currentlyspawnedwaifu']
        msgid = chatinfo['Currentlyspawnedwaifumsgid']
    except KeyError:
        if not lastspawnedwaifu:
            await event.reply('No Waifus here To protecc!!')
        else:
            await event.reply(f'Waifu Already Grabbed by {lastgrabbedby}')

    try:
        args = event.raw_text.split(' ')
        args.remove('/protecc')
    except Exception:
        await event.reply('Invalid Syntax!!\nUse <code>/protecc [waifu name]</code>')
    
    waifu = cln.find_one({'waifunum':spawnedwaifu})
    name = str(waifu['name'])
    anime = waifu['name']
    namelist = name.split('-')
    print(namelist)
    for argument in args:
        print(argument)
        if argument in namelist:
            await event.reply(f'Woah! You Just Grabbed {" ".join(namelist).capitalize()}. This Waifu has been added to your harem!')
            groupsdb.update_one({'chatid':chat},{'$set':{'Currentlyspawnedwaifu':None}})
            groupsdb.update_one({'chatid':chat},{'$set':{'lastspawnedwaifu':waifu['waifunum']}})
            groupsdb.update_one({'chatid':chat},{'$set':{'lastwaifugrabber':sender.id}})
            groupsdb.update_one({'chatid':chat},{'$set':{'Currentmsgcount':0}}) 
            break
        else:
            await event.reply(f"<code>That Doesn't Seem As a Correct Name! Use Your Anime Brain</code>")
    

@client.on(events.CallbackQuery(data='incinvite'))
async def likequery(event):
    
    msgid = event.message_id
    querysender = await event.get_sender()
    url = f"https://t.me/byhwaifupics/{msgid}"
    waifuu = cln.find_one({'channellink':url})
    waifuname = waifuu['name']
    animename = waifuu['anime']
    sender = waifuu['addedby']
    likes = waifuu['image1likes']
    likedby = waifuu['image1likedby']
    CurrentCount = waifuu['waifunum']
    imglink = waifuu['image1']
    if querysender.id in likedby:
        await event.answer("You Have Already Voted Once!",alert=True)
        return
    await event.edit(f"#Waifu_added\nName - <code>{waifuname.upper()}</code>\nAnime - <code>{animename.upper()}</code>\nAdded By - @{sender}",file=imglink,buttons = [Button.inline(f"WAIFU ID - {CurrentCount}", "cc"),Button.inline(f"👍 - {likes+1}",data="incinvite")])
    likedby.append(querysender.id)
    likes = likes + 1
    cln.update_one({'name':waifuname},{'$set':{'image1likedby':likedby}})
    cln.update_one({'name':waifuname},{'$set':{'image1likes':likes}})


client.run_until_disconnected()
