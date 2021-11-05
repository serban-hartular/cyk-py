export default class Tree {
    data : Object
    id : number
    rule : string
    score : number
    type : string
    form : string
    children_ids : Array<number>
    children : Array<Tree>
    constructor(json_node : Object) {
        this.data = json_node['data']
        this.id = json_node['id']
        this.rule = json_node['rule']
        this.score = Number(json_node['score'])
        this.type = json_node['type']
        this.form = json_node['form']
        this.children_ids = json_node['children']
        this.children = null
    }
}

export class TreeLibrary {
    tree_map : Map<number, Tree>
    position_map : Map<number, [number, number]>
    parse_table : Array<Array<Array<number>>>
    selected : number = undefined
    selected_children = new Array<number>()
    selected_descendants = new Array<number>()

    constructor(tree_list : any, parse_table : any) {
        let last_id = -1
        this.tree_map = new Map<number, Tree>()
        for(let tree of tree_list) {
            this.tree_map.set(tree.id, new Tree(tree))
            last_id = tree.id
        }
        this.position_map = new Map<number, [number, number]>()
        this.parse_table = new Array<Array<Array<number>>>()
        for(let row_index = 0; row_index < parse_table.length; row_index++) {
            let row = new Array<Array<number>>()
            for(let col_index = 0; col_index < parse_table[row_index].length; col_index++) {
                let square = new Array<number>()
                let score_sum = 0
                for(let tree_index = 0; tree_index < parse_table[row_index][col_index].length; tree_index++) {
                    let id = parse_table[row_index][col_index][tree_index]
                    square.push(id)
                    score_sum += this.get(id).score
                    // console.log(score_sum)
                    this.position_map.set(parse_table[row_index][col_index][tree_index], [row_index, col_index])
                }
                row.push(square)
                for(let item of square) //normalize scores
                    this.get(item).score /= score_sum
            }
            this.parse_table.push(row)
        }
        this.parse_table.reverse()
        this.setSelected(last_id)
    }

    get(id : number) {
        return this.tree_map.get(id)
    }
    children(id : number) {
        return this.get(id).children_ids
    }

    isParent(parent_id : number, child_id : number) {
        return this.children(parent_id).includes(child_id)
    }

    setSelected(id : number) {
        this.selected = id
        if(id == undefined) return
        let tree = this.tree_map.get(id)
        if(!tree) return
        this.selected_children = tree.children_ids
        this.selected_descendants = new Array<number>()
        for(let child_id of this.selected_children)
            this.selected_descendants = this.selected_descendants.concat(this.getDescendants(child_id))
    }
    getDescendants(id : number) : Array<number> {
        let ids = []
        for(let child_id of this.tree_map.get(id).children_ids) {
            ids = ids.concat([child_id])
            ids = ids.concat(this.getDescendants(child_id))
        }
        return ids
    }

    isSelectedOrDescendant(id : number) : boolean {
        return id == this.selected || this.selected_children.includes(id) 
            || this.selected_descendants.includes(id)
    }
}