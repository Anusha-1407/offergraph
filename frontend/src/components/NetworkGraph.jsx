import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import { ZoomIn, ZoomOut, Maximize2, RotateCcw, Filter, Search as SearchIcon } from 'lucide-react';

export default function NetworkGraph({
  elements,
  onNodeSelect,
  selectedNodeId,
  height = '600px'
}) {
  const containerRef = useRef(null);
  const cyRef = useRef(null);
  const [filterType, setFilterType] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const nodeColors = {
    report: '#ef4444',
    company: '#38bdf8',
    recruiter: '#a855f7',
    phone: '#f59e0b',
    email: '#10b981',
    domain: '#ec4899',
    upi: '#f43f5e',
  };

  useEffect(() => {
    if (!containerRef.current) return;

    // Filter elements if filterType is active
    let filteredNodes = elements.nodes || [];
    let filteredEdges = elements.edges || [];

    if (filterType !== 'all') {
      const allowedNodeIds = new Set();
      filteredNodes = filteredNodes.filter((n) => {
        const matches = n.data.type === filterType || n.data.type === 'report';
        if (matches) allowedNodeIds.add(n.data.id);
        return matches;
      });

      filteredEdges = filteredEdges.filter(
        (e) => allowedNodeIds.has(e.data.source) && allowedNodeIds.has(e.data.target)
      );
    }

    const cy = cytoscape({
      container: containerRef.current,
      elements: [...filteredNodes, ...filteredEdges],
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'color': '#f1f5f9',
            'font-size': '11px',
            'font-family': 'Inter, sans-serif',
            'text-valign': 'bottom',
            'text-margin-y': 6,
            'background-color': 'data(color)',
            'border-width': 2,
            'border-color': '#0f172a',
            'width': 'mapData(degree, 1, 10, 24, 46)',
            'height': 'mapData(degree, 1, 10, 24, 46)',
            'text-outline-color': '#060913',
            'text-outline-width': 2,
            'text-wrap': 'ellipsis',
            'text-max-width': '120px'
          }
        },
        {
          selector: 'node[type = "report"]',
          style: {
            'shape': 'diamond',
            'width': 34,
            'height': 34,
            'border-color': '#fecdd3',
            'border-width': 2
          }
        },
        {
          selector: 'node[type = "company"]',
          style: {
            'shape': 'round-rectangle',
            'corner-radius': '6px',
            'width': 38,
            'height': 28
          }
        },
        {
          selector: 'node[type = "upi"]',
          style: {
            'shape': 'hexagon'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 1.5,
            'line-color': '#334155',
            'target-arrow-color': '#475569',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'opacity': 0.75,
            'arrow-scale': 0.8
          }
        },
        {
          selector: 'node:selected',
          style: {
            'border-color': '#38bdf8',
            'border-width': 4,
            'shadow-blur': 15,
            'shadow-color': '#38bdf8',
            'shadow-opacity': 0.8
          }
        },
        {
          selector: '.highlighted',
          style: {
            'border-color': '#06b6d4',
            'border-width': 3,
            'opacity': 1,
            'line-color': '#06b6d4',
            'target-arrow-color': '#06b6d4',
            'z-index': 99
          }
        },
        {
          selector: '.dimmed',
          style: {
            'opacity': 0.15
          }
        }
      ],
      layout: {
        name: 'cose',
        animate: true,
        animationDuration: 800,
        nodeDimensionsIncludeLabels: true,
        nodeRepulsion: 8500,
        idealEdgeLength: 85,
        edgeElasticity: 0.45,
        gravity: 0.25,
        padding: 40
      }
    });

    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      const connectedEdges = node.connectedEdges();
      const connectedNodes = connectedEdges.connectedNodes();

      cy.elements().removeClass('highlighted dimmed');
      cy.elements().addClass('dimmed');

      node.removeClass('dimmed').addClass('highlighted');
      connectedEdges.removeClass('dimmed').addClass('highlighted');
      connectedNodes.removeClass('dimmed').addClass('highlighted');

      if (onNodeSelect) {
        onNodeSelect(node.data());
      }
    });

    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        cy.elements().removeClass('highlighted dimmed');
        if (onNodeSelect) onNodeSelect(null);
      }
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
    };
  }, [elements, filterType]);

  // Handle external selection
  useEffect(() => {
    if (!cyRef.current || !selectedNodeId) return;
    const cy = cyRef.current;
    const node = cy.getElementById(selectedNodeId);
    if (node && node.length > 0) {
      cy.center(node);
      cy.zoom(1.4);
      node.trigger('tap');
    }
  }, [selectedNodeId]);

  // Handle Search
  const handleSearch = (e) => {
    e.preventDefault();
    if (!cyRef.current || !searchTerm.trim()) return;
    const cy = cyRef.current;
    const term = searchTerm.toLowerCase();

    const matched = cy.nodes().filter((n) => {
      const label = (n.data('label') || '').toLowerCase();
      const raw = (n.data('raw_value') || '').toLowerCase();
      return label.includes(term) || raw.includes(term);
    });

    if (matched.length > 0) {
      cy.elements().removeClass('highlighted dimmed');
      cy.elements().addClass('dimmed');
      matched.removeClass('dimmed').addClass('highlighted');
      cy.center(matched);
      cy.zoom(1.2);
      if (onNodeSelect) onNodeSelect(matched[0].data());
    }
  };

  return (
    <div className="relative w-full rounded-2xl border border-navy-800 bg-navy-950 overflow-hidden shadow-2xl flex flex-col" style={{ height }}>
      {/* Top Toolbar */}
      <div className="z-10 flex flex-wrap items-center justify-between gap-3 p-3 bg-navy-900/80 backdrop-blur border-b border-navy-800">
        {/* Filter buttons */}
        <div className="flex items-center gap-1.5 overflow-x-auto text-xs">
          <span className="text-slate-400 flex items-center gap-1 px-1 font-medium">
            <Filter className="w-3.5 h-3.5" /> Filter:
          </span>
          {[
            { id: 'all', label: 'All Entities' },
            { id: 'report', label: 'Reports', color: 'bg-rose-500' },
            { id: 'phone', label: 'Phones', color: 'bg-amber-500' },
            { id: 'email', label: 'Emails', color: 'bg-emerald-500' },
            { id: 'upi', label: 'UPI IDs', color: 'bg-pink-500' },
            { id: 'domain', label: 'Domains', color: 'bg-fuchsia-500' },
            { id: 'company', label: 'Companies', color: 'bg-sky-500' }
          ].map((btn) => (
            <button
              key={btn.id}
              onClick={() => setFilterType(btn.id)}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-lg transition font-medium ${
                filterType === btn.id
                  ? 'bg-navy-700 text-white border border-cyan-500/40 shadow-sm'
                  : 'bg-navy-950/60 text-slate-400 hover:text-slate-200 border border-navy-800'
              }`}
            >
              {btn.color && <span className={`w-2 h-2 rounded-full ${btn.color}`} />}
              <span>{btn.label}</span>
            </button>
          ))}
        </div>

        {/* Search Input */}
        <form onSubmit={handleSearch} className="flex items-center gap-2">
          <div className="relative">
            <SearchIcon className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search phone, UPI, email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-8 pr-3 py-1 text-xs rounded-lg bg-navy-950 border border-navy-700 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-400 w-48"
            />
          </div>
          <button
            type="submit"
            className="px-2.5 py-1 text-xs rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-medium transition"
          >
            Locate
          </button>
        </form>
      </div>

      {/* Graph Canvas */}
      <div className="relative flex-1 w-full bg-radial from-navy-900/40 via-navy-950 to-navy-950">
        <div ref={containerRef} className="absolute inset-0" />

        {/* Floating Controls */}
        <div className="absolute bottom-4 right-4 z-10 flex flex-col gap-1.5 bg-navy-900/90 border border-navy-700 rounded-xl p-1.5 shadow-xl backdrop-blur">
          <button
            onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 1.25)}
            className="p-2 rounded-lg text-slate-300 hover:text-white hover:bg-navy-800 transition"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 0.8)}
            className="p-2 rounded-lg text-slate-300 hover:text-white hover:bg-navy-800 transition"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            onClick={() => cyRef.current?.fit(undefined, 40)}
            className="p-2 rounded-lg text-slate-300 hover:text-white hover:bg-navy-800 transition"
            title="Fit to View"
          >
            <Maximize2 className="w-4 h-4" />
          </button>
          <button
            onClick={() => cyRef.current?.layout({ name: 'cose', animate: true }).run()}
            className="p-2 rounded-lg text-slate-300 hover:text-white hover:bg-navy-800 transition"
            title="Reset Layout"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>

        {/* Legend */}
        <div className="absolute bottom-4 left-4 z-10 hidden sm:flex items-center gap-3 px-3 py-2 bg-navy-900/85 border border-navy-800 rounded-xl text-[11px] text-slate-300 backdrop-blur shadow-lg">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500" /> Report
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> Phone
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Email
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-pink-500" /> UPI
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-sky-500" /> Company
          </span>
        </div>
      </div>
    </div>
  );
}
