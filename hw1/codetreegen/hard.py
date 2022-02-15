import inspect
import ast
import os
# import astunparse
from PIL import Image, ImageFont, ImageDraw

from codetreegen.easy import fib

class Edge:
    def __init__(self, to, color=None, text=None):
        self.to = to
        self.color = color
        self.text = text

    def __str__(self):
        return f"Edge(color={self.color}, text={self.text}, to={self.to})"


class TreeNode:
    def __init__(self):
        self.color = None
        self.name = ""
        self.text = None
        self.edges = []
        self.attributes = {}
    
    def add_edge(self, child, color=None, text=None):
        self.edges.append(Edge(child, color=color, text=text))

    def __str__(self):
        comma = ", "
        return f"TreeNode(color={self.color}, name=\"{self.name}\", text=\"{self.text}\", edges=[{comma.join(str(edge) for edge in self.edges)}])"




def parse_to_graph(ast_node):
    tree_node = TreeNode()

    body_color = (102,51,0)
    loop_color = (0,51,102)
    name_color = (17, 102, 0)
    const_color = (0, 102, 51)
    call_color = (0, 213, 255)

    def parse_body(body_list):
        body_node = TreeNode()
        body_node.color = body_color
        body_node.name = "<body>"

        for statement in body_list:
            body_node.add_edge(parse_to_graph(statement))
        
        return body_node

    if type(ast_node) is ast.Module:
        tree_node.name = "Module"
        tree_node.add_edge(parse_body(ast_node.body))
    elif type(ast_node) is ast.FunctionDef:
        tree_node.name = "function"
        tree_node.text = f"def {ast_node.name}"
        
        tree_node.add_edge(parse_to_graph(ast_node.args))
        tree_node.add_edge(parse_body(ast_node.body))
    elif type(ast_node) is ast.arguments:
        tree_node.name = "arguments"
        for arg in ast_node.args:
            tree_node.add_edge(parse_to_graph(arg))
        if ast_node.vararg is not None:
            tree_node.add_edge(parse_to_graph(ast_node.vararg), text="vararg")
        for arg in ast_node.kwonlyargs:
            tree_node.add_edge(parse_to_graph(arg), text="kword only")
        if ast_node.kwarg is not None:
            tree_node.add_edge(parse_to_graph(ast_node.kwarg), text="kwarg")
            
    elif type(ast_node) is ast.arg:
        tree_node.name = "arg"
        tree_node.color = name_color
        tree_node.text = ast_node.arg

    elif type(ast_node) is ast.Assign:
        tree_node.name = "Assign"
        for target in ast_node.targets:
            tree_node.add_edge(parse_to_graph(target))

        tree_node.add_edge(parse_to_graph(ast_node.value))

    elif type(ast_node) is ast.Constant:
        tree_node.name = "Constant"
        tree_node.color = const_color
        tree_node.text = str(ast_node.value)

    elif type(ast_node) is ast.Name:
        tree_node.name = "Name"
        tree_node.color = name_color
        tree_node.text = str(ast_node.id)

    elif type(ast_node) is ast.Tuple:
        tree_node.name = "Tuple"
        for elt in ast_node.elts:
            tree_node.add_edge(parse_to_graph(elt))

    elif type(ast_node) is ast.List:
        tree_node.name = "List"
        for elt in ast_node.elts:
            tree_node.add_edge(parse_to_graph(elt))

    elif type(ast_node) is ast.For:
        tree_node.name = "for"
        tree_node.color = loop_color
        tree_node.add_edge(parse_to_graph(ast_node.target), text="target")
        tree_node.add_edge(parse_to_graph(ast_node.iter), text="iter")
        tree_node.add_edge(parse_body(ast_node.body), text="body")
        if ast_node.orelse:
            tree_node.add_edge(parse_body(ast_node.orelse), text="else-body")

    elif type(ast_node) is ast.Call:
        tree_node.name = "Call"
        tree_node.color = call_color
        tree_node.add_edge(parse_to_graph(ast_node.func), text="func")
        for arg in ast_node.args:
            tree_node.add_edge(parse_to_graph(arg), text="arg")

    elif type(ast_node) is ast.Return:
        tree_node.name = "Return"
        tree_node.add_edge(parse_to_graph(ast_node.value))

    elif type(ast_node) is ast.Attribute:
        tree_node.name = "Attribute"
        tree_node.text = f".{ast_node.attr}"
        tree_node.add_edge(parse_to_graph(ast_node.value), text="???.")

    elif type(ast_node) is ast.Expr:
        tree_node.name = "Expr"
        tree_node.add_edge(parse_to_graph(ast_node.value))

    elif type(ast_node) is ast.BinOp:
        tree_node.name = "BinOp"
        tree_node.text = type(ast_node.op).__name__
        tree_node.add_edge(parse_to_graph(ast_node.left))
        tree_node.add_edge(parse_to_graph(ast_node.right))

    else:
        tree_node.name = "{" + type(ast_node).__name__ + "}"

    
    return tree_node

