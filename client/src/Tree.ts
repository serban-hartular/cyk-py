export default class Tree {
    data : Map<string, Array<string>>
    id : number
    rule : string
    score : number
    type : string
    form : string
    children_ids : Array<number>
    children : Array<Tree>
}