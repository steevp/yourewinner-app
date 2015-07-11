import os
import json

theme = "weed"

with open("style.json", "w") as f:
    json.dump({
        "button_background": os.path.join("themes", theme, "catbg.png"),
        "text_color": [1,1,1,1],
        "background_color": [30/255.0, 63/255.0, 30/255.0, 1],
        "selected_color": [0.624, 0.365, 0.094, 1],
    }, f)

