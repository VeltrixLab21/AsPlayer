import os
import json
import threading
import wx
import vlc
import pysrt
import pyttsx3
import accessible_output2.outputs.auto


VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov', '.webm', '.ts', '.flv', '.wmv', '.m4v')

TRANSLATIONS = {
    "en": {
        "menu_file": "&File",
        "menu_open": "&Open",
        "open_file": "Open File...\tCtrl+O",
        "open_folder": "Open Folder...\tCtrl+Shift+O",
        "open_url": "Open URL...\tCtrl+U",
        "open_sub": "Open Subtitle (.srt)...\tAlt+O",
        "playlist_mgr": "Playlist Manager...\tCtrl+L",
        "media_info": "Media Information...\tCtrl+I",
        "exit": "Exit\tAlt+F4",
        "menu_view": "&View",
        "fs_keep_ar": "Fullscreen (Keep AR)\tF11",
        "fs_stretch": "Fullscreen (Stretch)\tCtrl+Enter",
        "menu_playback": "&Playback",
        "play_pause": "Play / Pause\tSpace",
        "stop": "Stop\tCtrl+S",
        "rew_5s": "Rewind 5 Seconds\tLeft",
        "fwd_5s": "Fast Forward 5 Seconds\tRight",
        "next_item": "Play Next Item\tPage Down",
        "prev_item": "Play Previous Item\tPage Up",
        "jump_to": "&Jump To",
        "jump_rew_30s": "Jump Backward 30 Seconds\tCtrl+Left",
        "jump_fwd_30s": "Jump Forward 30 Seconds\tCtrl+Right",
        "jump_rew_1m": "Jump Backward 1 Minute\tShift+Left",
        "jump_fwd_1m": "Jump Forward 1 Minute\tShift+Right",
        "jump_rew_5m": "Jump Backward 5 Minutes\tCtrl+PgUp",
        "jump_fwd_5m": "Jump Forward 5 Minutes\tCtrl+PgDn",
        "volume": "&Volume",
        "vol_up": "Volume Up\tUp",
        "vol_down": "Volume Down\tDown",
        "vol_mute": "Mute / Unmute\tM",
        "resume_pos": "Resume from Last Position",
        "menu_tools": "&Tools",
        "sub_menu": "Subtitle Menu",
        "sub_toggle": "Show / Hide Subtitle",
        "sub_appearance": "Subtitle Appearance Settings...",
        "sub_sync_menu": "Subtitle Sync Menu",
        "sub_inc_05": "Increase subtitle 0.5 second\t>",
        "sub_dec_05": "Decrease subtitle 0.5 second\t<",
        "sub_inc_5": "Increase subtitle 5 second\tCtrl+>",
        "sub_dec_5": "Decrease subtitle 5 second\tCtrl+<",
        "sub_inc_50": "Increase subtitle 50 second\tShift+>",
        "sub_dec_50": "Decrease subtitle 50 second\tShift+<",
        "sub_apply_current": "Apply to current line only",
        "sub_reset": "Reset Subtitle Sync to Default",
        "sub_pos_bottom": "Position: Bottom",
        "sub_pos_top": "Position: Top",
        "sub_app_title": "Subtitle Appearance - ASPlayer",
        "sub_size_lbl": "Font Size:",
        "sub_color_lbl": "Text Color:",
        "sub_bg_lbl": "Background Color:",
        "acc_menu": "Accessibility",
        "tts_settings": "Speech & TTS Settings...",
        "acc_dialog_title": "Accessibility & TTS Settings - ASPlayer",
        "tts_engine_label": "Subtitle Speech Output Engine:",
        "tts_screen_reader": "System Screen Reader (NVDA / JAWS - Default)",
        "tts_sapi5": "Built-in Windows TTS (SAPI5)",
        "tts_voice_label": "TTS Voice:",
        "tts_rate_label": "Speech Rate (Speed):",
        "tts_vol_label": "Speech Volume (%):",
        "tts_test_btn": "&Test Voice",
        "tts_test_phrase": "This is a test of the ASPlayer subtitle voice settings.",
        "preferences": "Preferences...\tCtrl+Shift+P",
        "about_menu": "About ASPlayer...",
        "paused": "Paused",
        "playing": "Playing",
        "stopped": "Stopped",
        "no_media": "No media currently loaded.",
        "media_info_title": "Media Information - ASPlayer",
        "about_title": "About ASPlayer",
        "prefs_title": "Preferences - ASPlayer",
        "prefs_saved": "Preferences saved. Some changes will fully apply on next restart.",
        "startup_behavior": "Startup Playback Behavior:",
        "play_beginning": "Always play from beginning",
        "resume_watched": "Resume from last watched position",
        "app_language": "Application Language:",
        "app_theme": "Application Theme:",
        "theme_dark": "Cinema Dark (Default)",
        "theme_midnight": "Midnight Blue",
        "theme_oled": "OLED Pitch Black",
        "save": "Save",
        "cancel": "Cancel",
        "close": "Close",
        "playlist_title": "Playlist Manager - ASPlayer",
        "playlist_lbl": "Playlist Items (Press Enter to play selected item):",
        "playlist_add": "&Add Files...",
        "playlist_remove": "&Remove Selected",
        "playlist_clear": "&Clear All",
        "playlist_play": "&Play Selected",
        "about_content": (
            "ASPlayer v1.0\n"
            "Professional Accessible Windows Media Player\n\n"
            "Designed and optimized for screen reader users (NVDA & JAWS),\n"
            "featuring built-in SAPI5 TTS, subtitle sync,\n"
            "and native Windows installer support."
        )
    },
    "id": {
        "menu_file": "&Berkas",
        "menu_open": "&Buka",
        "open_file": "Buka Berkas...\tCtrl+O",
        "open_folder": "Buka Folder...\tCtrl+Shift+O",
        "open_url": "Buka URL...\tCtrl+U",
        "open_sub": "Buka Subtitle (.srt)...\tAlt+O",
        "playlist_mgr": "Pengelola Daftar Putar...\tCtrl+L",
        "media_info": "Informasi Media...\tCtrl+I",
        "exit": "Keluar\tAlt+F4",
        "menu_view": "&Tampilan",
        "fs_keep_ar": "Layar Penuh (Rasio Asli)\tF11",
        "fs_stretch": "Layar Penuh (Penuh)\tCtrl+Enter",
        "menu_playback": "&Pemutaran",
        "play_pause": "Putar / Jeda\tSpace",
        "stop": "Berhenti\tCtrl+S",
        "rew_5s": "Mundur 5 Detik\tLeft",
        "fwd_5s": "Maju 5 Detik\tRight",
        "next_item": "Item Berikutnya\tPage Down",
        "prev_item": "Item Sebelumnya\tPage Up",
        "jump_to": "&Lompat Ke",
        "jump_rew_30s": "Mundur 30 Detik\tCtrl+Left",
        "jump_fwd_30s": "Maju 30 Detik\tCtrl+Right",
        "jump_rew_1m": "Mundur 1 Menit\tShift+Left",
        "jump_fwd_1m": "Maju 1 Menit\tShift+Right",
        "jump_rew_5m": "Mundur 5 Menit\tCtrl+PgUp",
        "jump_fwd_5m": "Maju 5 Menit\tCtrl+PgDn",
        "volume": "&Volume",
        "vol_up": "Naikkan Volume\tUp",
        "vol_down": "Turunkan Volume\tDown",
        "vol_mute": "Bisukan / Bunyikan\tM",
        "resume_pos": "Lanjutkan dari Posisi Terakhir",
        "menu_tools": "&Alat",
        "sub_menu": "Menu Subtitle",
        "sub_toggle": "Tampilkan / Sembunyikan Subtitle",
        "sub_appearance": "Pengaturan Tampilan Subtitle...",
        "sub_sync_menu": "Sinkronisasi Subtitle",
        "sub_inc_05": "Majukan subtitle 0,5 detik\t>",
        "sub_dec_05": "Mundurkan subtitle 0,5 detik\t<",
        "sub_inc_5": "Majukan subtitle 5 detik\tCtrl+>",
        "sub_dec_5": "Mundurkan subtitle 5 detik\tCtrl+<",
        "sub_inc_50": "Majukan subtitle 50 detik\tShift+>",
        "sub_dec_50": "Mundurkan subtitle 50 detik\tShift+<",
        "sub_apply_current": "Terapkan hanya pada baris saat ini",
        "sub_reset": "Atur Ulang Sinkronisasi Subtitle",
        "sub_pos_bottom": "Posisi: Bawah",
        "sub_pos_top": "Posisi: Atas",
        "sub_app_title": "Tampilan Subtitle - ASPlayer",
        "sub_size_lbl": "Ukuran Huruf:",
        "sub_color_lbl": "Warna Teks:",
        "sub_bg_lbl": "Warna Latar Belakang:",
        "acc_menu": "Aksesibilitas",
        "tts_settings": "Pengaturan Suara & TTS...",
        "acc_dialog_title": "Pengaturan Aksesibilitas & TTS - ASPlayer",
        "tts_engine_label": "Mesin Keluaran Suara Subtitle:",
        "tts_screen_reader": "Pembaca Layar Sistem (NVDA / JAWS - Standar)",
        "tts_sapi5": "TTS Windows Bawaan (SAPI5)",
        "tts_voice_label": "Pilihan Suara TTS:",
        "tts_rate_label": "Kecepatan Bicara:",
        "tts_vol_label": "Volume Suara (%):",
        "tts_test_btn": "&Uji Suara",
        "tts_test_phrase": "Ini adalah pengujian pengaturan suara subtitle ASPlayer.",
        "preferences": "Preferensi...\tCtrl+Shift+P",
        "about_menu": "Tentang ASPlayer...",
        "paused": "Dijeda",
        "playing": "Memutar",
        "stopped": "Dihentikan",
        "no_media": "Belum ada media yang dimuat.",
        "media_info_title": "Informasi Media - ASPlayer",
        "about_title": "Tentang ASPlayer",
        "prefs_title": "Preferensi - ASPlayer",
        "prefs_saved": "Preferensi disimpan. Beberapa perubahan akan diterapkan sepenuhnya setelah restart.",
        "startup_behavior": "Perilaku Pemutaran Saat Awal:",
        "play_beginning": "Selalu putar dari awal",
        "resume_watched": "Lanjutkan dari posisi terakhir ditonton",
        "app_language": "Bahasa Aplikasi:",
        "app_theme": "Tema Aplikasi:",
        "theme_dark": "Cinema Dark (Standar)",
        "theme_midnight": "Midnight Blue",
        "theme_oled": "OLED Pitch Black",
        "save": "Simpan",
        "cancel": "Batal",
        "close": "Tutup",
        "playlist_title": "Pengelola Daftar Putar - ASPlayer",
        "playlist_lbl": "Item Daftar Putar (Tekan Enter untuk memutar item yang dipilih):",
        "playlist_add": "&Tambah Berkas...",
        "playlist_remove": "&Hapus Terpilih",
        "playlist_clear": "&Bersihkan Semua",
        "playlist_play": "&Putar Terpilih",
        "about_content": (
            "ASPlayer v1.0\n"
            "Pemutar Media Windows Profesional yang Aksesibel\n\n"
            "Dirancang dan dioptimalkan untuk pengguna pembaca layar (NVDA & JAWS),\n"
            "dilengkapi TTS SAPI5 bawaan, sinkronisasi subtitle,\n"
            "serta dukungan pemasang asli Windows."
        )
    }
}


