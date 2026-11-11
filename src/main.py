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
        
        # Variabel Subtitle
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
        
        # Buat ID unik untuk shortcut keyboard agar tertangkap secara global di jendela
        self.ID_PLAY = wx.NewIdRef()
        self.ID_RIGHT = wx.NewIdRef()
        self.ID_LEFT = wx.NewIdRef()
        self.ID_UP = wx.NewIdRef()
        self.ID_DOWN = wx.NewIdRef()
        
        # Bind event menu/accelerator ke fungsi masing-masing
        self.Bind(wx.EVT_MENU, self.on_toggle_play, id=self.ID_PLAY)
        self.Bind(wx.EVT_MENU, self.on_forward, id=self.ID_RIGHT)
        self.Bind(wx.EVT_MENU, self.on_rewind, id=self.ID_LEFT)
        self.Bind(wx.EVT_MENU, self.on_volume_up, id=self.ID_UP)
        self.Bind(wx.EVT_MENU, self.on_volume_down, id=self.ID_DOWN)
        
        # Daftarkan kombinasi shortcut keyboard (Accelerator Table)
        accel_entries = [
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, ord(' '), self.ID_PLAY),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_RIGHT, self.ID_RIGHT),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_LEFT, self.ID_LEFT),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_UP, self.ID_UP),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_DOWN, self.ID_DOWN),
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

    def open_video(self, path):
        media = self.vlc_instance.media_new(path)
        self.player.set_media(media)
        self.player.play()
        self.speak("Playing video")

    def open_srt(self, path):
        try:
            self.srt_subtitles = pysrt.open(path, encoding='utf-8')
            self.speak("Subtitle file loaded successfully")
        except Exception as e:
            self.speak("Failed to load subtitle file")

    def on_timer_tick(self, event):
        if not self.player.is_playing() or not self.srt_subtitles:
            return
            
        current_time_ms = self.player.get_time()
        sub = self.srt_subtitles.at(milliseconds=current_time_ms)
        
        if sub and sub.index != self.current_sub_index:
            self.current_sub_index = sub.index
            clean_text = sub.text_without_tags.replace('\n', ' ')
            self.speak(clean_text)

    # Handler Shortcut Keyboard
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