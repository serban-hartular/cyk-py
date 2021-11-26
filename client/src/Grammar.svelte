<script lang="ts">

	import type { TreeLibrary } from "./parse_tree";
	import Square from "./ParseTableSquare.svelte";
import { onMount } from "svelte";

	// export let tree_library : TreeLibrary
	export let grammar : Array<string>
    export let grammar_change : boolean

    grammar_change = false

    function blurRule(id : number) {
        console.log(id, grammar[id])
        grammar_change = true
    }

    function splice(id : number, delCount : number, item : string = null) {
        if(item) {
            grammar.splice(id, delCount, item)
        } else {
            grammar.splice(id, delCount)
        }
        grammar = grammar
        grammar_change = true
    }

    //onMount(() => { console.log('mounting grammar'); grammar_change = false })

</script>

<h2>Grammar</h2>
<button on:click={() => grammar = ['     ']}>Clear</button>
<table>
    {#each grammar as rule, i}
        <tr>
            <td class="rulecell" contenteditable="true" on:blur={() => blurRule(i)}
                bind:textContent={rule}>
                <pre></pre>
            </td>
            <td class="buttons">
                <button class="insdel" on:click={() => splice(i+1, 0, '     ')}>Ins</button>
                <button class="insdel" on:click={() => splice(i, 1)    }>Del</button>
            </td>
        </tr>
        
    {/each}
</table>

<style>
    table, td {
        font-family: Arial, Helvetica, sans-serif;
        font-size: 11pt;
        border-spacing: 0px;
    }
    td {
        border: 1px solid black;
        border-collapse: collapse;
        padding: 0px;
        vertical-align: middle;
    }
    .buttons {
        white-space: nowrap;
    }
    .rulecell {
        font-family: 'Courier New', Courier, monospace;
        font-size: 11pt;
        min-width: 300px;
        max-width: 900px;
        white-space: pre;
    }
    .insdel {
        padding:0px;
    }
</style>