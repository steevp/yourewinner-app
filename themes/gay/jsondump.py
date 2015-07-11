import os
import json

theme = "default"

with open("style.json", "w") as f:
    json.dump({
        "button_background": os.path.join("themes", theme, "catbg.jpg"),
        "text_color": [1,1,1,1],
        "background_color": [32/255.0, 9/255.0, 39/255.0, 1],
        "selected_color": [0.624, 0.365, 0.094, 1],
    }, f)

