<script lang="ts">
import { get } from "svelte/store";
import type { TreeLibrary } from "./parse_tree";

export let tree_library : TreeLibrary
export let id_list : Array<string>

    function classFromId(id: string) {
        // if(id == tree_library.selected)
        //     return 'selected'
        // if(tree_library.selected_children.includes(id))
        //     return 'child'
        // if(tree_library.selected_descendants.includes(id))
        //     return 'descendant'
        return 'default'
    }

    function score2string(score : number): string {
        return Math.log10(score).toFixed(2)
    }

    let selected : string = ""
    let to_display = Array<string>()
    let ordered_display = new Array<string>()

$:{ tree_library;
    to_display = id_list.filter(id => true) //tree_library.isSelectedOrDescendant(id))
    ordered_display = new Array<string>()
    if(to_display.length > 0) {
        //fill in ordered_display, parent first, child next, grandkid next, etc
        ordered_display.push(to_display.pop())
        while(to_display.length > 0) {
            let no_child_found = true
            for(let index = 0; index < to_display.length; index++) {
                let id = to_display[index]
                if(tree_library.isParent(id, ordered_display[0])) { //insert at beginning
                    ordered_display.splice(0, 0, id)
                    to_display.splice(index, 1)
                    no_child_found = false
                    break
                }
                if(tree_library.isParent(ordered_display[ordered_display.length-1], id)) {
                    //insert at end
                    ordered_display.push(id)
                    to_display.splice(index, 1)
                    no_child_found = false
                    break
                }
            }
            if(no_child_found) {
                // console.log('Error arranging list ' + String(to_display))
                break
            }
        }
    }
}

</script>

<select bind:value={selected} on:change="{() => selected = selected}" required>
        <option value="" selected disabled hidden>nodes</option>
    {#each id_list as id}
        <option value={id}>{tree_library.get(id).type} ({score2string(tree_library.get(id).score)})</option>
    {/each}
</select>

{#each ordered_display as id}
<p class={classFromId(id)} on:click={() => selected = id}>
    {tree_library.get(id).type}
    {#if tree_library.children(id).length == 0}
        <br/>{tree_library.get(id).form}
    {/if}
</p>
{/each}

<style>
    p {
        user-select: none; 
        margin-top: 6px;
        margin-bottom: 6px;
    }
    select {
        padding:0px
    }
    .default {
        background-color: #FFFFFF;
    }
    .selected {
        background-color: #AAAAFF;
        border-width: 3px;
        border-style: solid;
    }
    .child {
        background-color: #CCCCFF;
        border-width: 3px;
        border-style: dotted;
    }
    .descendant {
        background-color: #E0E0FF;
    }
</style>