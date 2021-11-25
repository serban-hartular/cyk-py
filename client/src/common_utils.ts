import type { TreeLibrary } from "./parse_tree"



export function root_to_str_rep(root_ids : Array<string>, tree_library : TreeLibrary) : string {
    let types : string = root_ids.map(id => tree_library.get(id).type).join(',')
    return types
}
export function score2string(node_ids : Array<string>, tree_library : TreeLibrary): string {
    let str_array = new Array<string>()
    for(let id of node_ids) {
        let node = tree_library.get(id)
        let str = // String(Math.log10(node.score).toFixed(2)) + '/' + 
            String(node.nscore.toFixed(2))
        str_array.push(str)
    }
    return str_array.join(',')
}
