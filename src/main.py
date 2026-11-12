import os
import json
import wx
import vlc
import pysrt
import accessible_output2.outputs.auto


VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov', '.webm', '.ts', '.flv', '.wmv', '.m4v')


class PreferencesDialog(wx.Dialog):
    def __init__(self, parent, resume_enabled, current_lang):
        super().__init__(parent, title="Preferences - ASPlayer", size=(420, 280))
        self.resume_enabled = resume_enabled
        self.current_lang = current_lang
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        lbl_resume = wx.StaticText(panel, label="Startup Playback Behavior:")
        sizer.Add(lbl_resume, 0, wx.ALL, 10)
        
        self.rb_beginning = wx.RadioButton(panel, label="Always play from beginning", style=wx.RB_GROUP)
        self.rb_resume = wx.RadioButton(panel, label="Resume from last watched position")
        
        if self.resume_enabled:
            self.rb_resume.SetValue(True)
        else:
            self.rb_beginning.SetValue(True)
            
        sizer.Add(self.rb_beginning, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        sizer.Add(self.rb_resume, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        lbl_lang = wx.StaticText(panel, label="Application Language:")
        sizer.Add(lbl_lang, 0, wx.ALL, 10)
        
        self.lang_choices = ["English", "Indonesian"]
        self.lang_choice_ctrl = wx.Choice(panel, choices=self.lang_choices)
        
        if self.current_lang == "id":
            self.lang_choice_ctrl.SetSelection(1)
        else:
            self.lang_choice_ctrl.SetSelection(0)
            
        sizer.Add(self.lang_choice_ctrl, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        btn_sizer = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(panel, wx.ID_OK, "Save")
        btn_cancel = wx.Button(panel, wx.ID_CANCEL, "Cancel")
        btn_sizer.AddButton(btn_ok)
        btn_sizer.AddButton(btn_cancel)
        btn_sizer.Realize()
        
        sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 10)
        panel.SetSizer(sizer)
        self.CenterOnParent()

    def get_resume_setting(self):
        return self.rb_resume.GetValue()

    def get_language_setting(self):
        sel = self.lang_choice_ctrl.GetSelection()
        return "id" if sel == 1 else "en"


class PlaylistDialog(wx.Dialog):
    def __init__(self, parent, playlist, current_index):
        super().__init__(parent, title="Playlist Manager - ASPlayer", size=(550, 400))
        self.parent_frame = parent
        self.playlist = list(playlist)
        self.current_index = current_index
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        lbl = wx.StaticText(panel, label="Playlist Items (Press Enter to play selected item):")
        sizer.Add(lbl, 0, wx.ALL, 10)
        
        self.listbox = wx.ListBox(panel, style=wx.LB_SINGLE)
        self.refresh_list()
        sizer.Add(self.listbox, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_add = wx.Button(panel, label="&Add Files...")
        btn_remove = wx.Button(panel, label="&Remove Selected")
        btn_clear = wx.Button(panel, label="&Clear All")
        btn_play = wx.Button(panel, label="&Play Selected")
        btn_close = wx.Button(panel, wx.ID_CANCEL, "Close")
        
        btn_sizer.Add(btn_add, 0, wx.RIGHT, 5)
        btn_sizer.Add(btn_remove, 0, wx.RIGHT, 5)
        btn_sizer.Add(btn_clear, 0, wx.RIGHT, 5)
        btn_sizer.Add(btn_play, 0, wx.RIGHT, 5)
        btn_sizer.Add(btn_close, 0)
        
        sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        panel.SetSizer(sizer)
        
        btn_add.Bind(wx.EVT_BUTTON, self.on_add_files)
        btn_remove.Bind(wx.EVT_BUTTON, self.on_remove_item)
        btn_clear.Bind(wx.EVT_BUTTON, self.on_clear_all)
        btn_play.Bind(wx.EVT_BUTTON, self.on_play_selected)
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
            
        self.vlc_instance = vlc.Instance("--no-video-title-show", "--network-caching=3000", "--no-lua")
        self.player = self.vlc_instance.media_player_new()
        
        self.current_video_path = None
        self.playlist = []
        self.playlist_index = -1
        self.srt_subtitles = None
        self.current_sub_index = -1
        self.last_active_sub_index = -1
        self.pending_seek_time = 0
        self.was_playing = False
        
        # Variabel Subtitle Spesifik per Video
        self.sub_offset_ms = 0          # Penyesuaian timing global (ms)
        self.sub_line_offsets = {}      # Penyesuaian timing per baris: {sub_index_str: offset_ms}
        self.sub_current_line_only = False  # Mode "Apply to current line only"
        self.sub_enabled = True         # Status show/hide subtitle
        self.sub_position = 0           # Posisi subtitle (0: Bottom, 1: Top)
        
        self.init_ui()
        self.init_timer()
        self.Bind(wx.EVT_CLOSE, self.on_window_close)
        self.Center()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"resume_playback": True, "language": "en", "positions": {}, "subtitles": {}}

    def save_config(self):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except Exception:
            pass

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
            self.config["subtitles"][self.current_video_path] = {
                "offset_ms": self.sub_offset_ms,
                "line_offsets": self.sub_line_offsets,
                "enabled": self.sub_enabled,
                "position": self.sub_position
            }
            self.save_config()

    def load_video_subtitle_settings(self, path):
        sub_cfg = self.config.get("subtitles", {}).get(path, {})
        self.sub_offset_ms = sub_cfg.get("offset_ms", 0)
        self.sub_line_offsets = sub_cfg.get("line_offsets", {})
        self.sub_enabled = sub_cfg.get("enabled", True)
        self.sub_position = sub_cfg.get("position", 0)

    def init_ui(self):
        panel = wx.Panel(self)
        
        self.video_panel = wx.Panel(panel)
        self.video_panel.SetBackgroundColour(wx.BLACK)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.video_panel, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        
        # --- MEMBUAT MENU BAR ---
        menubar = wx.MenuBar()
        
        # 1. Menu File (Alt + F)
        file_menu = wx.Menu()
        open_submenu = wx.Menu()
        
        self.ID_OPEN_VIDEO = wx.NewIdRef()
        self.ID_OPEN_FOLDER = wx.NewIdRef()
        self.ID_OPEN_URL = wx.NewIdRef()
        self.ID_OPEN_SUB = wx.NewIdRef()
        self.ID_PLAYLIST = wx.NewIdRef()
        self.ID_EXIT = wx.NewIdRef()
        
        open_submenu.Append(self.ID_OPEN_VIDEO, "Open File...\tCtrl+O", "Open video file(s)")
        open_submenu.Append(self.ID_OPEN_FOLDER, "Open Folder...\tCtrl+Shift+O", "Play all videos in a folder")
        open_submenu.Append(self.ID_OPEN_URL, "Open URL...\tCtrl+U", "Open a video stream from URL")
        
        file_menu.AppendSubMenu(open_submenu, "&Open", "Open media source")
        file_menu.Append(self.ID_OPEN_SUB, "Open Subtitle (.srt)...\tAlt+O", "Open an external SRT subtitle file")
        file_menu.AppendSeparator()
        file_menu.Append(self.ID_PLAYLIST, "Playlist Manager...\tCtrl+L", "Manage and play video playlist")
        file_menu.AppendSeparator()
        file_menu.Append(self.ID_EXIT, "Exit\tAlt+F4", "Close the application")
        
        # 2. Menu View (Alt + V)
        view_menu = wx.Menu()
        self.ID_FS_KEEP_AR = wx.NewIdRef()
        self.ID_FS_STRETCH = wx.NewIdRef()
        
        view_menu.Append(self.ID_FS_KEEP_AR, "Fullscreen (Keep AR)\tF11", "Switch to fullscreen keeping aspect ratio")
        view_menu.Append(self.ID_FS_STRETCH, "Fullscreen (Stretch)\tCtrl+Enter", "Switch to fullscreen stretched")
        
        # 3. Menu Playback (Alt + P)
        playback_menu = wx.Menu()
        self.ID_PB_PLAYPAUSE = wx.NewIdRef()
        self.ID_PB_STOP = wx.NewIdRef()
        self.ID_PB_REWIND = wx.NewIdRef()
        self.ID_PB_FORWARD = wx.NewIdRef()
        self.ID_PB_NEXT = wx.NewIdRef()
        self.ID_PB_PREV = wx.NewIdRef()
        self.ID_PB_TOGGLE_RESUME = wx.NewIdRef()
        
        playback_menu.Append(self.ID_PB_PLAYPAUSE, "Play / Pause\tSpace", "Toggle playback")
        playback_menu.Append(self.ID_PB_STOP, "Stop\tCtrl+S", "Stop playback")
        playback_menu.Append(self.ID_PB_REWIND, "Rewind 5 Seconds\tLeft", "Rewind 5 seconds")
        playback_menu.Append(self.ID_PB_FORWARD, "Fast Forward 5 Seconds\tRight", "Fast forward 5 seconds")
        playback_menu.AppendSeparator()
        
        # --- SUBMENU JUMP TO ---
        jump_submenu = wx.Menu()
        self.ID_JUMP_REW_30S = wx.NewIdRef()
        self.ID_JUMP_FWD_30S = wx.NewIdRef()
        self.ID_JUMP_REW_1M = wx.NewIdRef()
        self.ID_JUMP_FWD_1M = wx.NewIdRef()
        self.ID_JUMP_REW_5M = wx.NewIdRef()
        self.ID_JUMP_FWD_5M = wx.NewIdRef()
        
        jump_submenu.Append(self.ID_JUMP_REW_30S, "Jump Backward 30 Seconds\tCtrl+Left", "Jump backward 30 seconds")
        jump_submenu.Append(self.ID_JUMP_FWD_30S, "Jump Forward 30 Seconds\tCtrl+Right", "Jump forward 30 seconds")
        jump_submenu.Append(self.ID_JUMP_REW_1M, "Jump Backward 1 Minute\tShift+Left", "Jump backward 1 minute")
        jump_submenu.Append(self.ID_JUMP_FWD_1M, "Jump Forward 1 Minute\tShift+Right", "Jump forward 1 minute")
        jump_submenu.Append(self.ID_JUMP_REW_5M, "Jump Backward 5 Minutes\tCtrl+PgUp", "Jump backward 5 minutes")
        jump_submenu.Append(self.ID_JUMP_FWD_5M, "Jump Forward 5 Minutes\tCtrl+PgDn", "Jump forward 5 minutes")
        
        playback_menu.AppendSubMenu(jump_submenu, "&Jump To", "Flexible video position navigation")
        
        # --- SUBMENU VOLUME ---
        volume_submenu = wx.Menu()
        self.ID_VOL_UP = wx.NewIdRef()
        self.ID_VOL_DOWN = wx.NewIdRef()
        self.ID_VOL_MUTE = wx.NewIdRef()
        
        volume_submenu.Append(self.ID_VOL_UP, "Volume Up\tUp", "Increase audio volume")
        volume_submenu.Append(self.ID_VOL_DOWN, "Volume Down\tDown", "Decrease audio volume")
        volume_submenu.Append(self.ID_VOL_MUTE, "Mute / Unmute\tM", "Mute or unmute audio")
        
        playback_menu.AppendSubMenu(volume_submenu, "&Volume", "Audio volume controls")
        
        playback_menu.AppendSeparator()
        playback_menu.Append(self.ID_PB_NEXT, "Play Next Item\tPage Down", "Play next item in playlist")
        playback_menu.Append(self.ID_PB_PREV, "Play Previous Item\tPage Up", "Play previous item in playlist")
        playback_menu.AppendSeparator()
        
        self.menu_resume_item = playback_menu.AppendCheckItem(
            self.ID_PB_TOGGLE_RESUME,
            "Resume from Last Position",
            "Automatically resume video from last watched position"
        )
        self.menu_resume_item.Check(self.config.get("resume_playback", True))
        
        # 4. Menu Tools (Alt + T) - Subtitle Settings Menu LENGKAP
        tools_menu = wx.Menu()
        
        sub_settings_menu = wx.Menu()
        self.ID_SUB_TOGGLE = wx.NewIdRef()
        self.ID_SUB_POS_BOTTOM = wx.NewIdRef()
        self.ID_SUB_POS_TOP = wx.NewIdRef()
        
        # Submenu Subtitle Sync Timing
        sub_sync_menu = wx.Menu()
        self.ID_SUB_CURRENT_LINE_ONLY = wx.NewIdRef()
        self.ID_SUB_INC_05 = wx.NewIdRef()
        self.ID_SUB_DEC_05 = wx.NewIdRef()
        self.ID_SUB_INC_5 = wx.NewIdRef()
        self.ID_SUB_DEC_5 = wx.NewIdRef()
        self.ID_SUB_INC_50 = wx.NewIdRef()
        self.ID_SUB_DEC_50 = wx.NewIdRef()
        self.ID_SUB_RESET_SYNC = wx.NewIdRef()
        
        self.menu_sub_current_line_item = sub_sync_menu.AppendCheckItem(
            self.ID_SUB_CURRENT_LINE_ONLY,
            "Apply to current line only",
            "Adjust timing only for the active subtitle line without shifting other lines"
        )
        self.menu_sub_current_line_item.Check(False)
        sub_sync_menu.AppendSeparator()
        
        sub_sync_menu.Append(self.ID_SUB_INC_05, "Increase subtitle 0.5 second\t>")
        sub_sync_menu.Append(self.ID_SUB_DEC_05, "Decrease subtitle 0.5 second\t<")
        sub_sync_menu.Append(self.ID_SUB_INC_5, "Increase subtitle 5 second\tCtrl+>")
        sub_sync_menu.Append(self.ID_SUB_DEC_5, "Decrease subtitle 5 second\tCtrl+<")
        sub_sync_menu.Append(self.ID_SUB_INC_50, "Increase subtitle 50 second\tShift+>")
        sub_sync_menu.Append(self.ID_SUB_DEC_50, "Decrease subtitle 50 second\tShift+<")
        sub_sync_menu.AppendSeparator()
        sub_sync_menu.Append(self.ID_SUB_RESET_SYNC, "Reset Subtitle Sync to Default")
        
        self.menu_sub_toggle_item = sub_settings_menu.AppendCheckItem(self.ID_SUB_TOGGLE, "Show / Hide Subtitle", "Toggle subtitle visibility")
        self.menu_sub_toggle_item.Check(True)
        
        sub_settings_menu.AppendSubMenu(sub_sync_menu, "Subtitle Sync Menu", "Adjust subtitle timing offset for current video")
        sub_settings_menu.AppendSeparator()
        sub_settings_menu.Append(self.ID_SUB_POS_BOTTOM, "Position: Bottom", "Place subtitles at bottom")
        sub_settings_menu.Append(self.ID_SUB_POS_TOP, "Position: Top", "Place subtitles at top")
        
        tools_menu.AppendSubMenu(sub_settings_menu, "Subtitle Menu", "Advanced subtitle configuration for current video")
        tools_menu.AppendSeparator()
        
        self.ID_PREFERENCES = wx.NewIdRef()
        tools_menu.Append(self.ID_PREFERENCES, "Preferences...\tCtrl+Shift+P", "Configure application settings and language")
        
        menubar.Append(file_menu, "&File")
        menubar.Append(view_menu, "&View")
        menubar.Append(playback_menu, "&Playback")
        menubar.Append(tools_menu, "&Tools")
        self.SetMenuBar(menubar)
        
        # Bind Event Menu
        self.Bind(wx.EVT_MENU, self.on_open_video_dialog, id=self.ID_OPEN_VIDEO)
        self.Bind(wx.EVT_MENU, self.on_open_folder_dialog, id=self.ID_OPEN_FOLDER)
        self.Bind(wx.EVT_MENU, self.on_open_url_dialog, id=self.ID_OPEN_URL)
        self.Bind(wx.EVT_MENU, self.on_open_sub_dialog, id=self.ID_OPEN_SUB)
        self.Bind(wx.EVT_MENU, self.on_open_playlist_dialog, id=self.ID_PLAYLIST)
        self.Bind(wx.EVT_MENU, self.on_exit, id=self.ID_EXIT)
        
        self.Bind(wx.EVT_MENU, self.on_fullscreen_keep_ar, id=self.ID_FS_KEEP_AR)
        self.Bind(wx.EVT_MENU, self.on_fullscreen_stretch, id=self.ID_FS_STRETCH)
        
        self.Bind(wx.EVT_MENU, self.on_toggle_play, id=self.ID_PB_PLAYPAUSE)
        self.Bind(wx.EVT_MENU, self.on_stop, id=self.ID_PB_STOP)
        self.Bind(wx.EVT_MENU, self.on_rewind, id=self.ID_PB_REWIND)
        self.Bind(wx.EVT_MENU, self.on_forward, id=self.ID_PB_FORWARD)
        
        # Bind Jump To Event
        self.Bind(wx.EVT_MENU, lambda e: self.jump_time(-30000, "Jumped backward 30 seconds"), id=self.ID_JUMP_REW_30S)
        self.Bind(wx.EVT_MENU, lambda e: self.jump_time(30000, "Jumped forward 30 seconds"), id=self.ID_JUMP_FWD_30S)
        self.Bind(wx.EVT_MENU, lambda e: self.jump_time(-60000, "Jumped backward 1 minute"), id=self.ID_JUMP_REW_1M)
        self.Bind(wx.EVT_MENU, lambda e: self.jump_time(60000, "Jumped forward 1 minute"), id=self.ID_JUMP_FWD_1M)
        self.Bind(wx.EVT_MENU, lambda e: self.jump_time(-300000, "Jumped backward 5 minutes"), id=self.ID_JUMP_REW_5M)
        self.Bind(wx.EVT_MENU, lambda e: self.jump_time(300000, "Jumped forward 5 minutes"), id=self.ID_JUMP_FWD_5M)
        
        # Bind Volume Event
        self.Bind(wx.EVT_MENU, self.on_volume_up, id=self.ID_VOL_UP)
        self.Bind(wx.EVT_MENU, self.on_volume_down, id=self.ID_VOL_DOWN)
        self.Bind(wx.EVT_MENU, self.on_toggle_mute, id=self.ID_VOL_MUTE)
        
        # Bind Subtitle Advanced Menu Event
        self.Bind(wx.EVT_MENU, self.on_toggle_subtitle_visibility, id=self.ID_SUB_TOGGLE)
        self.Bind(wx.EVT_MENU, self.on_toggle_sub_current_line_only, id=self.ID_SUB_CURRENT_LINE_ONLY)
        self.Bind(wx.EVT_MENU, lambda e: self.adjust_subtitle_sync(500), id=self.ID_SUB_INC_05)
        self.Bind(wx.EVT_MENU, lambda e: self.adjust_subtitle_sync(-500), id=self.ID_SUB_DEC_05)
        self.Bind(wx.EVT_MENU, lambda e: self.adjust_subtitle_sync(5000), id=self.ID_SUB_INC_5)
        self.Bind(wx.EVT_MENU, lambda e: self.adjust_subtitle_sync(-5000), id=self.ID_SUB_DEC_5)
        self.Bind(wx.EVT_MENU, lambda e: self.adjust_subtitle_sync(50000), id=self.ID_SUB_INC_50)
        self.Bind(wx.EVT_MENU, lambda e: self.adjust_subtitle_sync(-50000), id=self.ID_SUB_DEC_50)
        self.Bind(wx.EVT_MENU, self.on_reset_subtitle_sync, id=self.ID_SUB_RESET_SYNC)
        self.Bind(wx.EVT_MENU, lambda e: self.set_subtitle_position(0), id=self.ID_SUB_POS_BOTTOM)
        self.Bind(wx.EVT_MENU, lambda e: self.set_subtitle_position(1), id=self.ID_SUB_POS_TOP)
        
        self.Bind(wx.EVT_MENU, self.on_next_item, id=self.ID_PB_NEXT)
        self.Bind(wx.EVT_MENU, self.on_prev_item, id=self.ID_PB_PREV)
        self.Bind(wx.EVT_MENU, self.on_toggle_resume_mode, id=self.ID_PB_TOGGLE_RESUME)
        self.Bind(wx.EVT_MENU, self.on_preferences, id=self.ID_PREFERENCES)
        
        # --- CONTEXT MENU ---
        self.Bind(wx.EVT_CONTEXT_MENU, self.on_show_context_menu)
        self.video_panel.Bind(wx.EVT_CONTEXT_MENU, self.on_show_context_menu)

        # --- KEYBOARD ACCELERATOR TABLE ---
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

    def speak(self, text):
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
        dlg = PlaylistDialog(self, self.playlist, self.playlist_index)
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
        self.last_active_sub_index = -1
        
        # Muat pengaturan subtitle khusus video ini
        self.load_video_subtitle_settings(path)
        self.menu_sub_toggle_item.Check(self.sub_enabled)
        
        self.player.set_hwnd(self.video_panel.GetHandle())
        
        media = self.vlc_instance.media_new(path)
        self.player.set_media(media)
        self.player.play()
        
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
            loaded = False
            for enc in ['utf-8', 'cp1252', 'latin-1', 'utf-16']:
                try:
                    self.srt_subtitles = pysrt.open(srt_path, encoding=enc)
                    self.current_sub_index = -1
                    self.speak("Subtitle loaded")
                    loaded = True
                    break
                except Exception:
                    continue
            if not loaded:
                self.srt_subtitles = None
        else:
            self.srt_subtitles = None
            self.current_sub_index = -1

    def on_open_sub_dialog(self, event):
        wildcard = "Subtitle Files (*.srt)|*.srt|All files (*.*)|*.*"
        dlg = wx.FileDialog(self, "Open Subtitle File", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            loaded = False
            for enc in ['utf-8', 'cp1252', 'latin-1', 'utf-16']:
                try:
                    self.srt_subtitles = pysrt.open(path, encoding=enc)
                    self.current_sub_index = -1
                    self.speak("Subtitle file loaded successfully")
                    loaded = True
                    break
                except Exception:
                    continue
            if not loaded:
                self.speak("Failed to load subtitle file due to encoding error")
        dlg.Destroy()

    # --- FITUR KUSTOMISASI SUBTITLE SPESIFIK PER VIDEO & PER BARIS ---
    def on_toggle_subtitle_visibility(self, event):
        self.sub_enabled = self.menu_sub_toggle_item.IsChecked()
        self.save_current_subtitle_settings()
        if self.sub_enabled:
            self.speak("Subtitles shown")
        else:
            self.speak("Subtitles hidden")

    def on_toggle_sub_current_line_only(self, event):
        self.sub_current_line_only = self.menu_sub_current_line_item.IsChecked()
        if self.sub_current_line_only:
            self.speak("Apply to current line only enabled")
        else:
            self.speak("Apply to current line only disabled. Adjustments apply globally")

    def get_target_subtitle_index(self):
        if not self.srt_subtitles:
            return None
        if self.current_sub_index != -1:
            return self.current_sub_index
        if self.last_active_sub_index != -1:
            return self.last_active_sub_index

        current_time_ms = self.player.get_time()
        closest_sub = None
        min_diff = float('inf')
        for sub in self.srt_subtitles:
            line_off = self.sub_line_offsets.get(str(sub.index), 0)
            eff_start = sub.start.ordinal + self.sub_offset_ms + line_off
            eff_end = sub.end.ordinal + self.sub_offset_ms + line_off
            if eff_start <= current_time_ms <= eff_end:
                return sub.index
            diff = min(abs(current_time_ms - eff_start), abs(current_time_ms - eff_end))
            if diff < min_diff:
                min_diff = diff
                closest_sub = sub.index
        return closest_sub

    def adjust_subtitle_sync(self, delta_ms):
        if self.sub_current_line_only:
            target_idx = self.get_target_subtitle_index()
            if target_idx is None:
                self.speak("No subtitle line found to adjust")
                return
            key = str(target_idx)
            current_line_off = self.sub_line_offsets.get(key, 0) + delta_ms
            self.sub_line_offsets[key] = current_line_off
            self.save_current_subtitle_settings()
            total_line_sec = (self.sub_offset_ms + current_line_off) / 1000.0
            self.speak(f"Line {target_idx} offset adjusted by {delta_ms} milliseconds. Line offset: {total_line_sec} seconds")
        else:
            self.sub_offset_ms += delta_ms
            self.save_current_subtitle_settings()
            sec_offset = self.sub_offset_ms / 1000.0
            self.speak(f"Global subtitle offset adjusted by {delta_ms} milliseconds. Current offset: {sec_offset} seconds")

    def on_reset_subtitle_sync(self, event):
        self.sub_offset_ms = 0
        self.sub_line_offsets = {}
        self.save_current_subtitle_settings()
        self.speak("All subtitle sync settings reset to default for this video")

    def set_subtitle_position(self, pos):
        self.sub_position = pos
        self.save_current_subtitle_settings()
        pos_name = "Top" if pos == 1 else "Bottom"
        self.speak(f"Subtitle position set to {pos_name}")

    def on_toggle_resume_mode(self, event):
        is_checked = self.menu_resume_item.IsChecked()
        self.config["resume_playback"] = is_checked
        self.save_config()
        if is_checked:
            self.speak("Resume from last position enabled")
        else:
            self.speak("Always play from beginning enabled")

    def on_preferences(self, event):
        dlg = PreferencesDialog(self, self.config.get("resume_playback", True), self.config.get("language", "en"))
        if dlg.ShowModal() == wx.ID_OK:
            new_resume = dlg.get_resume_setting()
            new_lang = dlg.get_language_setting()
            
            self.config["resume_playback"] = new_resume
            self.config["language"] = new_lang
            self.menu_resume_item.Check(new_resume)
            self.save_config()
            self.speak("Preferences saved")
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
        item_open_vid = open_sub.Append(wx.ID_ANY, "Open File...")
        item_open_folder = open_sub.Append(wx.ID_ANY, "Open Folder...")
        item_open_url = open_sub.Append(wx.ID_ANY, "Open URL...")
        menu.AppendSubMenu(open_sub, "Open")
        
        item_open_sub = menu.Append(wx.ID_ANY, "Open Subtitle (.srt)...")
        item_playlist = menu.Append(wx.ID_ANY, "Playlist Manager...")
        menu.AppendSeparator()
        item_play = menu.Append(wx.ID_ANY, "Play / Pause")
        item_next = menu.Append(wx.ID_ANY, "Play Next Item")
        item_prev = menu.Append(wx.ID_ANY, "Play Previous Item")
        menu.AppendSeparator()
        item_fs = menu.Append(wx.ID_ANY, "Toggle Fullscreen (Keep AR)")
        
        self.Bind(wx.EVT_MENU, self.on_open_video_dialog, item_open_vid)
        self.Bind(wx.EVT_MENU, self.on_open_folder_dialog, item_open_folder)
        self.Bind(wx.EVT_MENU, self.on_open_url_dialog, item_open_url)
        self.Bind(wx.EVT_MENU, self.on_open_sub_dialog, item_open_sub)
        self.Bind(wx.EVT_MENU, self.on_open_playlist_dialog, item_playlist)
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
            
        video_time_ms = self.player.get_time()
        found_sub = None
        for sub in self.srt_subtitles:
            line_offset = self.sub_line_offsets.get(str(sub.index), 0)
            total_offset = self.sub_offset_ms + line_offset
            start_ms = sub.start.ordinal + total_offset
            end_ms = sub.end.ordinal + total_offset
            if start_ms <= video_time_ms <= end_ms:
                found_sub = sub
                break
                
        if found_sub and found_sub.index != self.current_sub_index:
            self.current_sub_index = found_sub.index
            self.last_active_sub_index = found_sub.index
            clean_text = found_sub.text_without_tags.replace('\n', ' ')
            self.speak(clean_text)
        elif not found_sub:
            self.current_sub_index = -1

    def on_toggle_play(self, event):
        if self.player.is_playing():
            self.player.pause()
            self.speak("Paused")
        else:
            self.player.play()
            self.speak("Playing")

    def on_stop(self, event):
        self.record_current_position()
        self.was_playing = False
        self.player.stop()
        self.speak("Stopped")

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