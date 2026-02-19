def generate_floor_layouts(area_sq_ft, floors=1, single_image=True, room_options=None):
    """Return a list of floor layouts for given area (sq ft) and floor count.

    Output format: [{"floor": "Ground Floor", "canvas": {"w":..,"h":..}, "rooms": [{name,area_sq_ft,dims,x,y,w,h}, ...]}, ...]

    This version assigns room areas by simple weights, chooses a realistic
    aspect ratio per room type, computes width/height in feet and converts
    to pixels using a floor-level pixels-per-foot scale, then packs rooms
    into rows (greedy) to create a clean blueprint-like layout.
    """
    import math

    # choose rooms based on total floor area (coarse grouping)
    area_per_floor = area_sq_ft / max(1, floors)
    if area_per_floor < 1000:
        rooms = ["Living Room", "Bedroom", "Kitchen", "Bathroom"]
    elif area_per_floor < 2500:
        rooms = ["Living Room", "Master Bedroom", "Bedroom 2", "Kitchen", "Dining Area", "Bathroom 1"]
    else:
        rooms = ["Living Room", "Master Bedroom", "Bedroom 2", "Bedroom 3", "Kitchen", "Dining Room", "Guest Room", "Bathroom 1"]

    layout = []

    # canvas sizing for front-end SVG rendering (px)
    canvas_w = 760
    canvas_h = 460
    margin = 12

    # room area weightings (higher -> larger share of floor area)
    weight_map = {
        "living": 1.6,
        "master": 1.4,
        "bedroom": 1.0,
        "kitchen": 1.0,
        "dining": 0.9,
        "bathroom": 0.4,
        "guest": 0.9,
        "study": 0.8,
    }

    # aspect ratio (width / height) typical per room keyword: (min, max)
    aspect_map = {
        "living": (1.4, 1.8),
        "master": (1.2, 1.6),
        "bedroom": (1.0, 1.4),
        "kitchen": (1.0, 1.6),
        "dining": (1.2, 1.6),
        "bathroom": (1.0, 1.2),
        "guest": (1.0, 1.4),
        "study": (1.0, 1.4),
    }

    # if single_image is requested, only generate the first floor (ground floor)
    effective_floors = 1 if single_image else max(1, floors)

    for i in range(effective_floors):
        floor_name = "Ground Floor" if i == 0 else f"Floor {i}"
        n = len(rooms)
        # compute weights
        weights = []
        for name in rooms:
            key = name.lower()
            matched = 1.0
            for k, w in weight_map.items():
                if k in key:
                    matched = w
                    break
            weights.append(matched)

        total_weight = sum(weights) or n
        # allocate area per room proportional to weight
        area_per_floor = area_sq_ft / max(1, floors)
        room_areas = [area_per_floor * (w / total_weight) for w in weights]

        # approximate overall floor footprint in feet (choose a comfortable aspect)
        floor_aspect = 1.4  # width / height
        floor_w_ft = math.sqrt(area_per_floor * floor_aspect)
        floor_h_ft = area_per_floor / floor_w_ft

        # compute pixels-per-foot so footprint fits into canvas with margins
        avail_w = canvas_w - margin * 2
        avail_h = canvas_h - margin * 2
        if floor_w_ft <= 0 or floor_h_ft <= 0:
            ppf = 1.0
        else:
            ppf = min(avail_w / floor_w_ft, avail_h / floor_h_ft)

        # build room descriptors with real-world dims (ft) and pixel dims
        room_rects = []
        for name, a in zip(rooms, room_areas):
            key = name.lower()
            # find aspect range
            ar_min, ar_max = (1.0, 1.3)
            for k, (mn, mx) in aspect_map.items():
                if k in key:
                    ar_min, ar_max = mn, mx
                    break
            # pick middle of range for deterministic layout
            aspect = (ar_min + ar_max) / 2.0

            # width_ft * height_ft = area, width/height = aspect => width = sqrt(area * aspect)
            width_ft = math.sqrt(max(1.0, a) * aspect)
            height_ft = max(1.0, a) / width_ft

            w_px = max(12, int(round(width_ft * ppf)))
            h_px = max(12, int(round(height_ft * ppf)))

            room_rects.append({
                "name": name,
                "area_sq_ft": round(a, 1),
                "width_ft": round(width_ft, 1),
                "height_ft": round(height_ft, 1),
                "w_px": w_px,
                "h_px": h_px,
            })

        # pack rooms into rows (simple greedy packing)
        rows = []
        current_row = {"width": 0, "height": 0, "rooms": []}
        max_floor_w_px = int(round(floor_w_ft * ppf))
        if max_floor_w_px < 40:
            max_floor_w_px = avail_w

        for r in room_rects:
            if current_row["rooms"] and (current_row["width"] + r["w_px"] + 8) > max_floor_w_px:
                rows.append(current_row)
                current_row = {"width": 0, "height": 0, "rooms": []}
            # add room to current row
            x_in_row = current_row["width"]
            current_row["rooms"].append((r, x_in_row))
            current_row["width"] += r["w_px"] + 8
            current_row["height"] = max(current_row["height"], r["h_px"])

        if current_row["rooms"]:
            rows.append(current_row)

        # compute total used height and possible vertical scaling if overflow
        total_rows_h = sum(row["height"] for row in rows) + (len(rows) - 1) * 8
        if total_rows_h > avail_h and total_rows_h > 0:
            v_scale = (avail_h / total_rows_h)
        else:
            v_scale = 1.0

        # emit room boxes with positions
        room_boxes = []
        y_cursor = margin
        for row in rows:
            row_h = int(round(row["height"] * v_scale))
            x_cursor = margin
            for r, x_offset in row["rooms"]:
                w = int(round(r["w_px"]))
                h = int(round(r["h_px"] * v_scale))
                # if the row width fits in the available width center it
                # compute row content width to center the row
            # compute row content width to support centering
            row_content_width = sum(int(round(rr[0]["w_px"])) + 8 for rr in row["rooms"]) - 8
            row_x_start = margin + max(0, (avail_w - row_content_width) // 2)
            x_cursor = row_x_start
            for r, x_offset in row["rooms"]:
                w = int(round(r["w_px"]))
                h = int(round(r["h_px"] * v_scale))
                name = r["name"]
                width_ft = r["width_ft"]
                height_ft = r["height_ft"]
                dims = f"{int(round(width_ft))}' x {int(round(height_ft))}'"

                # allow room_options override per room (match by substring key)
                lowkey = name.lower()
                matched_opts = {}
                if isinstance(room_options, dict):
                    for k, v in room_options.items():
                        if k.lower() in lowkey:
                            matched_opts = v
                            break

                # compute door placement: default on shorter wall center unless overridden
                door_w_px = max(12, int(round(3 * ppf)))
                door_h_px = max(8, int(round(7 * ppf)))
                door_side = matched_opts.get('door_side') if isinstance(matched_opts, dict) else None
                doors_count = int(matched_opts.get('doors', 1)) if isinstance(matched_opts, dict) and 'doors' in matched_opts else 1

                doors = []
                def add_door_at(side):
                    if side == 'top':
                        return {"x": int(x_cursor + (w - door_w_px) / 2), "y": int(y_cursor - 1), "w": door_w_px, "h": 4, "orientation": "top"}
                    if side == 'bottom':
                        return {"x": int(x_cursor + (w - door_w_px) / 2), "y": int(y_cursor + h - 1), "w": door_w_px, "h": 4, "orientation": "bottom"}
                    if side == 'left':
                        return {"x": int(x_cursor - 1), "y": int(y_cursor + (h - door_h_px) / 2), "w": 4, "h": door_h_px, "orientation": "left"}
                    return {"x": int(x_cursor + w - 1), "y": int(y_cursor + (h - door_h_px) / 2), "w": 4, "h": door_h_px, "orientation": "right"}

                if door_side:
                    doors.append(add_door_at(door_side))
                else:
                    # default heuristic
                    if w >= h:
                        doors.append(add_door_at('bottom'))
                    else:
                        doors.append(add_door_at('right'))
                # additional doors if requested
                if doors_count > 1:
                    # place extra door on opposite side
                    opp = 'top' if doors[0]['orientation'] == 'bottom' else 'left' if doors[0]['orientation'] == 'right' else 'right'
                    doors.append(add_door_at(opp))

                # windows: decide from matched_opts or defaults for main room types
                window_w_px = max(12, int(round(4 * ppf)))
                window_h_px = max(8, int(round(3 * ppf)))
                windows = []
                if isinstance(matched_opts, dict) and 'windows' in matched_opts:
                    num_windows = int(matched_opts.get('windows', 0))
                    win_side = matched_opts.get('window_side', 'top')
                else:
                    if any(k in lowkey for k in ("living", "bedroom", "kitchen", "dining", "master", "guest")):
                        num_windows = 2 if w > 220 else 1
                        win_side = 'top'
                    else:
                        num_windows = 0
                        win_side = 'top'

                for wi in range(num_windows):
                    if num_windows == 1:
                        wx = x_cursor + int((w - window_w_px) / 2)
                    else:
                        spacing = max(4, (w - (num_windows * window_w_px)) // (num_windows + 1))
                        wx = x_cursor + spacing * (wi + 1) + window_w_px * wi
                    if win_side == 'top':
                        wy = y_cursor - 1
                    elif win_side == 'bottom':
                        wy = y_cursor + h - window_h_px
                    elif win_side == 'left':
                        wx = x_cursor - 1
                        wy = y_cursor + int((h - window_h_px) / 2)
                    else:
                        wx = x_cursor + w - window_w_px
                        wy = y_cursor + int((h - window_h_px) / 2)
                    windows.append({"x": int(wx), "y": int(wy), "w": window_w_px, "h": window_h_px, "orientation": win_side})

                room_boxes.append({
                    "name": name,
                    "area_sq_ft": r["area_sq_ft"],
                    "dims": dims,
                    "x": int(x_cursor),
                    "y": int(y_cursor),
                    "w": w,
                    "h": h,
                    "doors": doors,
                    "windows": windows
                })
                x_cursor += w + 8
            y_cursor += row_h + 8

        layout.append({"floor": floor_name, "canvas": {"w": canvas_w, "h": canvas_h}, "rooms": room_boxes})

    return layout
