class TreeDrawer:
    def __init__(self, canvas, node_radius=40, v_spacing=160, h_spacing=100, font=("Arial", 12)):
        self.canvas = canvas
        self.node_radius = node_radius
        self.v_spacing = v_spacing
        self.h_spacing = h_spacing
        self.font = font
        self.positions = {}  # token_id -> (x,y)

    def _measure_leaf_count(self, node):
        """Считает 'ширину' поддерева в единицах листа."""
        children = node.get("children", [])
        if not children:
            return 1
        return sum(self._measure_leaf_count(ch) for ch in children)

    def _assign_positions(self, node, x_start, y, level=0):
        """
        node: dict {"text":..., "children":[...]}
        x_start: left-most x (in units)
        y: pixel y
        """
        leaf_count = self._measure_leaf_count(node)
        # center x (in units)
        x_center_units = x_start + (leaf_count - 1) / 2.0
        x = int(x_center_units * self.h_spacing)
        self.positions[id(node)] = (x, y)

        # assign children positions
        cur = x_start
        for ch in node.get("children", []):
            ch_leaves = self._measure_leaf_count(ch)
            self._assign_positions(ch, cur, y + self.v_spacing, level + 1)
            cur += ch_leaves

    def draw(self, tree):
        """Основной метод: очищает canvas, рассчитывает layout, рисует."""
        self.canvas.delete("all")
        self.positions = {}

        # safety
        if tree is None:
            return

        # compute total leaves to determine width
        total_leaves = self._measure_leaf_count(tree)
        # ensure canvas large enough: set scrollregion later
        # set starting x offset a bit to the right
        x_offset = self.h_spacing
        y_offset = self.node_radius + 10

        # assign positions in unit-space starting at 0
        self._assign_positions(tree, 0, y_offset)

        # find min/max coords
        xs = [pos[0] for pos in self.positions.values()]
        ys = [pos[1] for pos in self.positions.values()]
        if not xs:
            return
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # translate all x by x_offset - min_x to get positive coords
        translate_x = x_offset - min_x

        # draw edges first
        def draw_edges(node):
            x, y = self.positions[id(node)]
            x += translate_x
            for ch in node.get("children", []):
                cx, cy = self.positions[id(ch)]
                cx += translate_x
                # line from bottom of parent to top of child
                self.canvas.create_line(x, y + self.node_radius - 2, cx, cy - self.node_radius + 2)
                draw_edges(ch)
        draw_edges(tree)

        # draw nodes (so they appear over lines)
        def draw_nodes(node):
            x, y = self.positions[id(node)]
            x += translate_x
            # oval
            self.canvas.create_oval(
                x - self.node_radius, y - self.node_radius,
                x + self.node_radius, y + self.node_radius,
                fill="#e3f2fd", outline="#1976d2"
            )
            # text (wrap by width ~ node_radius*2)
            self.canvas.create_text(x, y, text=node["text"], font=self.font, width=self.node_radius * 2)
            for ch in node.get("children", []):
                draw_nodes(ch)
        draw_nodes(tree)

        pad = 50
        min_canvas_x = min_x + translate_x - self.node_radius - pad
        max_canvas_x = max_x + translate_x + self.node_radius + pad
        min_canvas_y = min_y - self.node_radius - pad
        max_canvas_y = max_y + self.node_radius + pad
        self.canvas.configure(scrollregion=(min_canvas_x, min_canvas_y, max_canvas_x, max_canvas_y))
