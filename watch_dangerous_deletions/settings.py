import os

origin_paths = ["Z:\\", "A:\\", "B:\\", "R:\\", "U:\\", "Y:\\"]
recycle_suffix = "@Recycle"
scan_interval = 60  # in seconds

warn_delete_size = 100  # Gigabytes

# Warn if these ever appear in the bin
warn_dir_whitelist = ["Finished Film"]
warn_file_ext_whitelist = [".fcpxml"]

# Ignore if these ever appear in the bin
warn_dir_blacklist = []
warn_file_ext_blacklist = []

warning_sound = os.path.join(os.path.dirname(__file__), "assets", "goat.wav")
