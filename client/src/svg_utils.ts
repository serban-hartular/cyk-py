
import  type { Node, TreeLibrary } from "./parse_tree";

type Coordinate = [number, number]

export default class SvgNode {
    static dx : number = 64
    static dy : number = 32
    id : string
    text : string
    //origin :Coordinate= [0, 0]
    x : number
    y : number
    w : number = 0
    h : number = 0
    mid_x : number
    top_y : number
    row : number
    col : number
    children_deprels : Array<string> 
    //svg_element : SVGGraphicsElement
    children : Array<string>
    constructor(id : string, text : string, children : Array<string>,
            children_deprels : Array<string>) {
        this.id = id
        this.text = text
        this.children = children
        this.children_deprels = children_deprels
    }
    calcTopBottom() {
        this.mid_x =    this.x + this.w / 2
        this.top_y =    this.y - this.h / 2
    }
    setMidX(mid_x : number) {
        this.mid_x = mid_x
        this.x = this.mid_x - this.w / 2
    }
}

export class Line {
    parent_id: string
    child_id: string
    x1 : number
    x2 : number
    y1 : number
    y2 : number
    deprel : string
    constructor(parent_id : string, child_id: string, x1 : number, y1 : number, x2 : number, y2 : number,
        deprel : string = '') {
        this.parent_id = parent_id
        this.child_id = child_id
        this.x1 = x1
        this.y1 = y1
        this.x2 = x2
        this.y2 = y2
        this.deprel = deprel
    }
}

export class SvgMap extends Map<string, SvgNode>{
    width : number = 300
    height : number = 300
    lines : Array<Line> = new Array<Line>()
    root_list : Array<string>
    static top_offset_y = 2
    static bottom_offset_y = 5
    static width_padding = 5
    width_array : Array<number>
    x_array : Array<number>
  
    constructor(tree_library : TreeLibrary, root_list : Array<string>) {
        super()
        this.root_list = root_list
        //let word_map = new Map<string, Array<string>>()
        for(let root_id of this.root_list) {
            for(let id of tree_library.traverse(root_id)) {
                let tree = tree_library.get(id)
                let node = new SvgNode(id, tree.type, tree.children_ids, tree.children_deprels)
                let [row, col] = tree_library.position_map.get(id)
                node.row = row
                node.col = col
                this.set(id, node)
                if(tree.children_ids.length == 0) { //this is a leaf
                    //add a word node
                    let word = new SvgNode('w'+id, tree.form, [], [])
                    word.row = node.row + 1
                    word.col = node.col
                    node.children = [word.id]
                    this.set(word.id, word)
                    // this.setSuffix(word, word_map)
                }
            }
            this.setFirstCoordinates(root_id)
        }
        this.generateLines()
    }

    // setSuffix(word : SvgNode, word_map : Map<string, Array<string>>) {
    //     if(!word_map.has(word.text)) {
    //         word_map.set()
    //     }
    // }

    getNodes() : Array<SvgNode> {
        return Array.from(this.values())
    }
    getLines() : Array<Line> {
        return this.lines
    }

    setFirstCoordinates(id : string, depth : number = 0) {
        let svg_node = this.get(id)
        svg_node.row = depth;
        svg_node.x = svg_node.col * SvgNode.dx
        svg_node.y = (svg_node.row + 1) * SvgNode.dy
        svg_node.calcTopBottom()
        for(let child_id of svg_node.children)
            this.setFirstCoordinates(child_id, depth+1)
    }
    generateLines() {
        this.lines = new Array<Line>()
        for(let parent of Array.from(this.values())) {
            for(let i = 0; i < parent.children.length; i++) {
                let child_id = parent.children[i]
                let deprel = parent.children_deprels[i]
                if(deprel == 'h') deprel = '' //don't display head
                let child = this.get(child_id)
                let line = new Line(parent.id, child_id,
                    parent.mid_x, parent.y + SvgMap.top_offset_y,
                    child.mid_x, child.top_y - SvgMap.bottom_offset_y, deprel)
                this.lines.push(line)
            }
        }
    }
    updateCoordinates() {
        //first calculate max width of each column
        let width_map = new Map<number, number>()
        let max_col = 0
        for(let node of this.values()) {
            let current_w = width_map.get(node.col)
            if(current_w == undefined || current_w < node.w)
                width_map.set(node.col, node.w)
            if(node.col > max_col) max_col = node.col
            if(node.y > this.height) this.height = node.y
        }
        if(this.height > 300) this.height += 10
        max_col += 1
        this.width_array = new Array<number>()
        this.x_array = new Array<number>()
        for(let col = 0; col < max_col; col++) {
            this.width_array.push(width_map.get(col) == undefined ?
                0 : width_map.get(col) + SvgMap.width_padding)
            this.x_array.push(col == 0 ? 0 : this.width_array[col-1] + this.x_array[col-1])
        }
        this.width = this.x_array[this.x_array.length-1] + this.width_array[this.width_array.length-1]
        this.setMidpoints()
        this.generateLines()
    }
    setMidpoints(ids : Array<string> = this.root_list) {
        for(let id of ids) {
            let node = this.get(id)
            node.calcTopBottom()
            if(node.children.length == 0) {
                node.setMidX(this.x_array[node.col] + this.width_array[node.col] / 2)
                return
            }
            let midpoint_sum = 0
            for(let child_id of node.children) {
                this.setMidpoints([child_id])
                midpoint_sum += this.get(child_id).mid_x
            }
            node.setMidX(midpoint_sum / node.children.length)
        }
    }
}

