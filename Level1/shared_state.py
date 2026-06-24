# shared_state.py
# Simple shared container for passing hotbar data between levels.

# Set by the calling level BEFORE entering a room – carries items IN.
incoming_hotbar_slots = None   # list[InventoryItem | None]

# Set by the room level BEFORE returning – carries items OUT.
returned_hotbar_slots = None   # list[InventoryItem | None]

# Optional spawn position for the player when returning to a garden level.
restart_level = None            # file path set before lose screen, read by ending.py on restart
