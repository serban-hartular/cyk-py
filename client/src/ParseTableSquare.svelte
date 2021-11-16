<script lang="ts">
import { get } from "svelte/store";
import type { TreeLibrary } from "./parse_tree";
import { score2string } from "./common_utils"

export let tree_library : TreeLibrary
export let id_list : Array<string>
export let parse_root : Array<string>


    function classFromId(id: string) {
        // if(id == tree_library.selected)
        //     return 'selected'
        // if(tree_library.selected_children.includes(id))
        //     return 'child'
        // if(tree_library.selected_descendants.includes(id))
        //     return 'descendant'
        return 'default'
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

<!-- <select bind:value={selected} on:change="{() => selected = selected}" required>
        <option value="" selected disabled hidden>nodes</option>
    {#each id_list as id}
        <option value={id}>{tree_library.get(id).type} ({score2string([id], tree_library)})</option>
    {/each}
</select> -->

{#if !id_list || id_list.length == 0}
<br/>
{:else}
    {#each id_list as id}
    <!-- <p class={classFromId(id)} on:click={() => selected = id}> -->
        <span on:click={()=>parse_root=[id]}>
        {#if parse_root && parse_root.includes(id)}
        <b>{tree_library.get(id).type},</b>
        {:else}
        {tree_library.get(id).type} 
        {/if}
        </span>
    <!-- </p> -->
    {/each}
{/if}
<style>
    

    /* p {
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
    } */
</style>