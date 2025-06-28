import { useState, useRef, useEffect } from 'react'
import { 
  GitBranch, 
  ZoomIn, 
  ZoomOut, 
  RotateCcw, 
  Download, 
  Maximize,
  Move,
  Settings,
  Eye,
  Filter
} from 'lucide-react'
import { ConceptMap } from '../../types/lecture'

interface ConceptMapTabProps {
  conceptMap: ConceptMap
}

const ConceptMapTab = ({ conceptMap }: ConceptMapTabProps) => {
  const svgRef = useRef<SVGSVGElement>(null)
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [highlightedNodes, setHighlightedNodes] = useState<Set<string>>(new Set())
  const [showLabels, setShowLabels] = useState(true)
  const [filterType, setFilterType] = useState<string>('all')

  // حساب مواضع العقد بتخطيط دائري
  const calculateLayout = () => {
    const centerX = 400
    const centerY = 300
    const radius = 200
    
    const nodePositions = new Map()
    
    // العقدة الجذرية في المركز
    const rootNode = conceptMap.nodes.find(node => node.type === 'root')
    if (rootNode) {
      nodePositions.set(rootNode.id, { x: centerX, y: centerY })
    }
    
    // العقد الرئيسية في دائرة حول المركز
    const mainNodes = conceptMap.nodes.filter(node => node.type === 'main')
    mainNodes.forEach((node, index) => {
      const angle = (index / mainNodes.length) * 2 * Math.PI
      const x = centerX + Math.cos(angle) * radius
      const y = centerY + Math.sin(angle) * radius
      nodePositions.set(node.id, { x, y })
    })
    
    // باقي العقد في دوائر خارجية
    const otherNodes = conceptMap.nodes.filter(node => !['root', 'main'].includes(node.type))
    otherNodes.forEach((node, index) => {
      const angle = (index / otherNodes.length) * 2 * Math.PI
      const x = centerX + Math.cos(angle) * (radius + 100)
      const y = centerY + Math.sin(angle) * (radius + 100)
      nodePositions.set(node.id, { x, y })
    })
    
    return nodePositions
  }

  const nodePositions = calculateLayout()

  const handleNodeClick = (nodeId: string) => {
    if (selectedNode === nodeId) {
      setSelectedNode(null)
      setHighlightedNodes(new Set())
    } else {
      setSelectedNode(nodeId)
      
      // تمييز العقد المتصلة
      const connectedNodes = new Set<string>()
      connectedNodes.add(nodeId)
      
      conceptMap.edges.forEach(edge => {
        if (edge.from === nodeId) {
          connectedNodes.add(edge.to)
        }
        if (edge.to === nodeId) {
          connectedNodes.add(edge.from)
        }
      })
      
      setHighlightedNodes(connectedNodes)
    }
  }

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev * 1.2, 3))
  }

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev / 1.2, 0.5))
  }

  const handleReset = () => {
    setZoom(1)
    setPan({ x: 0, y: 0 })
    setSelectedNode(null)
    setHighlightedNodes(new Set())
  }

  const getNodeColor = (node: any) => {
    const colors = {
      root: '#2563eb',      // أزرق
      main: '#10b981',      // أخضر
      category: '#f59e0b',  // برتقالي
      application: '#8b5cf6', // بنفسجي
      concept: '#6b7280'    // رمادي
    }
    return colors[node.type as keyof typeof colors] || colors.concept
  }

  const getEdgeColor = (edge: any) => {
    const opacity = Math.max(0.3, edge.strength)
    return `rgba(107, 114, 128, ${opacity})`
  }

  const filteredNodes = conceptMap.nodes.filter(node => 
    filterType === 'all' || node.type === filterType
  )

  const nodeTypes = [...new Set(conceptMap.nodes.map(node => node.type))]

  const downloadSVG = () => {
    if (!svgRef.current) return
    
    const svgData = new XMLSerializer().serializeToString(svgRef.current)
    const blob = new Blob([svgData], { type: 'image/svg+xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'concept-map.svg'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            خريطة المفاهيم التفاعلية
          </h2>
          <p className="text-gray-600">
            رسم بياني تفاعلي يربط بين المفاهيم الرئيسية في المحاضرة
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center space-x-reverse space-x-2">
          <button
            onClick={() => setShowLabels(!showLabels)}
            className={`p-2 rounded-lg transition-colors duration-200 ${
              showLabels ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
            }`}
            title="إظهار/إخفاء التسميات"
          >
            <Eye className="w-4 h-4" />
          </button>
          
          <button
            onClick={downloadSVG}
            className="p-2 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-lg transition-colors duration-200"
            title="تحميل كصورة"
          >
            <Download className="w-4 h-4" />
          </button>
          
          <button
            onClick={handleReset}
            className="p-2 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-lg transition-colors duration-200"
            title="إعادة التعيين"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Filters and Zoom Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-4 sm:space-y-0">
        {/* Node Type Filter */}
        <div className="flex items-center space-x-reverse space-x-2">
          <Filter className="w-4 h-4 text-gray-500" />
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">جميع المفاهيم</option>
            {nodeTypes.map(type => (
              <option key={type} value={type}>
                {type === 'root' ? 'المفهوم الجذر' :
                 type === 'main' ? 'المفاهيم الرئيسية' :
                 type === 'category' ? 'الفئات' :
                 type === 'application' ? 'التطبيقات' :
                 type === 'concept' ? 'المفاهيم' : type}
              </option>
            ))}
          </select>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center space-x-reverse space-x-2">
          <button
            onClick={handleZoomOut}
            className="p-2 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-lg transition-colors duration-200"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="text-sm text-gray-600 min-w-[60px] text-center">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={handleZoomIn}
            className="p-2 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-lg transition-colors duration-200"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Concept Map */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="relative h-96 sm:h-[500px] lg:h-[600px]">
          <svg
            ref={svgRef}
            width="100%"
            height="100%"
            viewBox={`${-pan.x} ${-pan.y} ${800 / zoom} ${600 / zoom}`}
            className="cursor-move"
          >
            {/* Define gradients and patterns */}
            <defs>
              <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="2" dy="2" stdDeviation="3" floodOpacity="0.3"/>
              </filter>
              <linearGradient id="nodeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="rgba(255,255,255,0.8)" />
                <stop offset="100%" stopColor="rgba(0,0,0,0.1)" />
              </linearGradient>
            </defs>

            {/* Edges */}
            <g>
              {conceptMap.edges.map((edge, index) => {
                const fromNode = conceptMap.nodes.find(n => n.id === edge.from)
                const toNode = conceptMap.nodes.find(n => n.id === edge.to)
                
                if (!fromNode || !toNode) return null
                
                const fromPos = nodePositions.get(edge.from)
                const toPos = nodePositions.get(edge.to)
                
                if (!fromPos || !toPos) return null

                const isHighlighted = highlightedNodes.has(edge.from) || highlightedNodes.has(edge.to)

                return (
                  <g key={index}>
                    <line
                      x1={fromPos.x}
                      y1={fromPos.y}
                      x2={toPos.x}
                      y2={toPos.y}
                      stroke={getEdgeColor(edge)}
                      strokeWidth={isHighlighted ? 3 : Math.max(1, edge.strength * 3)}
                      opacity={isHighlighted ? 1 : 0.6}
                      className="transition-all duration-300"
                    />
                    
                    {/* Edge Label */}
                    {showLabels && edge.label && (
                      <text
                        x={(fromPos.x + toPos.x) / 2}
                        y={(fromPos.y + toPos.y) / 2}
                        textAnchor="middle"
                        className="text-xs fill-gray-600 font-medium"
                        dy="-2"
                      >
                        {edge.label}
                      </text>
                    )}
                    
                    {/* Arrow */}
                    <polygon
                      points={`${toPos.x-5},${toPos.y-5} ${toPos.x+5},${toPos.y} ${toPos.x-5},${toPos.y+5}`}
                      fill={getEdgeColor(edge)}
                      opacity={isHighlighted ? 1 : 0.6}
                    />
                  </g>
                )
              })}
            </g>

            {/* Nodes */}
            <g>
              {filteredNodes.map((node) => {
                const pos = nodePositions.get(node.id)
                if (!pos) return null

                const isSelected = selectedNode === node.id
                const isHighlighted = highlightedNodes.has(node.id)
                const nodeSize = Math.max(20, node.size || 30)

                return (
                  <g key={node.id} className="cursor-pointer">
                    {/* Node Circle */}
                    <circle
                      cx={pos.x}
                      cy={pos.y}
                      r={nodeSize}
                      fill={getNodeColor(node)}
                      stroke={isSelected ? '#1d4ed8' : isHighlighted ? '#3b82f6' : 'white'}
                      strokeWidth={isSelected ? 4 : isHighlighted ? 3 : 2}
                      filter="url(#shadow)"
                      opacity={highlightedNodes.size === 0 || isHighlighted ? 1 : 0.3}
                      className="transition-all duration-300 hover:stroke-blue-500"
                      onClick={() => handleNodeClick(node.id)}
                    />
                    
                    {/* Node Gradient Overlay */}
                    <circle
                      cx={pos.x}
                      cy={pos.y}
                      r={nodeSize}
                      fill="url(#nodeGradient)"
                      opacity="0.7"
                      pointerEvents="none"
                    />

                    {/* Node Label */}
                    {showLabels && (
                      <text
                        x={pos.x}
                        y={pos.y + nodeSize + 15}
                        textAnchor="middle"
                        className={`text-sm font-medium transition-all duration-300 ${
                          isSelected ? 'fill-blue-700' : 
                          isHighlighted ? 'fill-blue-600' : 
                          'fill-gray-700'
                        }`}
                        opacity={highlightedNodes.size === 0 || isHighlighted ? 1 : 0.5}
                      >
                        {node.label}
                      </text>
                    )}

                    {/* Type Indicator */}
                    <circle
                      cx={pos.x + nodeSize - 8}
                      cy={pos.y - nodeSize + 8}
                      r="6"
                      fill="white"
                      stroke={getNodeColor(node)}
                      strokeWidth="2"
                    />
                    <text
                      x={pos.x + nodeSize - 8}
                      y={pos.y - nodeSize + 12}
                      textAnchor="middle"
                      className="text-xs font-bold"
                      fill={getNodeColor(node)}
                    >
                      {node.type === 'root' ? 'R' :
                       node.type === 'main' ? 'M' :
                       node.type === 'category' ? 'C' :
                       node.type === 'application' ? 'A' : 'T'}
                    </text>
                  </g>
                )
              })}
            </g>
          </svg>
        </div>
      </div>

      {/* Selected Node Info */}
      {selectedNode && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-reverse space-x-3">
            <GitBranch className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-blue-900 mb-1">
                {conceptMap.nodes.find(n => n.id === selectedNode)?.label}
              </h4>
              <p className="text-blue-700 text-sm mb-2">
                نوع المفهوم: {conceptMap.nodes.find(n => n.id === selectedNode)?.type}
              </p>
              <div className="text-blue-700 text-sm">
                <strong>الارتباطات:</strong>
                <ul className="mt-1 space-y-1">
                  {conceptMap.edges
                    .filter(edge => edge.from === selectedNode || edge.to === selectedNode)
                    .map((edge, index) => {
                      const connectedNodeId = edge.from === selectedNode ? edge.to : edge.from
                      const connectedNode = conceptMap.nodes.find(n => n.id === connectedNodeId)
                      return (
                        <li key={index} className="flex items-center space-x-reverse space-x-2">
                          <span>→</span>
                          <span>{connectedNode?.label}</span>
                          <span className="text-xs">({edge.label})</span>
                        </li>
                      )
                    })}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h4 className="font-semibold text-gray-900 mb-3">دليل الألوان</h4>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {[
            { type: 'root', label: 'المفهوم الجذر', color: '#2563eb' },
            { type: 'main', label: 'المفاهيم الرئيسية', color: '#10b981' },
            { type: 'category', label: 'الفئات', color: '#f59e0b' },
            { type: 'application', label: 'التطبيقات', color: '#8b5cf6' },
            { type: 'concept', label: 'المفاهيم', color: '#6b7280' }
          ].map((item) => (
            <div key={item.type} className="flex items-center space-x-reverse space-x-2">
              <div
                className="w-4 h-4 rounded-full"
                style={{ backgroundColor: item.color }}
              />
              <span className="text-sm text-gray-700">{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 text-center">
          <div className="text-2xl font-bold text-blue-600">
            {conceptMap.nodes.length}
          </div>
          <div className="text-sm text-gray-600">مفهوم</div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg border border-green-200 text-center">
          <div className="text-2xl font-bold text-green-600">
            {conceptMap.edges.length}
          </div>
          <div className="text-sm text-gray-600">رابط</div>
        </div>
        <div className="bg-orange-50 p-4 rounded-lg border border-orange-200 text-center">
          <div className="text-2xl font-bold text-orange-600">
            {nodeTypes.length}
          </div>
          <div className="text-sm text-gray-600">نوع</div>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg border border-purple-200 text-center">
          <div className="text-2xl font-bold text-purple-600">
            {Math.round(conceptMap.edges.reduce((sum, edge) => sum + edge.strength, 0) / conceptMap.edges.length * 100)}%
          </div>
          <div className="text-sm text-gray-600">قوة الترابط</div>
        </div>
      </div>
    </div>
  )
}

export default ConceptMapTab
