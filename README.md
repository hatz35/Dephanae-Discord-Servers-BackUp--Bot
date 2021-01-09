This Bot is for you if you meet these requirements.
1. You use Discord (It is the best.)
2. Like me, you have loads of data.
3. You are somewhat familiar with Discord Bots + Discord.py & rewrite

Okay. Our Bot's Name is Dephanae/Dephu with a firm personality. You can change it anytime.
To create a local BackUp of your server in your system follow these steps.

<Rep Setup>
1. Clone this repository
2. Create Path Directory Dephanae -> Private -> Data
3. Also add a file in Dephanae -> Private -> "Secrets.py"

 <Bot setup>
1. Create a Discord Bot Application
2. Copy its Token & add in your Secrets.py in this format
Token = "Jh34ok3Sdn"
3. Add your Bot to the servers you want to BackUp + Give the administrator permisssion.
4. Download Pip -> Download Discord.py Aiohttp etc (Modules used in Dephu.py)

<Using Bot - Single Channel>
1. -create [This will create a directory for that channel]
2. -backup [This will put the channel's data in that directory]
3. For loading the backup data, create a new channel with the same name
4. -load [Bot will post all the data from the backup]

<Tips>
 1. You can use -ping to check if Bot is working
 2. -clear x [will delete x number of messages] [Dangerous!!]
 3. You can manually delete/rename a channel/server's backup by deleting the folder [Private -> Data -> "ServerName"-> "ChannelName"] [Dangerous!!]
 4. -deletefull [will delete all the channels in a server for which you have backup in your system][Dangerous!!]

<Using Bot - Single Server>
1. -createFull [This will create a folder for your server having sub folders for all the channels]
2. -backupfull [This will put the server's data in that directory]
3. For loading the backup data, create a new server with the same name
4. -setfull [This will create all the channels in your server for which you have backup in your system]
5. -loadfull [Bot will post all the data from the backup]


<Editing>
You can edit the code anytime but it is not clean at all. :(
