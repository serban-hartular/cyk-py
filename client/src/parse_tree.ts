export class Node {
    data : Object
    id : string
    rule : string
    score : number
    type : string
    form : string
    children_ids : Array<string>
    children : Array<Node>
    children_deprels : Array<string>
    constructor(json_node : Object) {
        this.data = json_node['data']
        this.id = String(json_node['id'])
        this.rule = json_node['rule']
        this.score = Number(json_node['score'])
        this.type = json_node['type']
        this.form = json_node['form']
        this.children_ids = json_node['children'].map((n) => String(n))
        this.children = null
        this.children_deprels = new Array<string>()
        if(json_node['children_annot'] != undefined) {
            for(let annotation of json_node['children_annot']) {
                let deprel = annotation['deprel']
                this.children_deprels.push(deprel == undefined ? '' : deprel)
            }
        }
    }
}

export class TreeLibrary {
    tree_map : Map<string, Node>
    position_map : Map<string, [number, number]>
    parse_table : Array<Array<Array<string>>>
    selected : string = undefined
    selected_children = new Array<string>()
    selected_descendants = new Array<string>()

    constructor(tree_list : any, json_parse_table : any) {
        this.tree_map = new Map<string, Node>()
        for(let tree of tree_list) {
            this.tree_map.set(String(tree.id), new Node(tree))
        }
        //populate parse table
        this.parse_table = new Array<Array<Array<string>>>()
        for(let row_index = 0; row_index < json_parse_table.length; row_index++) {
            let row = new Array<Array<string>>()
            for(let col_index = 0; col_index < json_parse_table[row_index].length; col_index++) {
                let square = new Array<string>()
                for(let tree_index = 0; tree_index < json_parse_table[row_index][col_index].length; tree_index++) {
                    let id = json_parse_table[row_index][col_index][tree_index]
                    square.push(String(id))
                }
                row.push(square)
            }
            this.parse_table.splice(0, 0, row)
        }
        //populate position map
        this.position_map = new Map<string, [number, number]>()
        for(let row_index = 0; row_index < this.parse_table.length; row_index++) {
            for(let col_index = 0; col_index < this.parse_table[row_index].length; col_index++) {
                for(let tree_index = 0; tree_index < this.parse_table[row_index][col_index].length; tree_index++) {
                    this.position_map.set(this.parse_table[row_index][col_index][tree_index],
                        [row_index, col_index])
                }
            }
        }
        this.setSelected(this.parse_table[0][0][0])
    }

    get(id : string) {
        return this.tree_map.get(id)
    }
    children(id : string) {
        // console.log('Getting children of ' + id)
        return this.get(id).children_ids
    }

    isParent(parent_id : string, child_id : string) {
        return this.children(parent_id).includes(child_id)
    }

    setSelected(id : string) {
        this.selected = id
        if(id == undefined) return
        let tree = this.tree_map.get(id)
        if(!tree) return
        this.selected_children = tree.children_ids
        this.selected_descendants = new Array<string>()
        for(let child_id of this.selected_children)
            this.selected_descendants = this.selected_descendants.concat(this.getDescendants(child_id))
    }
    getDescendants(id : string) : Array<string> {
        let ids = []
        for(let child_id of this.children(id)) {
            ids = ids.concat([child_id])
            ids = ids.concat(this.getDescendants(child_id))
        }
        return ids
    }

    isSelectedOrDescendant(id : string) : boolean {
        return id == this.selected || this.selected_children.includes(id) 
            || this.selected_descendants.includes(id)
    }

    *traverse(id : string) {
        yield id
        for(let child_id of this.get(id).children_ids)
            for(let y of this.traverse(child_id))
                yield y
    }
}