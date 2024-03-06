<script lang="ts">
  import PaperGraph from "./lib/PaperGraph.svelte";

  import "svelte-material-ui/themes/material-dark.css";
  import Button from "@smui/button";
  import CircularProgress from "@smui/circular-progress";
  import Select, { Option } from "@smui/select";
  import DataTable, { Head, Body, Row, Cell } from "@smui/data-table";
  import Textfield from "@smui/textfield";

  import { onMount } from "svelte";

  import { getPapersList, getPaperInfo, uploadPaper } from "./lib/utils.js";

  let paperFiles = null;

  let current_paper = null;

  let papers = getPapersList();

  let cur_paper = null;
  $: paper_info = cur_paper != null ? getPaperInfo(cur_paper) : null;
</script>

<link rel="stylesheet" href="node_modules/svelte-material-ui/bare.css" />
<main>
  <h1>Paper Knowlage Graphs (PrivateAI)</h1>
  <dev class="upload-button">
    <Textfield bind:files={paperFiles} label="Select File" type="file" />
    <Button on:click={(e) => uploadPaper(paperFiles[0])}>Upload paper</Button>
  </dev>
  <Button on:click={(e) => (papers = getPapersList())}
    >Reload papers list</Button
  >
  {#await papers}
    <CircularProgress indeterminate style="height: 32px; width: 32px;" />
  {:then values}
    <DataTable stickyHeader table$aria-label="User list" style="width: 80%;">
      <Head>
        <Row>
          <Cell>ID</Cell>
          <Cell style="width: 100%;">Title</Cell>
        </Row>
      </Head>
      <Body>
        {#each values as paper}
          <Row on:click={(e) => (cur_paper = paper.id)}>
            <Cell class={cur_paper == paper.id ? "current-row" : ""}
              >{paper.id}</Cell
            >
            <Cell class={cur_paper == paper.id ? "current-row" : ""}
              >{paper.title}</Cell
            >
          </Row>
        {/each}
      </Body>
    </DataTable>
  {/await}
  {#if cur_paper != null}
    {#await paper_info}
      <p>Paper loading ...</p>
      <CircularProgress indeterminate style="height: 32px; width: 32px;" />
    {:then values}
      <h2 class="title">{values.meta.title}</h2>
      <div id="paper-graph" class="svg-container">
        <PaperGraph data={values.kg} />
      </div>
    {:catch error}
      <p style="color: red">{error.message}</p>
    {/await}
  {/if}
</main>

<style>
  .svg-container {
    border: 3px solid;
    display: inline-block;
    position: relative;
    width: 70%;

    vertical-align: top;
    overflow: hidden;
  }
  .title {
    text-align: center;
    font-style: italic;
  }
  .upload-button {
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    /* background-color: var(--mdc-theme-primary, #333); */
  }
  :global(.current-row) {
    background-color: "blue";
  }

  .upload-button :global(input[type="file"]::file-selector-button) {
    display: none;
  }

  .upload-button
    :global(:not(.mdc-text-field--label-floating) input[type="file"]) {
    color: transparent;
  }
</style>