class TreeDrawer:
    def __init__(self):
        self.letter_width = 7
        self.letter_height = 9
        self.text_distance_v = 5
        self.box_padding_inside = 5
        self.box_padding_outside = 10
        self.box_vertical_distance = 20
        self.default_box_color = "gray"
        self.default_arrow_color = "black"

    def calc_sizes(self, root):
        has_text = root.text is not None
        max_text_length = max(len(t) for t in [root.name, root.text] if t is not None)
        root.attributes["box_width"] = max_text_length * self.letter_width + 2 * self.box_padding_inside
        root.attributes["box_height"] =  self.letter_height + self.box_padding_inside * 2 + has_text * (self.letter_height + self.text_distance_v)

        max_child_height = 0
        sum_child_width = 0

        for edge in root.edges:
            self.calc_sizes(edge.to)
            max_child_height = max(max_child_height, edge.to.attributes["subtree_height"])
            sum_child_width += edge.to.attributes["subtree_width"]
        
        root.attributes["subtree_height"] = root.attributes["box_height"] + 2 * self.box_padding_outside + max_child_height + self.box_vertical_distance
        root.attributes["subtree_width"] = max(sum_child_width, root.attributes["box_width"] + 2 * self.box_padding_outside)
    
    def calc_positions(self, root, offset_x=0, offset_y=0):
        self.calc_sizes(root)
        root.attributes["x_center"] = offset_x + root.attributes["subtree_width"] // 2
        root.attributes["y_top"] = offset_y + self.box_padding_outside
        
        offset_y += root.attributes["box_height"] + 2 * self.box_padding_outside + self.box_vertical_distance

        for edge in root.edges:
            self.calc_positions(edge.to, offset_x, offset_y)
            offset_x += edge.to.attributes["subtree_width"]

    def draw(self, root):
        self.calc_positions(root)
        
        im = Image.new(mode="RGB", size=(root.attributes["subtree_width"], root.attributes["subtree_height"]), color="white")
        draw = ImageDraw.Draw(im)
        
        self.draw_subtree(root, draw)
        return im
        

    def draw_subtree(self, root, draw):
        x_center = root.attributes["x_center"]
        y_top = root.attributes["y_top"]
        width = root.attributes["box_width"]
        height = root.attributes["box_height"]

        box_color = root.color if root.color is not None else self.default_box_color
        draw.rectangle(((x_center - width//2, y_top),(x_center + width//2, y_top + height)), fill=box_color)

        def text_centered(x_mid, y_top, text, center_y=False, **kwargs):
            w, h = draw.textsize(text)
            draw.text((x_mid - w // 2, y_top - center_y * h//2), text, **kwargs)

        text_centered(x_center, y_top + self.box_padding_inside, root.name)
        if root.text is not None:
            text_centered(x_center, y_top + self.box_padding_inside + self.text_distance_v + self.letter_height, root.text)

        for edge in root.edges:
            x_start = x_center
            y_start = y_top + height
            x_end = edge.to.attributes["x_center"]
            y_end = edge.to.attributes["y_top"]

            line_color = edge.color if edge.color is not None else self.default_arrow_color
            draw.line((x_start, y_start, x_end, y_end), fill=line_color)
            if edge.text is not None:
                text_centered((x_start + x_end) // 2, (y_start + y_end) // 2, edge.text, center_y=True, fill=line_color)
            self.draw_subtree(edge.to, draw)

def codetreegen(item):
    tree = parse_to_graph(ast.parse(inspect.getsource(item)))
    return TreeDrawer().draw(tree)


def main():
    # print(astunparse.dump(ast.parse(inspect.getsource(fib))))

    tree = parse_to_graph(ast.parse(inspect.getsource(fib)))

    # print(tree)

    im = TreeDrawer().draw(tree)
    try: 
        os.mkdir("artifacts") 
    except OSError as _: 
        pass

    im.save("artifacts/output.png", "PNG")

if __name__ == "__main__":
    main()