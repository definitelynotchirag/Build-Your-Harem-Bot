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

def is_sudo(senderid):
    is_sudo = sudos.find_one({'ID':senderid})
    if is_sudo:
        return True
    else:
        return False

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    chat = await event.get_chat()

    markup = client.build_reply_markup(buttons=
[[Button.url('Add Me To Your Groups',url='https://t.me/build_your_harem_bot?startgroup=true')],[
Button.url('Support Channel',url='https://t.me/friendswithoutbenefits'),
Button.url('Update Channel',url='https://t.me/friendswithoutbenefits')]])
    
    await client.send_message(chat, START_TEXTS, buttons = markup, file=START_IMG)


@client.on(events.NewMessage(pattern="/upload"))
async def upload(event):
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
    if len(arg) not in [2,3]:
        await event.reply('Invalid Syntax!\nTry <code>/upload [waifu name] [anime name]</code>\n\nNote: Please use "-" instead of SPACE in anime and waifu name\nEXAMPLE - <code>/upload mikasa-ackerman attack-on-titan</code>')
        return
    
    waifuname = arg[1].lower()
    animename = arg[2].lower()

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

    msg = await client.send_message(WAIFU_CHANNEL,f"#Waifu_added\nName - <code>{waifuname.upper()}</code>\nAnime - <code>{animename.upper()}</code>\nAdded By - @{sender.username if sender.username else sender.id}",file=imglink,buttons = [Button.inline(f"WAIFU ID - {CurrentCount+1}", "cc"),Button.inline(f"👍 - 0",data="incinvite")])

    url = f"https://t.me/byhwaifupics/{msg.id}"

    print(url)
    waifudict = {'name':f'{waifuname}',
                 'reversename':f'{reversewaifuname}',
                 'waifunum':CurrentCount+1,
                 'imagenum':nextimagenum,
                 'anime':  f'{animename}',
                 'image1':f"https://te.legra.ph{media_urls[0]}",
                 'image1likes':0,
                 'image1likedby':[],
                 'channellink':url,
                 'addedby':f'{sender.username if sender.username else sender.id}'}

    cln.insert_one(waifudict)
    if len(xd) or len(bc) != 0:
        buttons = []
        for waifus in xd:
            linkss = waifus['channellink']
            imagenum = waifus['imagenum']
            buttons.append(Button.url(f'Waifu - {imagenum}',url=f'{linkss}'))
        await event.reply("Your Waifu has been addded to database!\nThese Waifu is Added by others too so make sure to check them out!.\n(Last Button is Your Waifu)",buttons=buttons)
    else:
        await event.reply(f"DONE! Waifu {waifuname} Added to Database. Thanks for Contributing :)\nCheck @byhwaifupics")


    numcount.update_one({'Waifus':True},{'$set':{'CurrentCount':CurrentCount+1}})
    x = sudos.find_one({'ID':sender.id})
    cont = x['Contributions']
    sudos.update_one({'ID':sender.id},{'$set':{'Contributions':cont+1}})


@client.on(events.NewMessage(pattern="/delwaifu"))
async def delwaifu(event):
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
        await event.reply("Removed!")
        op = numcount.find_one({'Waifus':True})
        CurrentCount = int(op['CurrentCount'])
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
    if sender1.id not in GODS:
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
