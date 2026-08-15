import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
from typing import Optional, Dict, Any, Union


# noinspection SpellCheckingInspection
class Music(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

        self.is_playing: bool = False

        self.song_playing: Union[str, list] = ''
        self.music_queue: list = []

        self.YDL_OPTIONS: Dict[str, Any] = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'username': 'oauth2',
            'password': '',
        }

        self.FFMPEG_OPTIONS: Dict[str, str] = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.vc: Optional[discord.VoiceClient] = None

    def search_yt(self, item: str) -> Union[Dict[str, str], bool]:
        # noinspection PyTypeChecker
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            # noinspection PyBroadException
            try:
                info = ydl.extract_info(f"ytsearch:{item}", download=False)
                if isinstance(info, dict) and 'entries' in info:
                    info = info['entries'][0]
            except Exception:
                return False

        if not info or not isinstance(info, dict):
            return False

        return {'source': info.get('url', ''), 'title': info.get('title', ''), 'link': info.get('webpage_url', '')}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']
            self.song_playing = self.music_queue[0]
            self.music_queue.pop(0)

            if self.vc:
                self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda err: self.play_next())
        else:
            self.is_playing = False

    async def play_music(self):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']
            voice_channel = self.music_queue[0][1]

            try:
                print("--- AUDIO PROCESS START ---")
                print("1. Trying to connect to voice channel...")
                if self.vc is None or not self.vc.is_connected():
                    self.vc = await voice_channel.connect()
                    print("2. Successfully connected to the channel!")
                else:
                    await self.vc.move_to(voice_channel)

                self.song_playing = self.music_queue[0]
                self.music_queue.pop(0)

                # explicit type check to satisfy linter
                song_info = self.song_playing[0]
                if isinstance(song_info, dict):
                    print(f"3. Injecting audio to FFmpeg: {song_info.get('title', 'Unknown')}")

                if self.vc:
                    self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                                 after=lambda err: self.play_next())
                    print("4. Audio streaming perfectly!\n")

            except Exception as e:
                print(f"\n[AUDIO ERROR DETECTED]: {e}\n")
                self.is_playing = False  # unlock bot to try again
                if self.vc:
                    await self.vc.disconnect()
        else:
            self.is_playing = False
            if self.vc:
                await self.vc.disconnect()

    @commands.command(name="help", aliases=['ajuda'], help="Comando de ajuda")
    async def help(self, ctx):
        helptxt = ''
        for command in self.client.commands:
            cmd_help = command.help if command.help else "Sem descrição"
            helptxt += f'**{command}** - {cmd_help}\n'

        embedhelp = discord.Embed(
            colour=1646116,
            description=helptxt
        )

        bot_user = self.client.user
        if bot_user is not None:
            embedhelp.title = f'Comandos do {bot_user.name}'
            bot_avatar = bot_user.avatar
            if bot_avatar is not None:
                embedhelp.set_thumbnail(url=bot_avatar.url)
        else:
            embedhelp.title = 'Comandos do Bot'

        await ctx.send(embed=embedhelp)

    @commands.command(name="play", help="Toca uma música do YouTube", aliases=['p', 'tocar'])
    async def p(self, ctx, *args):
        query = " ".join(args)

        try:
            voice_channel = ctx.author.voice.channel
        except AttributeError:
            embedvc = discord.Embed(
                colour=1646116,
                description='Para tocar uma música, primeiro se conecte a um canal de voz.'
            )
            await ctx.send(embed=embedvc)
            return
        else:
            song = self.search_yt(query)
            if isinstance(song, bool):
                embedvc = discord.Embed(
                    colour=12255232,
                    description='Algo deu errado! Tente mudar ou configurar a playlist/vídeo ou escrever o nome dele novamente!'
                )
                await ctx.send(embed=embedvc)
            else:
                embedvc = discord.Embed(
                    colour=32768,
                    description=f"Você adicionou a música [**{song['title']}**]({song['link']}) à fila!"
                )
                await ctx.send(embed=embedvc)
                self.music_queue.append([song, voice_channel])

                if not self.is_playing:
                    await self.play_music()

    @commands.command(name="queue", help="Mostra as atuais músicas da fila.", aliases=['q', 'fila'])
    async def q(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            song_data = self.music_queue[i][0]
            if isinstance(song_data, dict):
                retval += f'**{i + 1} - **' + song_data.get('title', 'Unknown') + "\n"

        if retval != "":
            embedvc = discord.Embed(
                colour=12255232,
                description=f"{retval}"
            )
            await ctx.send(embed=embedvc)
        else:
            embedvc = discord.Embed(
                colour=1646116,
                description='Não existem músicas na fila no momento.'
            )
            await ctx.send(embed=embedvc)

    @commands.command(name="currently", help="Mostra a música tocando.", aliases=['c', 'tocando'])
    async def currently(self, ctx):
        if isinstance(self.song_playing, list) and len(self.song_playing) > 0:
            song_data = self.song_playing[0]
            if isinstance(song_data, dict):
                embedvc = discord.Embed(
                    colour=32768,
                    description=f"Tocando [**{song_data.get('title', 'Unknown')}**]({song_data.get('link', '')}) no momento!"
                )
                await ctx.send(embed=embedvc)

    @commands.command(name="skip", help="Pula a atual música que está tocando.", aliases=['pular', 's'])
    @commands.has_permissions(manage_channels=True)
    async def skip(self, ctx):
        if self.vc:
            self.vc.stop()
            await self.play_music()
            embedvc = discord.Embed(
                colour=1646116,
                description=f"Você pulou a música!"
            )
            await ctx.send(embed=embedvc)

    @commands.command(name="pause", help="Pausa a atual música que está tocando.", aliases=['pausar', 'ps'])
    @commands.has_permissions(manage_channels=True)
    async def pause(self, ctx):
        if self.vc:
            self.vc.pause()
            embedvc = discord.Embed(
                colour=1646116,
                description=f"Você pausou a música!"
            )
            await ctx.send(embed=embedvc)

    @commands.command(name="resume", help="Despausa a atual música que está tocando.", aliases=['despausar', 'rs'])
    @commands.has_permissions(manage_channels=True)
    async def resume(self, ctx):
        if self.vc:
            self.vc.resume()
            embedvc = discord.Embed(
                colour=1646116,
                description=f"Você deu play na música!"
            )
            await ctx.send(embed=embedvc)

    @skip.error
    async def skip_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embedvc = discord.Embed(
                colour=12255232,
                description=f"Você precisa da permissão **Gerenciar canais** para pular músicas!"
            )
            await ctx.send(embed=embedvc)
        else:
            raise error


async def setup(client):
    await client.add_cog(Music(client))