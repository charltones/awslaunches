class DarkSolarizedTheme:
    DARKGREYBLUE = '#012b37'
    # Palette from http://ethanschoonover.com/solarized
    YELLOW = '#b58900'
    ORANGE = '#cb4b16'
    VIOLET = '#6c71c4'
    RED = '#dc323f'
    BLUE = '#268bd2'
    MAGENTA = '#d33682'
    CYAN = '#2aa198'
    GREEN = '#859900'
    GREY = '#939393'

    EDGE_COLORS = [YELLOW, ORANGE, VIOLET, RED, BLUE, MAGENTA, CYAN, GREEN, GREY]

    def __init__(self, layout, font):
        self.graph_style = dict(
            layout=layout,
            overlap='false',
            splines='curved',
            fontname=font,
            bgcolor=self.DARKGREYBLUE,
        )

    def edge_style(self, dest_node, graph_height, hide_branches_from_id=None):
        color = self.graph_style['bgcolor'] if hide_branches_from_id is not None and dest_node.branch_id >= hide_branches_from_id \
                                            else self.EDGE_COLORS[dest_node.branch_id % len(self.EDGE_COLORS)]
        return dict(
            color=color,
            dir='none',
            penwidth=2 * (2 + graph_height - dest_node.depth),
        )

    def node_style(self, node, graph_height, hide_branches_from_id=None):
        color = self.graph_style['bgcolor'] if hide_branches_from_id is not None and node.branch_id >= hide_branches_from_id \
                                            else 'white'
        label = node.content.strip() if node.content and node.content != node.ROOT_DEFAULT_NAME else ''
        return dict(
            group=node.branch_id,
            shape='plaintext',
            label=label,
            fontcolor=color,
            fontsize=2 * (16 + graph_height - node.depth),
            fontname=self.graph_style['fontname'], # not inherited by default
        )