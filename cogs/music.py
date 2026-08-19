import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
from typing import Optional, Dict, Any, Union
import asyncio

# noinspection SpellCheckingInspection
class Music(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

        self.is_playing: bool = False

        self.song_playing: Union[str, list] = ''
        self.music_queue: list = []

        self.YDL_OPTIONS: Dict[str, Any] = {
            'format': 'bestaudio/best',
            'noplaylist': False,  # Process full playlists instead of single videos
            'nocheckcertificate': True,
            'ignoreerrors': True,  # Skip unavailable or private videos without raising an error
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'cookiefile': 'config/cookies.txt',
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
        }

        self.FFMPEG_OPTIONS: Dict[str, str] = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.vc: Optional[discord.VoiceClient] = None

    def search_yt(self, item: str) -> Union[list, bool]:
        # Determine if the input is a direct URL or a search query
        is_link = item.startswith('http')
        query = item if is_link else f"ytsearch:{item}"

        # noinspection PyTypeChecker
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            # noinspection PyBroadException
            try:
                info = ydl.extract_info(query, download=False)
            except Exception:
                return False

        if not info or not isinstance(info, dict):
            return False

        songs = []

        # The 'entries' key indicates a playlist or a list of search results
        if 'entries' in info:
            entries = info.get('entries')
            if not isinstance(entries, list) or not entries:
                return False

            if not is_link:
                # For search queries, extract only the first top result
                first_entry = entries[0]
                if isinstance(first_entry, dict):
                    songs.append({
                        'source': first_entry.get('url', ''),
                        'title': first_entry.get('title', ''),
                        'link': first_entry.get('webpage_url', '')
                    })
            else:
                # For playlist URLs, extract all valid video entries
                for entry in entries:
                    if isinstance(entry, dict):  # Skip entries that are unavailable or private
                        songs.append({
                            'source': entry.get('url', ''),
                            'title': entry.get('title', ''),
                            'link': entry.get('webpage_url', '')
                        })
        else:
            # Single video entry without a playlist wrapper
            songs.append({
                'source': info.get('url', ''),
                'title': info.get('title', ''),
                'link': info.get('webpage_url', '')
            })

        return songs if len(songs) > 0 else False

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']
            self.song_playing = self.music_queue[0]
            self.music_queue.pop(0)

            if self.vc:
                def after_playing(err):
                    if err:
                        print(f"\n[FFMPEG STREAM ERROR]: {err}\n")
                    self.play_next()

                self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=after_playing)
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

                # Explicit type check to satisfy linter
                song_info = self.song_playing[0]
                if isinstance(song_info, dict):
                    print(f"3. Injecting audio to FFmpeg: {song_info.get('title', 'Unknown')}")

                if self.vc:
                    def after_playing(err):
                        if err:
                            print(f"\n[FFMPEG STREAM ERROR]: {err}\n")
                        self.play_next()

                    self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=after_playing)
                    print("4. Audio streaming perfectly!\n")

            # noinspection PyBroadException
            except Exception as e:
                print(f"\n[AUDIO ERROR DETECTED]: {e}\n")
                self.is_playing = False  # Unlock bot to try again
                if self.vc:
                    # noinspection PyBroadException
                    try:
                        await self.vc.disconnect()
                    except Exception:
                        pass
                    self.vc = None
        else:
            self.is_playing = False
            if self.vc:
                # noinspection PyBroadException
                try:
                    await self.vc.disconnect()
                except Exception:
                    pass
                self.vc = None

    @commands.command(name="help", aliases=['h', 'ajuda'], help="Mostra esta central de ajuda com todos os comandos.")
    async def help(self, ctx):
        # Create the embed with an introductory description
        embedhelp = discord.Embed(
            colour=32768,
            description="Olá! Eu sou o seu Bot de Música. Fui desenvolvido para extrair e reproduzir áudios e playlists do YouTube com alta qualidade diretamente no seu canal de voz.\n\n**Abaixo está a lista de comandos que você pode usar:**"
        )

        # Set dynamic title and thumbnail based on the bot's profile
        bot_user = self.client.user
        if bot_user is not None:
            embedhelp.title = f'🎵 Central de Ajuda do {bot_user.name}'
            bot_avatar = bot_user.avatar
            if bot_avatar is not None:
                embedhelp.set_thumbnail(url=bot_avatar.url)
        else:
            embedhelp.title = '🎵 Central de Ajuda'

        # Loop through all bot commands and format them nicely
        for command in self.client.commands:
            cmd_help = command.help if command.help else "Sem descrição"

            # Format aliases to look like: [alias1, alias2]
            aliases_str = f" `[{', '.join(command.aliases)}]`" if command.aliases else ""

            # Add each command as a separate field in the embed
            embedhelp.add_field(
                name=f"**!{command.name}**{aliases_str}",
                value=f"> {cmd_help}",
                inline=False
            )

        # Add a helpful footer note
        embedhelp.set_footer(text="Dica: Comandos como skip, stop e jump exigem permissão de Gerenciar Canais.")

        await ctx.send(embed=embedhelp)

    @commands.command(name="play", help="Toca uma música ou playlist do YouTube", aliases=['p', 'tocar'])
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

        # Send a temporary loading message during metadata extraction
        processing_msg = await ctx.send("🔍 Processando áudio, aguarde...")

        songs = await asyncio.to_thread(self.search_yt, query)

        # Ensure songs returned a valid list and silence linter warnings
        if isinstance(songs, bool):
            embedvc = discord.Embed(
                colour=12255232,
                description='Algo deu errado! Tente mudar o link, verificar se a playlist é pública ou escrever o nome novamente!'
            )
            await processing_msg.edit(content=None, embed=embedvc)
            return

        # Format the confirmation message based on the number of songs added
        if len(songs) == 1:
            embedvc = discord.Embed(
                colour=32768,
                description=f"Você adicionou a música [**{songs[0]['title']}**]({songs[0]['link']}) à fila!"
            )
        else:
            embedvc = discord.Embed(
                colour=32768,
                description=f"Você adicionou uma playlist com **{len(songs)}** músicas à fila!"
            )

        await processing_msg.edit(content=None, embed=embedvc)

        # Append extracted songs to the playback queue
        for song in songs:
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

    @commands.command(name="jump", help="Pula direto para uma música específica da fila.", aliases=['j', 'pularpara'])
    @commands.has_permissions(manage_channels=True)
    async def jump(self, ctx, index: str):
        try:
            target_index = int(index)
        except ValueError:
            embedvc = discord.Embed(
                colour=12255232,
                description="Por favor, forneça um número válido da fila. Ex: `!jump 3`"
            )
            await ctx.send(embed=embedvc)
            return

        if not self.music_queue:
            embedvc = discord.Embed(
                colour=1646116,
                description="A fila está vazia no momento."
            )
            await ctx.send(embed=embedvc)
            return

        if target_index < 1 or target_index > len(self.music_queue):
            embedvc = discord.Embed(
                colour=12255232,
                description=f"Posição inválida! Escolha um número entre **1** e **{len(self.music_queue)}**."
            )
            await ctx.send(embed=embedvc)
            return

        # Convert to 0-based index and pop the song from its current position
        list_index = target_index - 1
        song_to_jump = self.music_queue.pop(list_index)

        # Insert the selected song at the very beginning of the queue
        self.music_queue.insert(0, song_to_jump)

        song_data = song_to_jump[0]
        if isinstance(song_data, dict):
            embedvc = discord.Embed(
                colour=32768,
                description=f"Pulando diretamente para: [**{song_data.get('title', 'Unknown')}**]({song_data.get('link', '')})"
            )
            await ctx.send(embed=embedvc)

        # Stop the current playback to trigger play_next() automatically with the new top song
        if self.vc and self.is_playing:
            self.vc.stop()
        elif not self.is_playing:
            await self.play_music()

    @commands.command(name="stop", help="Para a música e limpa a fila atual.", aliases=['parar'])
    @commands.has_permissions(manage_channels=True)
    async def stop(self, ctx):
        # Clear the queue completely
        self.music_queue.clear()

        if self.vc:
            self.vc.stop()

        self.is_playing = False
        self.song_playing = ''

        embedvc = discord.Embed(
            colour=12255232,
            description="Música parada e fila completamente limpa!"
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
    @jump.error
    @stop.error
    async def permissions_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embedvc = discord.Embed(
                colour=12255232,
                description=f"Você precisa da permissão **Gerenciar canais** para usar este comando!"
            )
            await ctx.send(embed=embedvc)
        else:
            raise error


async def setup(client):
    await client.add_cog(Music(client))