class SubtitleAppearanceDialog(wx.Dialog):
    def __init__(self, parent, sub_style, current_lang="en"):
        tr = TRANSLATIONS[current_lang]
        super().__init__(parent, title=tr["sub_app_title"], size=(400, 300))
        self.sub_style = dict(sub_style)
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Font Size
        lbl_size = wx.StaticText(panel, label=tr["sub_size_lbl"])
        sizer.Add(lbl_size, 0, wx.ALL, 8)
        self.size_choices = ["Small", "Normal", "Large", "Extra Large"]
        self.size_choice = wx.Choice(panel, choices=self.size_choices)
        
        current_size = self.sub_style.get("font_size", "Normal")
        if current_size in self.size_choices:
            self.size_choice.SetStringSelection(current_size)
        else:
            self.size_choice.SetSelection(1)
        sizer.Add(self.size_choice, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        
        # Text Color
        lbl_color = wx.StaticText(panel, label=tr["sub_color_lbl"])
        sizer.Add(lbl_color, 0, wx.ALL, 8)
        self.color_choices = ["White", "Yellow", "Green", "Cyan", "Red"]
        self.color_choice = wx.Choice(panel, choices=self.color_choices)
        
        current_color = self.sub_style.get("text_color", "White")
        if current_color in self.color_choices:
            self.color_choice.SetStringSelection(current_color)
        else:
            self.color_choice.SetSelection(0)
        sizer.Add(self.color_choice, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        
        # Background Color
        lbl_bg = wx.StaticText(panel, label=tr["sub_bg_lbl"])
        sizer.Add(lbl_bg, 0, wx.ALL, 8)
        self.bg_choices = ["Transparent", "Black Translucent", "Solid Black"]
        self.bg_choice = wx.Choice(panel, choices=self.bg_choices)
        
        current_bg = self.sub_style.get("bg_color", "Black Translucent")
        if current_bg in self.bg_choices:
            self.bg_choice.SetStringSelection(current_bg)
        else:
            self.bg_choice.SetSelection(1)
        sizer.Add(self.bg_choice, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)
        
        # Buttons
        btn_sizer = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(panel, wx.ID_OK, tr["save"])
        btn_cancel = wx.Button(panel, wx.ID_CANCEL, tr["cancel"])
        btn_sizer.AddButton(btn_ok)
        btn_sizer.AddButton(btn_cancel)
        btn_sizer.Realize()
        
        sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 10)
        panel.SetSizer(sizer)
        self.CenterOnParent()

    def get_style(self):
        return {
            "font_size": self.size_choices[self.size_choice.GetSelection()],
            "text_color": self.color_choices[self.color_choice.GetSelection()],
            "bg_color": self.bg_choices[self.bg_choice.GetSelection()]
        }


class MediaInfoDialog(wx.Dialog):
    def __init__(self, parent, info_text, current_lang="en"):
        title = TRANSLATIONS[current_lang]["media_info_title"]
        close_lbl = TRANSLATIONS[current_lang]["close"]
        super().__init__(parent, title=title, size=(480, 350))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.txt_info = wx.TextCtrl(
            panel,
            value=info_text,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2
        )
        sizer.Add(self.txt_info, 1, wx.EXPAND | wx.ALL, 12)

        btn_close = wx.Button(panel, wx.ID_CLOSE, close_lbl)
        btn_close.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CLOSE))
        sizer.Add(btn_close, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, 12)

        panel.SetSizer(sizer)
        self.txt_info.SetFocus()
        self.CenterOnParent()


class AboutDialog(wx.Dialog):
    def __init__(self, parent, current_lang="en"):
        title_str = TRANSLATIONS[current_lang]["about_title"]
        about_text = TRANSLATIONS[current_lang]["about_content"]
        
        super().__init__(parent, title=title_str, size=(450, 280))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.txt_about = wx.TextCtrl(
            panel,
            value=about_text,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.NO_BORDER
        )
        self.txt_about.SetBackgroundColour(panel.GetBackgroundColour())
        sizer.Add(self.txt_about, 1, wx.EXPAND | wx.ALL, 15)

        btn_ok = wx.Button(panel, wx.ID_OK, "OK")
        btn_ok.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_OK))
        sizer.Add(btn_ok, 0, wx.ALIGN_CENTER | wx.BOTTOM, 15)

        panel.SetSizer(sizer)
        btn_ok.SetFocus()
        self.CenterOnParent()


