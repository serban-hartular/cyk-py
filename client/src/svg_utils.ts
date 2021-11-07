
import  type { Node, TreeLibrary } from "./parse_tree";

export default class SvgNode {
    static dx : number = 64
    static dy : number = 32
    id : string
    text : string
    x : number
    y : number
    private w : number = 0
    private h : number = 0
    row : number
    col : number
    top : [number, number]
    bottom : [number, number]
    svg_element : SVGGraphicsElement
    children : Array<string>
    constructor(id : string, text : string, children : Array<string>) {
        this.id = id
        this.text = text
        this.children = children
    }
    setDimensions(width : number, height : number) {
        this.w = width
        this.h = height
        this.calcTopBottom()
    }
    getDimensions() : [number, number] {
        return [this.w, this.h]
    }
    getTop() : [number,number] {
        return this.top
    }
    getBottom() : [number, number] {
        return this.bottom
    }
    calcTopBottom() {
        this.top =      [this.x + this.w / 2, this.y + this.h]
        this.bottom =   [this.x + this.w / 2, this.y]
    }
    static generateTree(tree_library : TreeLibrary, id : string, depth : number = 0) : Map<string, SvgNode> {
        let node = tree_library.get(id)
        let svg_node = new SvgNode(node.id, node.type, node.children_ids)
        let [row, col] = tree_library.position_map.get(id)
        svg_node.row = depth;
        svg_node.col = col
        svg_node.x = svg_node.col * SvgNode.dx
        svg_node.y = (svg_node.row + 1) * SvgNode.dy
        let map = new Map<string, SvgNode>()
        map.set(id, svg_node)
        // console.log(svg_node.id, depth, svg_node.y)
        for(let child of svg_node.children) {
            for(let [k, v] of SvgNode.generateTree(tree_library, child, depth+1))
                map.set(k, v)
        }
        return map
    }
    connectToDom(svg_element : SVGGraphicsElement) {
        this.svg_element = svg_element
        this.setDimensions(svg_element.getBBox().width, svg_element.getBBox().height)
    }
    static generatePositions(map : Map<number, SvgNode>) {
        let row_width_map = new Map<number, number>()
        let max_row = 0
        for (let [id, node] of map) { //find maximum width of each row
            if(!(row_width_map.get(node.row) > node.w)) {
                row_width_map.set(node.row, node.w)
            }
            max_row = node.row > max_row ? node.row : max_row
        }
        let row_limits = new Array<[number, number]>(max_row).fill([0, 0])
        row_limits[0][1] = row_width_map.get(0)
        if(row_limits[0][1] == undefined) throw Error('row 0 width undefined')
        for(let row = 1; row < max_row; row++) {
            let row_width = row_width_map.get(row)
            if(row_width == undefined) throw Error('row ' + String(row) + ' width undefined ')
            row_limits[row][0] = row_limits[row-1][1]
            row_limits[row][1] = row_limits[row][0] + row_width
        }
        for(let [id, node] of map) {
            let row = node.row
            node.x = (row_limits[row][0] + row_limits[row][1]) / 2 - node.w / 2
        }
    }
}

export class SvgTree extends Map<string, SvgNode> {
    constructor(tree_library : TreeLibrary, root_id : string) {
        super()
        let nodes = [root_id].concat(tree_library.getDescendants(root_id))
        for(let node of nodes) {

        }
    }
}

