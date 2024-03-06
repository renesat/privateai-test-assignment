<script lang="ts">
  import { onMount } from "svelte";
  import * as d3 from "d3";

  export let data;
  export let width = 900;
  export let height = 400;

  console.log(data);
  $: nodes = data.nodes;
  $: links = data.links;

  // Utils
  function selectNode(event) {
    if (event.target.tagName === "circle") {
      view_node = event.target.id;
    } else {
      view_node = null;
    }
  }

  function isNeighbors(node1, node2) {
    for (const i in links) {
      if (
        (links[i].source.id == node1 && links[i].target.id == node2) ||
        (links[i].source.id == node2 && links[i].target.id == node1)
      ) {
        return true;
      }
    }
    return false;
  }

  function setNodeDragable(node) {
    const dragDop = d3
      .drag()
      .on("start", (event, d) => {
        node.fx = node.x;
        node.fy = node.y;
      })
      .on("drag", (event, d) => {
        simulation.alphaTarget(0.3).restart();
        node.fx = event.x;
        node.fy = event.y;
      })
      .on("end", (event, d) => {
        if (!event.active) {
          simulation.alphaTarget(0);
        }
        node.fx = null;
        node.fy = null;
      });

    const svgElem = document.getElementById(node.id);
    d3.select(svgElem).call(dragDop);
  }

  // Simulation
  $: _nodes = nodes;
  $: _links = links;

  function updateSimulation() {
    _nodes = nodes;
    _links = links;
    return nodes;
  }

  $: simulation = d3
    .forceSimulation(nodes)
    .force("charge", d3.forceManyBody().strength(-400))
    .force("x", d3.forceX())
    .force("y", d3.forceY())
    .force(
      "link",
      d3
        .forceLink(links)
        .id((d) => d.id)
        .strength((link) => 0.5),
    )
    .on("tick", updateSimulation);

  // Mount
  let view_node = null;
  let nodesGroup;
  let svgElement;

  let viewBox = [-width / 2, -height / 2, width, height];
  let transform;

  onMount(() => {
    // Dragable
    nodes.forEach(setNodeDragable);

    // Zoom
    let zoom = d3.zoom().on("zoom", function (event) {
      var ntransform = event.transform;
      console.log(transform);
      viewBox = [
        -width / 2 / ntransform.k + ntransform.x * 0.5,
        -height / 2 / ntransform.k + ntransform.y * 0.5,
        width / ntransform.k,
        height / ntransform.k,
      ];
    });

    d3.select(svgElement).call(zoom);
  });
</script>

<svg
  on:click={selectNode}
  {viewBox}
  preserveAspectRatio="xMidYMid meet"
  bind:this={svgElement}
  {transform}
>
  <g stroke-width="1.5">
    {#each _links as link}
      <line
        x1={link.source.x}
        y1={link.source.y}
        x2={link.target.x}
        y2={link.target.y}
        stroke={link.source.id == view_node || link.target.id == view_node
          ? "#F36F38"
          : "#656771"}
      />
    {/each}
  </g>
  <g bind:this={nodesGroup} fill="white" stroke="656771" stroke-width="1.5">
    {#each _nodes as node}
      <circle
        id={node.id}
        class="node-circle"
        fill={view_node == node.id
          ? "#F1828D"
          : view_node && !isNeighbors(view_node, node.id)
            ? "#497061"
            : "#8FB9A8"}
        fx={node.fx}
        fy={node.fx}
        cx={node.x}
        cy={node.y}
        r="5"
        on:click={(e) => (view_node = node.id)}
      />
    {/each}
  </g>
  <g fill="#8ea2f8" stroke="#FEFAD4" stroke-width="0.2">
    {#each _nodes as node}
      <text font-size="10" dx="10" dy="4" x={node.x} y={node.y}>{node.id}</text>
    {/each}
  </g>
</svg>

<style>
  svg {
    display: inline-block;
  }
</style>
