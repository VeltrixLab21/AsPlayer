import os
import wx
import vlc
import pysrt
import accessible_output2.outputs.auto

class AsplayerWindow(wx.Frame):
    def __init__(self):
        super().__init__(None, title="ASPlayer", size=(900, 600))
        
        # Inisialisasi Screen Reader Output
        try:
            self.speech = accessible_output2.outputs.auto.Auto()
        except Exception:
            self.speech = None
            
        # Inisialisasi VLC Media Player
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        
        # Variabel Media & Subtitle
        self.current_video_path = None
        self.srt_subtitles = None
        self.current_sub_index = -1
        
        self.init_ui()
        self.init_timer()
        self.Center()

    def init_ui(self):
        panel = wx.Panel(self)
        
        # Panel render video
        self.video_panel = wx.Panel(panel)
        self.video_panel.SetBackgroundColour(wx.BLACK)
        
        # Hubungkan handle window panel ke VLC
        self.player.set_hwnd(self.video_panel.GetHandle())
        
        # Layout Utama
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.video_panel, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        
        # --- MEMBUAT MENU BAR ---
        menubar = wx.MenuBar()
        
        # 1. Menu File (Alt + F)
        file_menu = wx.Menu()
        self.ID_OPEN_VIDEO = wx.NewIdRef()
        self.ID_OPEN_SUB = wx.NewIdRef()
        self.ID_EXIT = wx.NewIdRef()
        
        file_menu.Append(self.ID_OPEN_VIDEO, "Open Video\tCtrl+O", "Open a video file to play")
        file_menu.Append(self.ID_OPEN_SUB, "Open Subtitle (.srt)\tAlt+O", "Open an external SRT subtitle file")
        file_menu.AppendSeparator()
        file_menu.Append(self.ID_EXIT, "Exit\tAlt+F4", "Close the application")
        
        # 2. Menu View (Alt + V)
        view_menu = wx.Menu()
        self.ID_FULLSCREEN = wx.NewIdRef()
        view_menu.Append(self.ID_FULLSCREEN, "Toggle Fullscreen\tF11", "Switch fullscreen mode")
        
        # 3. Menu Tools (Alt + T)
        tools_menu = wx.Menu()
        self.ID_PREFERENCES = wx.NewIdRef()
        tools_menu.Append(self.ID_PREFERENCES, "Preferences\tCtrl+P", "Configure application settings")
        
        # Masukkan menu ke MenuBar utama
        menubar.Append(file_menu, "&File")
        menubar.Append(view_menu, "&View")
        menubar.Append(tools_menu, "&Tools")
        self.SetMenuBar(menubar)
        
        # Bind Event Menu
        self.Bind(wx.EVT_MENU, self.on_open_video_dialog, id=self.ID_OPEN_VIDEO)
        self.Bind(wx.EVT_MENU, self.on_open_sub_dialog, id=self.ID_OPEN_SUB)
        self.Bind(wx.EVT_MENU, self.on_exit, id=self.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.on_toggle_fullscreen, id=self.ID_FULLSCREEN)
        self.Bind(wx.EVT_MENU, self.on_preferences, id=self.ID_PREFERENCES)
        
        # --- CONTEXT MENU (Klik Kanan / Shift+F10) ---
        self.Bind(wx.EVT_CONTEXT_MENU, self.on_show_context_menu)
        self.video_panel.Bind(wx.EVT_CONTEXT_MENU, self.on_show_context_menu)

        # --- KEYBOARD ACCELERATOR TABLE (Shortcut Global) ---
        self.ID_PLAY = wx.NewIdRef()
        self.ID_RIGHT = wx.NewIdRef()
        self.ID_LEFT = wx.NewIdRef()
        self.ID_UP = wx.NewIdRef()
        self.ID_DOWN = wx.NewIdRef()
        
        self.Bind(wx.EVT_MENU, self.on_toggle_play, id=self.ID_PLAY)
        self.Bind(wx.EVT_MENU, self.on_forward, id=self.ID_RIGHT)
        self.Bind(wx.EVT_MENU, self.on_rewind, id=self.ID_LEFT)
        self.Bind(wx.EVT_MENU, self.on_volume_up, id=self.ID_UP)
        self.Bind(wx.EVT_MENU, self.on_volume_down, id=self.ID_DOWN)
        
        accel_entries = [
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, ord(' '), self.ID_PLAY),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_RIGHT, self.ID_RIGHT),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_LEFT, self.ID_LEFT),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_UP, self.ID_UP),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_DOWN, self.ID_DOWN),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('o'), self.ID_OPEN_VIDEO),
            wx.AcceleratorEntry(wx.ACCEL_ALT, ord('o'), self.ID_OPEN_SUB),
        ]
        self.SetAcceleratorTable(wx.AcceleratorTable(accel_entries))

    def init_timer(self):
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer_tick, self.timer)
        self.timer.Start(200)

    def speak(self, text):
        if self.speech:
            try:
                self.speech.output(text)
            except Exception:
                pass

    def on_open_video_dialog(self, event):
        wildcard = "Video Files (*.mp4;*.mkv;*.avi;*.mov;*.webm;*.ts)|*.mp4;*.mkv;*.avi;*.mov;*.webm;*.ts|All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Open Video File", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.load_video(path)
        dlg.Destroy()

    def load_video(self, path):
        self.current_video_path = path
        media = self.vlc_instance.media_new(path)
        self.player.set_media(media)
        self.player.play()
        self.speak("Playing video")
        self.check_and_load_matching_srt(path)

    def check_and_load_matching_srt(self, video_path):
        folder_dir, file_name = os.path.split(video_path)
        base_name, _ = os.path.splitext(file_name)
        srt_path = os.path.join(folder_dir, base_name + ".srt")
        
        if os.path.exists(srt_path):
            try:
                self.srt_subtitles = pysrt.open(srt_path, encoding='utf-8')
                self.current_sub_index = -1
                self.speak("Matching subtitle loaded automatically")
            except Exception:
                self.srt_subtitles = None
        else:
            self.srt_subtitles = None
            self.current_sub_index = -1

    def on_open_sub_dialog(self, event):
        wildcard = "Subtitle Files (*.srt)|*.srt|All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Open Subtitle File", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            try:
                self.srt_subtitles = pysrt.open(path, encoding='utf-8')
                self.current_sub_index = -1
                self.speak("Subtitle file loaded successfully")
            except Exception:
                self.speak("Failed to load subtitle file")
        dlg.Destroy()

    def on_exit(self, event):
        self.Close()

    def on_toggle_fullscreen(self, event):
        is_fs = self.IsFullScreen()
        self.ShowFullScreen(not is_fs)
        self.speak("Fullscreen enabled" if not is_fs else "Fullscreen disabled")

    def on_preferences(self, event):
        self.speak("Preferences dialog coming soon")

    def on_show_context_menu(self, event):
        menu = wx.Menu()
        menu.Append(self.ID_OPEN_VIDEO, "Open Video...")
        menu.Append(self.ID_OPEN_SUB, "Open Subtitle (.srt)...")
        menu.AppendSeparator()
        menu.Append(self.ID_FULLSCREEN, "Toggle Fullscreen")
        self.PopupMenu(menu)
        menu.Destroy()

    def on_timer_tick(self, event):
        if not self.player.is_playing() or not self.srt_subtitles:
            return
            
        current_time_ms = self.player.get_time()
        
        # Cari baris subtitle yang mencakup waktu putar saat ini secara akurat
        found_sub = None
        for sub in self.srt_subtitles:
            start_ms = sub.start.ordinal
            end_ms = sub.end.ordinal
            if start_ms <= current_time_ms <= end_ms:
                found_sub = sub
                break
                
        if found_sub and found_sub.index != self.current_sub_index:
            self.current_sub_index = found_sub.index
            clean_text = found_sub.text_without_tags.replace('\n', ' ')
            self.speak(clean_text)
        elif not found_sub:
            # Reset index jika sedang tidak ada dialog subtitle pada detik tersebut
            self.current_sub_index = -1

    def on_toggle_play(self, event):
        if self.player.is_playing():
            self.player.pause()
            self.speak("Paused")
        else:
            self.player.play()
            self.speak("Playing")

    def on_forward(self, event):
        new_time = self.player.get_time() + 5000
        self.player.set_time(new_time)
        self.speak("Forward 5 seconds")

    def on_rewind(self, event):
        new_time = max(0, self.player.get_time() - 5000)
        self.player.set_time(new_time)
        self.speak("Rewind 5 seconds")

    def on_volume_up(self, event):
        vol = min(100, self.player.audio_get_volume() + 5)
        self.player.audio_set_volume(vol)
        self.speak(f"Volume {vol} percent")

    def on_volume_down(self, event):
        vol = max(0, self.player.audio_get_volume() - 5)
        self.player.audio_set_volume(vol)
        self.speak(f"Volume {vol} percent")

if __name__ == '__main__':
    app = wx.App()
    frame = AsplayerWindow()
    frame.Show()
    app.MainLoop()