class AccessibilityDialog(wx.Dialog):
    def __init__(self, parent, acc_config, current_lang="en"):
        self.current_lang = current_lang
        tr = TRANSLATIONS[current_lang]
        super().__init__(parent, title=tr["acc_dialog_title"], size=(460, 380))
        self.acc_config = dict(acc_config)
        
        self.voices_list = []
        try:
            temp_engine = pyttsx3.init()
            voices = temp_engine.getProperty('voices')
            for v in voices:
                self.voices_list.append((v.id, v.name))
            temp_engine.stop()
        except Exception:
            pass

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        lbl_engine = wx.StaticText(panel, label=tr["tts_engine_label"])
        sizer.Add(lbl_engine, 0, wx.ALL, 10)

        self.rb_screen_reader = wx.RadioButton(panel, label=tr["tts_screen_reader"], style=wx.RB_GROUP)
        self.rb_sapi_tts = wx.RadioButton(panel, label=tr["tts_sapi5"])

        if self.acc_config.get("tts_engine", "screen_reader") == "sapi5":
            self.rb_sapi_tts.SetValue(True)
        else:
            self.rb_screen_reader.SetValue(True)

        sizer.Add(self.rb_screen_reader, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        sizer.Add(self.rb_sapi_tts, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.tts_panel = wx.Panel(panel)
        tts_sizer = wx.BoxSizer(wx.VERTICAL)

        lbl_voice = wx.StaticText(self.tts_panel, label=tr["tts_voice_label"])
        tts_sizer.Add(lbl_voice, 0, wx.BOTTOM, 3)

        voice_names = [v[1] for v in self.voices_list] if self.voices_list else ["Default System Voice"]
        self.choice_voice = wx.Choice(self.tts_panel, choices=voice_names)
        
        saved_voice_id = self.acc_config.get("tts_voice_id", "")
        selected_idx = 0
        for idx, (vid, _) in enumerate(self.voices_list):
            if vid == saved_voice_id:
                selected_idx = idx
                break
        self.choice_voice.SetSelection(selected_idx)
        tts_sizer.Add(self.choice_voice, 0, wx.EXPAND | wx.BOTTOM, 10)

        lbl_rate = wx.StaticText(self.tts_panel, label=tr["tts_rate_label"])
        tts_sizer.Add(lbl_rate, 0, wx.BOTTOM, 3)
        self.slider_rate = wx.Slider(self.tts_panel, value=self.acc_config.get("tts_rate", 200), minValue=100, maxValue=400, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        tts_sizer.Add(self.slider_rate, 0, wx.EXPAND | wx.BOTTOM, 10)

        lbl_vol = wx.StaticText(self.tts_panel, label=tr["tts_vol_label"])
        tts_sizer.Add(lbl_vol, 0, wx.BOTTOM, 3)
        self.slider_vol = wx.Slider(self.tts_panel, value=self.acc_config.get("tts_volume", 100), minValue=0, maxValue=100, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        tts_sizer.Add(self.slider_vol, 0, wx.EXPAND | wx.BOTTOM, 5)

        self.tts_panel.SetSizer(tts_sizer)
        sizer.Add(self.tts_panel, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)

        btn_sizer = wx.StdDialogButtonSizer()
        self.btn_test = wx.Button(panel, label=tr["tts_test_btn"])
        btn_ok = wx.Button(panel, wx.ID_OK, tr["save"])
        btn_cancel = wx.Button(panel, wx.ID_CANCEL, tr["cancel"])

        btn_sizer.AddButton(btn_ok)
        btn_sizer.AddButton(btn_cancel)
        btn_sizer.Realize()

        bottom_row = wx.BoxSizer(wx.HORIZONTAL)
        bottom_row.Add(self.btn_test, 0, wx.ALL, 10)
        bottom_row.AddStretchSpacer()
        bottom_row.Add(btn_sizer, 0, wx.ALL, 10)

        sizer.Add(bottom_row, 0, wx.EXPAND)
        panel.SetSizer(sizer)

        self.rb_screen_reader.Bind(wx.EVT_RADIOBUTTON, self.on_engine_changed)
        self.rb_sapi_tts.Bind(wx.EVT_RADIOBUTTON, self.on_engine_changed)
        self.btn_test.Bind(wx.EVT_BUTTON, self.on_test_voice)

        self.update_controls_state()
        self.CenterOnParent()

    def on_engine_changed(self, event):
        self.update_controls_state()

    def update_controls_state(self):
        is_sapi = self.rb_sapi_tts.GetValue()
        self.tts_panel.Enable(is_sapi)
        self.btn_test.Enable(is_sapi)

    def on_test_voice(self, event):
        rate = self.slider_rate.GetValue()
        vol = self.slider_vol.GetValue() / 100.0
        sel_idx = self.choice_voice.GetSelection()
        voice_id = self.voices_list[sel_idx][0] if (self.voices_list and sel_idx != wx.NOT_FOUND) else None
        test_phrase = TRANSLATIONS[self.current_lang]["tts_test_phrase"]

        def _speak_test():
            try:
                eng = pyttsx3.init()
                if voice_id:
                    eng.setProperty('voice', voice_id)
                eng.setProperty('rate', rate)
                eng.setProperty('volume', vol)
                eng.say(test_phrase)
                eng.runAndWait()
                eng.stop()
            except Exception:
                pass

        threading.Thread(target=_speak_test, daemon=True).start()

    def get_settings(self):
        engine = "sapi5" if self.rb_sapi_tts.GetValue() else "screen_reader"
        sel_idx = self.choice_voice.GetSelection()
        voice_id = self.voices_list[sel_idx][0] if (self.voices_list and sel_idx != wx.NOT_FOUND) else ""
        return {
            "tts_engine": engine,
            "tts_voice_id": voice_id,
            "tts_rate": self.slider_rate.GetValue(),
            "tts_volume": self.slider_vol.GetValue()
        }


class PreferencesDialog(wx.Dialog):
    def __init__(self, parent, resume_enabled, current_lang, current_theme):
        title_str = TRANSLATIONS[current_lang]["prefs_title"]
        super().__init__(parent, title=title_str, size=(440, 360))
        self.resume_enabled = resume_enabled
        self.current_lang = current_lang
        self.current_theme = current_theme
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.lbl_resume_heading = wx.StaticText(panel, label=TRANSLATIONS[current_lang]["startup_behavior"])
        sizer.Add(self.lbl_resume_heading, 0, wx.ALL, 10)
        
        self.rb_beginning = wx.RadioButton(panel, label=TRANSLATIONS[current_lang]["play_beginning"], style=wx.RB_GROUP)
        self.rb_resume = wx.RadioButton(panel, label=TRANSLATIONS[current_lang]["resume_watched"])
        
        if self.resume_enabled:
            self.rb_resume.SetValue(True)
        else:
            self.rb_beginning.SetValue(True)
            
        sizer.Add(self.rb_beginning, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        sizer.Add(self.rb_resume, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        self.lbl_lang_heading = wx.StaticText(panel, label=TRANSLATIONS[current_lang]["app_language"])
        sizer.Add(self.lbl_lang_heading, 0, wx.ALL, 10)
        
        self.lang_choices = ["English", "Bahasa Indonesia"]
        self.lang_choice_ctrl = wx.Choice(panel, choices=self.lang_choices)
        
        if self.current_lang == "id":
            self.lang_choice_ctrl.SetSelection(1)
        else:
            self.lang_choice_ctrl.SetSelection(0)
            
        sizer.Add(self.lang_choice_ctrl, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.lbl_theme_heading = wx.StaticText(panel, label=TRANSLATIONS[current_lang]["app_theme"])
        sizer.Add(self.lbl_theme_heading, 0, wx.ALL, 10)

        self.theme_choices = [
            TRANSLATIONS[current_lang]["theme_dark"],
            TRANSLATIONS[current_lang]["theme_midnight"],
            TRANSLATIONS[current_lang]["theme_oled"]
        ]
        self.theme_choice_ctrl = wx.Choice(panel, choices=self.theme_choices)
        
        theme_map = {"dark": 0, "midnight": 1, "oled": 2}
        self.theme_choice_ctrl.SetSelection(theme_map.get(self.current_theme, 0))
        sizer.Add(self.theme_choice_ctrl, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        btn_sizer = wx.StdDialogButtonSizer()
        self.btn_ok = wx.Button(panel, wx.ID_OK, TRANSLATIONS[current_lang]["save"])
        self.btn_cancel = wx.Button(panel, wx.ID_CANCEL, TRANSLATIONS[current_lang]["cancel"])
        btn_sizer.AddButton(self.btn_ok)
        btn_sizer.AddButton(self.btn_cancel)
        btn_sizer.Realize()
        
        sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 10)
        panel.SetSizer(sizer)
        self.CenterOnParent()

    def get_resume_setting(self):
        return self.rb_resume.GetValue()

    def get_language_setting(self):
        sel = self.lang_choice_ctrl.GetSelection()
        return "id" if sel == 1 else "en"

    def get_theme_setting(self):
        sel = self.theme_choice_ctrl.GetSelection()
        keys = ["dark", "midnight", "oled"]
        return keys[sel] if 0 <= sel < len(keys) else "dark"


class PlaylistDialog(wx.Dialog):
    def __init__(self, parent, playlist, current_index, current_lang="en"):
        self.current_lang = current_lang
        tr = TRANSLATIONS[current_lang]
        super().__init__(parent, title=tr["playlist_title"], size=(550, 400))
        self.parent_frame = parent
        self.playlist = list(playlist)
        self.current_index = current_index
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        lbl = wx.StaticText(panel, label=tr["playlist_lbl"])
        sizer.Add(lbl, 0, wx.ALL, 10)
        
        self.listbox = wx.ListBox(panel, style=wx.LB_SINGLE)
        self.refresh_list()
        sizer.Add(self.listbox, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_add = wx.Button(panel, label=tr["playlist_add"])
        self.btn_remove = wx.Button(panel, label=tr["playlist_remove"])
        self.btn_clear = wx.Button(panel, label=tr["playlist_clear"])
        self.btn_play = wx.Button(panel, label=tr["playlist_play"])
        self.btn_close = wx.Button(panel, wx.ID_CANCEL, tr["close"])
        
        btn_sizer.Add(self.btn_add, 0, wx.RIGHT, 5)
        btn_sizer.Add(self.btn_remove, 0, wx.RIGHT, 5)
        btn_sizer.Add(self.btn_clear, 0, wx.RIGHT, 5)
        btn_sizer.Add(self.btn_play, 0, wx.RIGHT, 5)
        btn_sizer.Add(self.btn_close, 0)
        
        sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        panel.SetSizer(sizer)
        
        self.btn_add.Bind(wx.EVT_BUTTON, self.on_add_files)
        self.btn_remove.Bind(wx.EVT_BUTTON, self.on_remove_item)
        self.btn_clear.Bind(wx.EVT_BUTTON, self.on_clear_all)
        self.btn_play.Bind(wx.EVT_BUTTON, self.on_play_selected)
        self.listbox.Bind(wx.EVT_LISTBOX_DCLICK, self.on_play_selected)
        self.listbox.Bind(wx.EVT_KEY_DOWN, self.on_list_key)
        
        self.listbox.SetFocus()
        self.CenterOnParent()

    def refresh_list(self):
        self.listbox.Clear()
        for idx, item in enumerate(self.playlist):
            name = os.path.basename(item) if not item.startswith(("http://", "https://")) else item
            prefix = "[Playing] " if idx == self.current_index else ""
            self.listbox.Append(f"{idx + 1}. {prefix}{name}")
        if 0 <= self.current_index < len(self.playlist):
            self.listbox.SetSelection(self.current_index)
        elif len(self.playlist) > 0:
            self.listbox.SetSelection(0)

    def on_add_files(self, event):
        wildcard = "Video Files (*.mp4;*.mkv;*.avi;*.mov;*.webm;*.ts)|*.mp4;*.mkv;*.avi;*.mov;*.webm;*.ts|All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Add Videos to Playlist", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            self.playlist.extend(paths)
            self.parent_frame.playlist = list(self.playlist)
            self.refresh_list()
            self.parent_frame.speak(f"Added {len(paths)} items to playlist")
        dlg.Destroy()

    def on_remove_item(self, event):
        sel = self.listbox.GetSelection()
        if sel != wx.NOT_FOUND:
            removed_name = os.path.basename(self.playlist[sel])
            self.playlist.pop(sel)
            if sel < self.current_index:
                self.current_index -= 1
            elif sel == self.current_index:
                self.current_index = -1
            self.parent_frame.playlist = list(self.playlist)
            self.parent_frame.playlist_index = self.current_index
            self.refresh_list()
            self.parent_frame.speak(f"Removed {removed_name}")

    def on_clear_all(self, event):
        self.playlist.clear()
        self.current_index = -1
        self.parent_frame.playlist = []
        self.parent_frame.playlist_index = -1
        self.refresh_list()
        self.parent_frame.speak("Playlist cleared")

    def on_play_selected(self, event):
        sel = self.listbox.GetSelection()
        if sel != wx.NOT_FOUND and sel < len(self.playlist):
            self.parent_frame.playlist = list(self.playlist)
            self.parent_frame.play_playlist_index(sel)
            self.EndModal(wx.ID_OK)

    def on_list_key(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_RETURN:
            self.on_play_selected(None)
        elif key == wx.WXK_DELETE:
            self.on_remove_item(None)
        else:
            event.Skip()


class AsplayerWindow(wx.Frame):
    def __init__(self):
        super().__init__(None, title="ASPlayer", size=(900, 600))
        
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asplayer_config.json")
        self.config = self.load_config()
        
        try:
            self.speech = accessible_output2.outputs.auto.Auto()
        except Exception:
            self.speech = None
            
        self.vlc_instance = vlc.Instance(
            "--no-video-title-show",
            "--no-osd",
            "--network-caching=3000",
            "--no-lua",
            "--quiet"
        )
        self.player = self.vlc_instance.media_player_new()
        
        self.current_video_path = None
        self.playlist = []
        self.playlist_index = -1
        self.srt_subtitles = None
        self.current_sub_index = -1
        self.pending_seek_time = 0
        self.was_playing = False
        
        self.sub_offset_ms = 0
        self.sub_enabled = True
        self.sub_position = 0
        self.per_line_offsets = {}
        self.sub_style = {
            "font_size": "Normal",
            "text_color": "White",
            "bg_color": "Black Translucent"
        }
        
        self.init_ui()
        self.apply_theme()
        self.init_timer()
        self.Bind(wx.EVT_CLOSE, self.on_window_close)
        self.Center()

    def tr(self, key):
        lang = self.config.get("language", "en")
        lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
        return lang_dict.get(key, TRANSLATIONS["en"].get(key, key))

    def load_config(self):
        default_cfg = {
            "resume_playback": True,
            "language": "en",
            "theme": "dark",
            "positions": {},
            "subtitles": {},
            "accessibility": {
                "tts_engine": "screen_reader",
                "tts_voice_id": "",
                "tts_rate": 200,
                "tts_volume": 100
            }
        }
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    for k, v in default_cfg.items():
                        if k not in loaded:
                            loaded[k] = v
                    return loaded
            except Exception:
                pass
        return default_cfg

    def save_config(self):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except Exception:
            pass

    def apply_theme(self):
        theme = self.config.get("theme", "dark")
        if theme == "midnight":
            bg_color = wx.Colour(15, 23, 42)
        elif theme == "oled":
            bg_color = wx.Colour(0, 0, 0)
        else:
            bg_color = wx.Colour(30, 30, 30)
            
        if hasattr(self, 'video_panel') and self.video_panel:
            self.video_panel.SetBackgroundColour(bg_color)
            self.video_panel.Refresh()

    def record_current_position(self):
        if self.current_video_path and not self.current_video_path.startswith(("http://", "https://")) and self.player:
            current_ms = self.player.get_time()
            total_ms = self.player.get_length()
            if current_ms > 3000 and (total_ms <= 0 or (total_ms - current_ms) > 5000):
                self.config["positions"][self.current_video_path] = current_ms
            elif total_ms > 0 and (total_ms - current_ms) <= 5000:
                self.config["positions"].pop(self.current_video_path, None)
            self.save_config()

    def save_current_subtitle_settings(self):
        if self.current_video_path and not self.current_video_path.startswith(("http://", "https://")):
            if "subtitles" not in self.config:
                self.config["subtitles"] = {}
            serialized_per_line = {str(k): v for k, v in self.per_line_offsets.items()}
            self.config["subtitles"][self.current_video_path] = {
                "offset_ms": self.sub_offset_ms,
                "enabled": self.sub_enabled,
                "position": self.sub_position,
                "per_line_offsets": serialized_per_line,
                "style": self.sub_style
            }
            self.save_config()

    def load_video_subtitle_settings(self, path):
        sub_cfg = self.config.get("subtitles", {}).get(path, {})
        self.sub_offset_ms = sub_cfg.get("offset_ms", 0)
        self.sub_enabled = sub_cfg.get("enabled", True)
        self.sub_position = sub_cfg.get("position", 0)
        raw_per_line = sub_cfg.get("per_line_offsets", {})
        self.per_line_offsets = {int(k): v for k, v in raw_per_line.items()}
        self.sub_style = sub_cfg.get("style", {
            "font_size": "Normal",
            "text_color": "White",
            "bg_color": "Black Translucent"
        })

    def init_ui(self):
        panel = wx.Panel(self)
        
        self.video_panel = wx.Panel(panel)
        self.video_panel.SetBackgroundColour(wx.BLACK)
        self.video_panel.SetName("Video Viewport")
        self.video_panel.SetCanFocus(False)
        panel.SetFocus()
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.video_panel, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        
        menubar = wx.MenuBar()
        
        # Menu File
        file_menu = wx.Menu()
        open_submenu = wx.Menu()
        
        self.ID_OPEN_VIDEO = wx.NewIdRef()
        self.ID_OPEN_FOLDER = wx.NewIdRef()
        self.ID_OPEN_URL = wx.NewIdRef()
        self.ID_OPEN_SUB = wx.NewIdRef()
        self.ID_PLAYLIST = wx.NewIdRef()
        self.ID_MEDIA_INFO = wx.NewIdRef()
        self.ID_EXIT = wx.NewIdRef()
        
        open_submenu.Append(self.ID_OPEN_VIDEO, self.tr("open_file"))
        open_submenu.Append(self.ID_OPEN_FOLDER, self.tr("open_folder"))
        open_submenu.Append(self.ID_OPEN_URL, self.tr("open_url"))
        
        file_menu.AppendSubMenu(open_submenu, self.tr("menu_open"))
        file_menu.Append(self.ID_OPEN_SUB, self.tr("open_sub"))
        file_menu.AppendSeparator()
        file_menu.Append(self.ID_PLAYLIST, self.tr("playlist_mgr"))
        file_menu.Append(self.ID_MEDIA_INFO, self.tr("media_info"))
        file_menu.AppendSeparator()
        file_menu.Append(self.ID_EXIT, self.tr("exit"))
        
        # Menu View
        view_menu = wx.Menu()
        self.ID_FS_KEEP_AR = wx.NewIdRef()
        self.ID_FS_STRETCH = wx.NewIdRef()
        
        view_menu.Append(self.ID_FS_KEEP_AR, self.tr("fs_keep_ar"))
        view_menu.Append(self.ID_FS_STRETCH, self.tr("fs_stretch"))
        
        # Menu Playback
        playback_menu = wx.Menu()
        self.ID_PB_PLAYPAUSE = wx.NewIdRef()
        self.ID_PB_STOP = wx.NewIdRef()
        self.ID_PB_REWIND = wx.NewIdRef()
        self.ID_PB_FORWARD = wx.NewIdRef()
        self.ID_PB_NEXT = wx.NewIdRef()
        self.ID_PB_PREV = wx.NewIdRef()
        self.ID_PB_TOGGLE_RESUME = wx.NewIdRef()
        
        playback_menu.Append(self.ID_PB_PLAYPAUSE, self.tr("play_pause"))
        playback_menu.Append(self.ID_PB_STOP, self.tr("stop"))
        playback_menu.Append(self.ID_PB_REWIND, self.tr("rew_5s"))
        playback_menu.Append(self.ID_PB_FORWARD, self.tr("fwd_5s"))
        playback_menu.AppendSeparator()
        
        playback_menu.Append(self.ID_PB_NEXT, self.tr("next_item"))
        playback_menu.Append(self.ID_PB_PREV, self.tr("prev_item"))
        playback_menu.AppendSeparator()
        
        jump_submenu = wx.Menu()
        self.ID_JUMP_REW_30S = wx.NewIdRef()
        self.ID_JUMP_FWD_30S = wx.NewIdRef()
        self.ID_JUMP_REW_1M = wx.NewIdRef()
        self.ID_JUMP_FWD_1M = wx.NewIdRef()
        self.ID_JUMP_REW_5M = wx.NewIdRef()
        self.ID_JUMP_FWD_5M = wx.NewIdRef()
        
        jump_submenu.Append(self.ID_JUMP_REW_30S, self.tr("jump_rew_30s"))
        jump_submenu.Append(self.ID_JUMP_FWD_30S, self.tr("jump_fwd_30s"))
        jump_submenu.Append(self.ID_JUMP_REW_1M, self.tr("jump_rew_1m"))
        jump_submenu.Append(self.ID_JUMP_FWD_1M, self.tr("jump_fwd_1m"))
        jump_submenu.Append(self.ID_JUMP_REW_5M, self.tr("jump_rew_5m"))
        jump_submenu.Append(self.ID_JUMP_FWD_5M, self.tr("jump_fwd_5m"))
        
        playback_menu.AppendSubMenu(jump_submenu, self.tr("jump_to"))
        
        volume_submenu = wx.Menu()
        self.ID_VOL_UP = wx.NewIdRef()
        self.ID_VOL_DOWN = wx.NewIdRef()
        self.ID_VOL_MUTE = wx.NewIdRef()
        
        volume_submenu.Append(self.ID_VOL_UP, self.tr("vol_up"))
        volume_submenu.Append(self.ID_VOL_DOWN, self.tr("vol_down"))
        volume_submenu.Append(self.ID_VOL_MUTE, self.tr("vol_mute"))
        
        playback_menu.AppendSubMenu(volume_submenu, self.tr("volume"))
        playback_menu.AppendSeparator()
        
        self.menu_resume_item = playback_menu.AppendCheckItem(
            self.ID_PB_TOGGLE_RESUME,
            self.tr("resume_pos")
        )
        self.menu_resume_item.Check(self.config.get("resume_playback", True))
        
        # Menu Tools
        tools_menu = wx.Menu()
        
        sub_settings_menu = wx.Menu()
        self.ID_SUB_TOGGLE = wx.NewIdRef()
        self.ID_SUB_APPEARANCE = wx.NewIdRef()
        self.ID_SUB_POS_BOTTOM = wx.NewIdRef()
        self.ID_SUB_POS_TOP = wx.NewIdRef()
        
        sub_sync_menu = wx.Menu()
        self.ID_SUB_INC_05 = wx.NewIdRef()
        self.ID_SUB_DEC_05 = wx.NewIdRef()
        self.ID_SUB_INC_5 = wx.NewIdRef()
        self.ID_SUB_DEC_5 = wx.NewIdRef()
        self.ID_SUB_INC_50 = wx.NewIdRef()
        self.ID_SUB_DEC_50 = wx.NewIdRef()
        self.ID_SUB_RESET_SYNC = wx.NewIdRef()
        
        sub_sync_menu.Append(self.ID_SUB_INC_05, self.tr("sub_inc_05"))
        sub_sync_menu.Append(self.ID_SUB_DEC_05, self.tr("sub_dec_05"))
        sub_sync_menu.Append(self.ID_SUB_INC_5, self.tr("sub_inc_5"))
        sub_sync_menu.Append(self.ID_SUB_DEC_5, self.tr("sub_dec_5"))
        sub_sync_menu.Append(self.ID_SUB_INC_50, self.tr("sub_inc_50"))
        sub_sync_menu.Append(self.ID_SUB_DEC_50, self.tr("sub_dec_50"))
        sub_sync_menu.AppendSeparator()
        
        self.ID_SUB_APPLY_CURRENT_ONLY = wx.NewIdRef()
        self.menu_apply_current_item = sub_sync_menu.AppendCheckItem(
            self.ID_SUB_APPLY_CURRENT_ONLY,
            self.tr("sub_apply_current")
        )
        sub_sync_menu.AppendSeparator()
        sub_sync_menu.Append(self.ID_SUB_RESET_SYNC, self.tr("sub_reset"))
        
        self.menu_sub_toggle_item = sub_settings_menu.AppendCheckItem(self.ID_SUB_TOGGLE, self.tr("sub_toggle"))
        self.menu_sub_toggle_item.Check(True)
        
        sub_settings_menu.Append(self.ID_SUB_APPEARANCE, self.tr("sub_appearance"))
        sub_settings_menu.AppendSeparator()
        sub_settings_menu.AppendSubMenu(sub_sync_menu, self.tr("sub_sync_menu"))
        sub_settings_menu.AppendSeparator()
        sub_settings_menu.Append(self.ID_SUB_POS_BOTTOM, self.tr("sub_pos_bottom"))
        sub_settings_menu.Append(self.ID_SUB_POS_TOP, self.tr("sub_pos_top"))
        
        tools_menu.AppendSubMenu(sub_settings_menu, self.tr("sub_menu"))
        tools_menu.AppendSeparator()
        
        accessibility_menu = wx.Menu()
        self.ID_ACC_TTS_SETTINGS = wx.NewIdRef()
        accessibility_menu.Append(self.ID_ACC_TTS_SETTINGS, self.tr("tts_settings"))
        
        tools_menu.AppendSubMenu(accessibility_menu, self.tr("acc_menu"))
        tools_menu.AppendSeparator()
        
        self.ID_PREFERENCES = wx.NewIdRef()
        self.ID_ABOUT = wx.NewIdRef()
        tools_menu.Append(self.ID_PREFERENCES, self.tr("preferences"))
        tools_menu.AppendSeparator()
        tools_menu.Append(self.ID_ABOUT, self.tr("about_menu"))
        
        menubar.Append(file_menu, self.tr("menu_file"))
        menubar.Append(view_menu, self.tr("menu_view"))
        menubar.Append(playback_menu, self.tr("menu_playback"))
        menubar.Append(tools_menu, self.tr("menu_tools"))
        self.SetMenuBar(menubar)
        
        # Event Bindings
        self.Bind(wx.EVT_MENU, self.on_open_video_dialog, id=self.ID_OPEN_VIDEO)
        self.Bind(wx.EVT_MENU, self.on_open_folder_dialog, id=self.ID_OPEN_FOLDER)
        self.Bind(wx.EVT_MENU, self.on_open_url_dialog, id=self.ID_OPEN_URL)
        self.Bind(wx.EVT_MENU, self.on_open_sub_dialog, id=self.ID_OPEN_SUB)
        self.Bind(wx.EVT_MENU, self.on_open_playlist_dialog, id=self.ID_PLAYLIST)
        self.Bind(wx.EVT_MENU, self.on_announce_status, id=self.ID_MEDIA_INFO)
        self.Bind(wx.EVT_MENU, self.on_exit, id=self.ID_EXIT)
        
        self.Bind(wx.EVT_MENU, self.on_fullscreen_keep_ar, id=self.ID_FS_KEEP_AR)
        self.Bind(wx.EVT_MENU, self.on_fullscreen_stretch, id=self.ID_FS_STRETCH)
        
        self.Bind(wx.EVT_MENU, self.on_toggle_play, id=self.ID_PB_PLAYPAUSE)
        self.Bind(wx.EVT_MENU, self.on_stop, id=self.ID_PB_STOP)
        self.Bind(wx.EVT_MENU, self.on_rewind, id=self.ID_PB_REWIND)
        self.Bind(wx.EVT_MENU, self.on_forward, id=self.ID_PB_FORWARD)
        
        self.Bind(wx.EVT_MENU, lambda e: self.jump_time(-30000, "Jumped backward 30 seconds"), id=self.ID_JUMP_REW_30S)
        self.Bind(wx.EVT_MENU, lambda e: self.jump_time(30000, "Jumped forward 30 seconds"), id=self.ID_JUMP_FWD_30S)
        self.Bind(wx.EVT_MENU, lambda e: self.jump_time(-60000, "Jumped backward 1 minute"), id=self.ID_JUMP_REW_1M)
        self.Bind(wx.EVT_MENU, lambda e: self.jump_time(60000, "Jumped forward 1 minute"), id=self.ID_JUMP_FWD_1M)
        self.Bind(wx.EVT_MENU, lambda e: self.jump_time(-300000, "Jumped backward 5 minutes"), id=self.ID_JUMP_REW_5M)
        self.Bind(wx.EVT_MENU, lambda e: self.jump_time(300000, "Jumped forward 5 minutes"), id=self.ID_JUMP_FWD_5M)
        
        self.Bind(wx.EVT_MENU, self.on_volume_up, id=self.ID_VOL_UP)
        self.Bind(wx.EVT_MENU, self.on_volume_down, id=self.ID_VOL_DOWN)
        self.Bind(wx.EVT_MENU, self.on_toggle_mute, id=self.ID_VOL_MUTE)
        
        self.Bind(wx.EVT_MENU, self.on_toggle_subtitle_visibility, id=self.ID_SUB_TOGGLE)
        self.Bind(wx.EVT_MENU, self.on_open_subtitle_appearance, id=self.ID_SUB_APPEARANCE)
        self.Bind(wx.EVT_MENU, lambda e: self.adjust_subtitle_sync(500), id=self.ID_SUB_INC_05)
        self.Bind(wx.EVT_MENU, lambda e: self.adjust_subtitle_sync(-500), id=self.ID_SUB_DEC_05)
        self.Bind(wx.EVT_MENU, lambda e: self.adjust_subtitle_sync(5000), id=self.ID_SUB_INC_5)
        self.Bind(wx.EVT_MENU, lambda e: self.adjust_subtitle_sync(-5000), id=self.ID_SUB_DEC_5)
        self.Bind(wx.EVT_MENU, lambda e: self.adjust_subtitle_sync(50000), id=self.ID_SUB_INC_50)
        self.Bind(wx.EVT_MENU, lambda e: self.adjust_subtitle_sync(-50000), id=self.ID_SUB_DEC_50)
        self.Bind(wx.EVT_MENU, self.on_reset_subtitle_sync, id=self.ID_SUB_RESET_SYNC)
        self.Bind(wx.EVT_MENU, lambda e: self.set_subtitle_position(0), id=self.ID_SUB_POS_BOTTOM)
        self.Bind(wx.EVT_MENU, lambda e: self.set_subtitle_position(1), id=self.ID_SUB_POS_TOP)
        
        self.Bind(wx.EVT_MENU, self.on_open_accessibility_dialog, id=self.ID_ACC_TTS_SETTINGS)
        
        self.Bind(wx.EVT_MENU, self.on_next_item, id=self.ID_PB_NEXT)
        self.Bind(wx.EVT_MENU, self.on_prev_item, id=self.ID_PB_PREV)
        self.Bind(wx.EVT_MENU, self.on_toggle_resume_mode, id=self.ID_PB_TOGGLE_RESUME)
        self.Bind(wx.EVT_MENU, self.on_preferences, id=self.ID_PREFERENCES)
        self.Bind(wx.EVT_MENU, self.on_about, id=self.ID_ABOUT)
        
        self.Bind(wx.EVT_CONTEXT_MENU, self.on_show_context_menu)
        self.video_panel.Bind(wx.EVT_CONTEXT_MENU, self.on_show_context_menu)

        accel_entries = [
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, ord(' '), self.ID_PB_PLAYPAUSE),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_RIGHT, self.ID_PB_FORWARD),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_LEFT, self.ID_PB_REWIND),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_LEFT, self.ID_JUMP_REW_30S),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_RIGHT, self.ID_JUMP_FWD_30S),
            wx.AcceleratorEntry(wx.ACCEL_SHIFT, wx.WXK_LEFT, self.ID_JUMP_REW_1M),
            wx.AcceleratorEntry(wx.ACCEL_SHIFT, wx.WXK_RIGHT, self.ID_JUMP_FWD_1M),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_PAGEUP, self.ID_JUMP_REW_5M),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_PAGEDOWN, self.ID_JUMP_FWD_5M),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_UP, self.ID_VOL_UP),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_DOWN, self.ID_VOL_DOWN),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, ord('m'), self.ID_VOL_MUTE),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('i'), self.ID_MEDIA_INFO),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_PAGEDOWN, self.ID_PB_NEXT),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_PAGEUP, self.ID_PB_PREV),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('o'), self.ID_OPEN_VIDEO),
            wx.AcceleratorEntry(wx.ACCEL_CTRL | wx.ACCEL_SHIFT, ord('o'), self.ID_OPEN_FOLDER),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('u'), self.ID_OPEN_URL),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('l'), self.ID_PLAYLIST),
            wx.AcceleratorEntry(wx.ACCEL_ALT, ord('o'), self.ID_OPEN_SUB),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F11, self.ID_FS_KEEP_AR),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_RETURN, self.ID_FS_STRETCH),
        ]
        self.SetAcceleratorTable(wx.AcceleratorTable(accel_entries))

    def init_timer(self):
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer_tick, self.timer)
        self.timer.Start(200)

    def speak(self, text, is_subtitle=False):
        acc_cfg = self.config.get("accessibility", {})
        if is_subtitle and acc_cfg.get("tts_engine") == "sapi5":
            def _sapi_speak():
                try:
                    eng = pyttsx3.init()
                    vid = acc_cfg.get("tts_voice_id", "")
                    if vid:
                        eng.setProperty('voice', vid)
                    eng.setProperty('rate', acc_cfg.get("tts_rate", 200))
                    eng.setProperty('volume', acc_cfg.get("tts_volume", 100) / 100.0)
                    eng.say(text)
                    eng.runAndWait()
                    eng.stop()
                except Exception:
                    pass
            threading.Thread(target=_sapi_speak, daemon=True).start()
        else:
            if self.speech:
                try:
                    self.speech.output(text)
                except Exception:
                    pass

    def on_open_video_dialog(self, event):
        wildcard = "Video Files (*.mp4;*.mkv;*.avi;*.mov;*.webm;*.ts)|*.mp4;*.mkv;*.avi;*.mov;*.webm;*.ts|All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Open Video File(s)", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            self.playlist = list(paths)
            self.play_playlist_index(0)
        dlg.Destroy()

    def on_open_folder_dialog(self, event):
        dlg = wx.DirDialog(self, "Select Folder Containing Videos", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            folder_path = dlg.GetPath()
            found_videos = []
            try:
                for entry in sorted(os.listdir(folder_path)):
                    full_path = os.path.join(folder_path, entry)
                    if os.path.isfile(full_path) and entry.lower().endswith(VIDEO_EXTENSIONS):
                        found_videos.append(full_path)
            except Exception as e:
                self.speak(f"Error reading folder: {e}")
                dlg.Destroy()
                return

            if found_videos:
                self.playlist = found_videos
                self.speak(f"Found {len(found_videos)} videos in folder")
                self.play_playlist_index(0)
            else:
                self.speak("No supported video files found in the selected folder")
        dlg.Destroy()

    def on_open_url_dialog(self, event):
        dlg = wx.TextEntryDialog(self, "Enter video stream URL:", "Open URL - ASPlayer")
        if dlg.ShowModal() == wx.ID_OK:
            url = dlg.GetValue().strip()
            if url:
                self.playlist = [url]
                self.play_playlist_index(0)
        dlg.Destroy()

    def on_open_playlist_dialog(self, event):
        current_lang = self.config.get("language", "en")
        dlg = PlaylistDialog(self, self.playlist, self.playlist_index, current_lang=current_lang)
        dlg.ShowModal()
        dlg.Destroy()

    def format_duration(self, ms):
        if ms <= 0:
            return "Unknown / Live Stream"
        total_sec = ms // 1000
        hours, remainder = divmod(total_sec, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    def play_playlist_index(self, index):
        if 0 <= index < len(self.playlist):
            self.playlist_index = index
            path = self.playlist[index]
            self.load_video(path)

    def load_video(self, path):
        self.record_current_position()
        
        self.current_video_path = path
        self.was_playing = False
        
        self.load_video_subtitle_settings(path)
        self.menu_sub_toggle_item.Check(self.sub_enabled)
        
        self.player.set_hwnd(self.video_panel.GetHandle())
        
        media = self.vlc_instance.media_new(path)
        self.player.set_media(media)
        self.player.play()
        
        wx.CallAfter(self.SetFocus)
        
        is_url = path.startswith(("http://", "https://"))
        display_name = path if is_url else os.path.basename(path)
        self.SetTitle(f"{display_name} - ASPlayer")
        
        playlist_info = ""
        if len(self.playlist) > 1:
            playlist_info = f"Item {self.playlist_index + 1} of {len(self.playlist)}: "
            
        saved_pos = 0 if is_url else self.config.get("positions", {}).get(path, 0)
        if self.config.get("resume_playback", True) and saved_pos > 0:
            self.pending_seek_time = saved_pos
            sec = saved_pos // 1000
            mins, secs = divmod(sec, 60)
            self.speak(f"{playlist_info}Resuming {display_name} from {mins} minutes {secs} seconds")
        else:
            self.pending_seek_time = 0
            self.speak(f"{playlist_info}Playing {display_name}")
            
        if not is_url:
            self.check_and_load_matching_srt(path)
        else:
            self.srt_subtitles = None
            self.current_sub_index = -1

    def check_and_load_matching_srt(self, video_path):
        folder_dir, file_name = os.path.split(video_path)
        base_name, _ = os.path.splitext(file_name)
        srt_path = os.path.join(folder_dir, base_name + ".srt")
        
        if os.path.exists(srt_path):
            self.load_subtitle_file(srt_path)
        else:
            self.srt_subtitles = None
            self.current_sub_index = -1
            try:
                self.player.video_set_subtitle_file("")
            except Exception:
                pass

    def load_subtitle_file(self, srt_path):
        loaded = False
        for enc in ['utf-8', 'cp1252', 'latin-1', 'utf-16']:
            try:
                self.srt_subtitles = pysrt.open(srt_path, encoding=enc)
                self.current_sub_index = -1
                loaded = True
                break
            except Exception:
                continue
        if loaded:
            self.speak("Subtitle loaded successfully")
            try:
                self.player.video_set_subtitle_file(srt_path)
            except Exception:
                pass
        else:
            self.srt_subtitles = None
            self.speak("Failed to load subtitle file due to encoding error")

    def on_open_sub_dialog(self, event):
        wildcard = "Subtitle Files (*.srt)|*.srt|All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Open Subtitle File", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.load_subtitle_file(path)
        dlg.Destroy()

    def on_toggle_subtitle_visibility(self, event):
        self.sub_enabled = self.menu_sub_toggle_item.IsChecked()
        self.save_current_subtitle_settings()
        try:
            track_idx = 1 if self.sub_enabled else 0
            self.player.video_set_subtitle_track(track_idx)
        except Exception:
            pass
            
        if self.sub_enabled:
            self.speak("Subtitles shown")
        else:
            self.speak("Subtitles hidden")

    def on_open_subtitle_appearance(self, event):
        current_lang = self.config.get("language", "en")
        dlg = SubtitleAppearanceDialog(self, self.sub_style, current_lang=current_lang)
        if dlg.ShowModal() == wx.ID_OK:
            self.sub_style = dlg.get_style()
            self.save_current_subtitle_settings()
            self.speak("Subtitle appearance settings saved")
        dlg.Destroy()

    def adjust_subtitle_sync(self, delta_ms):
        apply_current_only = self.menu_apply_current_item.IsChecked()
        
        if apply_current_only and self.current_sub_index != -1:
            current_line_offset = self.per_line_offsets.get(self.current_sub_index, 0)
            new_line_offset = current_line_offset + delta_ms
            self.per_line_offsets[self.current_sub_index] = new_line_offset
            self.save_current_subtitle_settings()
            sec_offset = new_line_offset / 1000.0
            self.speak(f"Line {self.current_sub_index} offset adjusted by {delta_ms} milliseconds. Current line offset: {sec_offset} seconds")
        else:
            self.sub_offset_ms += delta_ms
            self.save_current_subtitle_settings()
            sec_offset = self.sub_offset_ms / 1000.0
            self.speak(f"Subtitle global offset adjusted by {delta_ms} milliseconds. Current offset: {sec_offset} seconds")

    def on_reset_subtitle_sync(self, event):
        self.sub_offset_ms = 0
        self.per_line_offsets.clear()
        self.save_current_subtitle_settings()
        self.speak("Subtitle sync reset to default for this video")

    def set_subtitle_position(self, pos):
        self.sub_position = pos
        self.save_current_subtitle_settings()
        pos_name = "Top" if pos == 1 else "Bottom"
        self.speak(f"Subtitle position set to {pos_name}")

    def on_announce_status(self, event):
        current_lang = self.config.get("language", "en")
        if not self.current_video_path:
            msg = self.tr("no_media")
            self.speak(msg)
            dlg = MediaInfoDialog(self, msg, current_lang=current_lang)
            dlg.ShowModal()
            dlg.Destroy()
            return

        current_ms = self.player.get_time()
        total_ms = self.player.get_length()
        cur_str = self.format_duration(current_ms)
        tot_str = self.format_duration(total_ms)
        state_str = self.tr("playing") if self.player.is_playing() else self.tr("paused")
        vol = self.player.audio_get_volume()
        file_name = os.path.basename(self.current_video_path)
        width, height = self.player.video_get_size(0)
        res_str = f"{width}x{height}" if width > 0 and height > 0 else "Audio Only / Unknown"
        
        bitrate_kbps = 0
        try:
            stats = self.player.get_media().get_stats()
            if stats and hasattr(stats, 'input_bitrate'):
                bitrate_kbps = int(stats.input_bitrate * 8 * 1024)
        except Exception:
            pass
            
        if bitrate_kbps <= 0:
            try:
                if not self.current_video_path.startswith(("http://", "https://")) and os.path.exists(self.current_video_path) and total_ms > 0:
                    file_size_bits = os.path.getsize(self.current_video_path) * 8
                    duration_sec = total_ms / 1000.0
                    bitrate_kbps = int((file_size_bits / duration_sec) / 1000)
            except Exception:
                pass

        bitrate_str = f"{bitrate_kbps} kbps" if bitrate_kbps > 0 else "Variable / Unknown"
        sub_status = f"Loaded ({len(self.srt_subtitles)} lines)" if self.srt_subtitles else "None"

        summary_speech = f"{state_str}, {file_name}, Position {cur_str} of {tot_str}, Volume {vol} percent"
        self.speak(summary_speech)

        detail_text = (
            f"File Name  : {file_name}\n"
            f"Full Path  : {self.current_video_path}\n"
            f"Status     : {state_str}\n"
            f"Position   : {cur_str} / {tot_str}\n"
            f"Video Size : {res_str}\n"
            f"Bitrate    : {bitrate_str}\n"
            f"Volume     : {vol}%\n"
            f"Subtitle   : {sub_status}\n"
            f"Playlist   : Item {self.playlist_index + 1} of {len(self.playlist)}"
        )
        dlg = MediaInfoDialog(self, detail_text, current_lang=current_lang)
        dlg.ShowModal()
        dlg.Destroy()

    def on_open_accessibility_dialog(self, event):
        acc_cfg = self.config.get("accessibility", {})
        current_lang = self.config.get("language", "en")
        dlg = AccessibilityDialog(self, acc_cfg, current_lang=current_lang)
        if dlg.ShowModal() == wx.ID_OK:
            new_settings = dlg.get_settings()
            self.config["accessibility"].update(new_settings)
            self.save_config()
            self.speak("Accessibility and speech settings saved")
        dlg.Destroy()

    def on_toggle_resume_mode(self, event):
        is_checked = self.menu_resume_item.IsChecked()
        self.config["resume_playback"] = is_checked
        self.save_config()
        if is_checked:
            self.speak("Resume from last position enabled")
        else:
            self.speak("Always play from beginning enabled")

    def on_preferences(self, event):
        dlg = PreferencesDialog(
            self, 
            self.config.get("resume_playback", True), 
            self.config.get("language", "en"),
            self.config.get("theme", "dark")
        )
        if dlg.ShowModal() == wx.ID_OK:
            new_resume = dlg.get_resume_setting()
            new_lang = dlg.get_language_setting()
            new_theme = dlg.get_theme_setting()
            
            self.config["resume_playback"] = new_resume
            self.config["language"] = new_lang
            self.config["theme"] = new_theme
            self.menu_resume_item.Check(new_resume)
            self.save_config()
            self.apply_theme()
            self.speak(self.tr("prefs_saved"))
        dlg.Destroy()

    def on_about(self, event):
        current_lang = self.config.get("language", "en")
        dlg = AboutDialog(self, current_lang=current_lang)
        dlg.ShowModal()
        dlg.Destroy()

    def on_exit(self, event):
        self.Close()

    def on_window_close(self, event):
        self.record_current_position()
        self.timer.Stop()
        self.player.stop()
        event.Skip()

    def on_fullscreen_keep_ar(self, event):
        is_fs = self.IsFullScreen()
        self.ShowFullScreen(not is_fs)
        self.player.video_set_scale(0)
        self.speak("Fullscreen keep aspect ratio enabled" if not is_fs else "Windowed mode restored")

    def on_fullscreen_stretch(self, event):
        is_fs = self.IsFullScreen()
        self.ShowFullScreen(not is_fs)
        self.player.video_set_scale(1)
        self.speak("Fullscreen stretched enabled" if not is_fs else "Windowed mode restored")

    def on_show_context_menu(self, event):
        menu = wx.Menu()
        open_sub = wx.Menu()
        item_open_vid = open_sub.Append(wx.ID_ANY, self.tr("open_file"))
        item_open_folder = open_sub.Append(wx.ID_ANY, self.tr("open_folder"))
        item_open_url = open_sub.Append(wx.ID_ANY, self.tr("open_url"))
        menu.AppendSubMenu(open_sub, self.tr("menu_open"))
        
        item_open_sub = menu.Append(wx.ID_ANY, self.tr("open_sub"))
        item_playlist = menu.Append(wx.ID_ANY, self.tr("playlist_mgr"))
        item_media_info = menu.Append(wx.ID_ANY, self.tr("media_info"))
        menu.AppendSeparator()
        item_play = menu.Append(wx.ID_ANY, self.tr("play_pause"))
        item_next = menu.Append(wx.ID_ANY, self.tr("next_item"))
        item_prev = menu.Append(wx.ID_ANY, self.tr("prev_item"))
        menu.AppendSeparator()
        item_fs = menu.Append(wx.ID_ANY, self.tr("fs_keep_ar"))
        
        self.Bind(wx.EVT_MENU, self.on_open_video_dialog, item_open_vid)
        self.Bind(wx.EVT_MENU, self.on_open_folder_dialog, item_open_folder)
        self.Bind(wx.EVT_MENU, self.on_open_url_dialog, item_open_url)
        self.Bind(wx.EVT_MENU, self.on_open_sub_dialog, item_open_sub)
        self.Bind(wx.EVT_MENU, self.on_open_playlist_dialog, item_playlist)
        self.Bind(wx.EVT_MENU, self.on_announce_status, item_media_info)
        self.Bind(wx.EVT_MENU, self.on_toggle_play, item_play)
        self.Bind(wx.EVT_MENU, self.on_next_item, item_next)
        self.Bind(wx.EVT_MENU, self.on_prev_item, item_prev)
        self.Bind(wx.EVT_MENU, self.on_fullscreen_keep_ar, item_fs)
        
        self.PopupMenu(menu)
        menu.Destroy()

    def on_timer_tick(self, event):
        state = self.player.get_state()
        
        if state == vlc.State.Playing:
            self.was_playing = True
            if self.pending_seek_time > 0:
                self.player.set_time(self.pending_seek_time)
                self.pending_seek_time = 0
        elif state == vlc.State.Ended and self.was_playing:
            self.was_playing = False
            if self.playlist_index + 1 < len(self.playlist):
                self.play_playlist_index(self.playlist_index + 1)
            else:
                self.speak("End of playlist")
            return

        if not self.player.is_playing() or not self.srt_subtitles or not self.sub_enabled:
            return
            
        current_time_ms = self.player.get_time() + self.sub_offset_ms
        found_sub = None
        for sub in self.srt_subtitles:
            line_specific_offset = self.per_line_offsets.get(sub.index, 0)
            start_ms = sub.start.ordinal + line_specific_offset
            end_ms = sub.end.ordinal + line_specific_offset
            if start_ms <= current_time_ms <= end_ms:
                found_sub = sub
                break
                
        if found_sub and found_sub.index != self.current_sub_index:
            self.current_sub_index = found_sub.index
            clean_text = found_sub.text_without_tags.replace('\n', ' ')
            self.speak(clean_text, is_subtitle=True)
        elif not found_sub:
            self.current_sub_index = -1

    def on_toggle_play(self, event):
        if self.player.is_playing():
            self.player.pause()
            self.speak(self.tr("paused"))
        else:
            self.player.play()
            self.speak(self.tr("playing"))

    def on_stop(self, event):
        self.record_current_position()
        self.was_playing = False
        self.player.stop()
        self.speak(self.tr("stopped"))

    def on_forward(self, event):
        new_time = self.player.get_time() + 5000
        self.player.set_time(new_time)
        self.speak("Forward 5 seconds")

    def on_rewind(self, event):
        new_time = max(0, self.player.get_time() - 5000)
        self.player.set_time(new_time)
        self.speak("Rewind 5 seconds")

    def jump_time(self, offset_ms, action_label):
        current_time = self.player.get_time()
        max_time = self.player.get_length()
        new_time = max(0, current_time + offset_ms)
        if max_time > 0 and new_time > max_time:
            new_time = max_time
        self.player.set_time(new_time)
        
        sec = new_time // 1000
        mins, secs = divmod(sec, 60)
        self.speak(f"{action_label}. Position {mins} minutes {secs} seconds")

    def on_next_item(self, event):
        if self.playlist_index + 1 < len(self.playlist):
            self.play_playlist_index(self.playlist_index + 1)
        else:
            self.speak("No next item in playlist")

    def on_prev_item(self, event):
        if self.playlist_index - 1 >= 0:
            self.play_playlist_index(self.playlist_index - 1)
        else:
            self.speak("No previous item in playlist")

    def on_volume_up(self, event):
        vol = min(100, self.player.audio_get_volume() + 5)
        self.player.audio_set_volume(vol)
        self.speak(f"Volume {vol} percent")

    def on_volume_down(self, event):
        vol = max(0, self.player.audio_get_volume() - 5)
        self.player.audio_set_volume(vol)
        self.speak(f"Volume {vol} percent")

    def on_toggle_mute(self, event):
        self.player.audio_toggle_mute()
        is_muted = self.player.audio_get_mute()
        if is_muted:
            self.speak("Muted")
        else:
            vol = self.player.audio_get_volume()
            self.speak(f"Unmuted. Volume {vol} percent")


if __name__ == '__main__':
    app = wx.App()
    frame = AsplayerWindow()
    frame.Show()
    app.MainLoop()