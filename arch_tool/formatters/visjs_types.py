from typing import Dict, TypedDict, Literal, Callable, Any

# Type definitions for vis.js node configuration
class ColorHighlight(TypedDict, total=False):
    """Color configuration for highlighted state."""
    border: str
    background: str

class ColorHover(TypedDict, total=False):
    """Color configuration for hover state."""
    border: str
    background: str

class NodeColor(TypedDict, total=False):
    """Color configuration for node."""
    border: str
    background: str
    highlight: ColorHighlight | str
    hover: ColorHover | str

Color = str | NodeColor

class FixedPosition(TypedDict, total=False):
    """Configuration for fixed node position."""
    x: bool
    y: bool

# Fixed can be either a boolean or specific axis configuration
Fixed = bool | FixedPosition

# Shape type definition with all valid vis.js shapes
Shape = Literal[
    "ellipse",
    "circle",
    "database",
    "box",
    "text",  # Label inside
    "image",
    "circularImage",
    "diamond",
    "dot",
    "star",  # Label outside
    "triangle",
    "triangleDown",
    "hexagon",
    "square",
    "icon",  # Label outside
    "custom",  # Custom rendering
]

class FontStyle(TypedDict, total=False):
    """Style configuration for specific font variants."""
    color: str
    size: int
    face: str
    mod: str
    vadjust: int

class FontConfig(FontStyle, total=False):
    """Font configuration for node label."""
    background: str
    strokeWidth: int
    strokeColor: str
    align: Literal["left", "center", "right"]
    multi: bool | Literal["html", "markdown", "md"]
    bold: FontStyle
    ital: FontStyle
    boldital: FontStyle
    mono: FontStyle

class MarginConfig(TypedDict, total=False):
    """Margin configuration for node label."""
    top: int
    right: int
    bottom: int
    left: int

Margin = MarginConfig

class ImagePaddingConfig(TypedDict, total=False):
    """Padding configuration for images inside nodes."""
    left: int
    top: int
    bottom: int
    right: int

ImagePadding = ImagePaddingConfig

class ImageConfig(TypedDict, total=False):
    """Image configuration for image-based nodes."""
    unselected: str
    selected: str

Image = str | ImageConfig

class IconConfig(TypedDict, total=False):
    """Icon configuration for icon-based nodes."""
    face: str
    code: str
    size: int
    color: str
    weight: int | str

Icon = IconConfig

class ShapeProperties(TypedDict, total=False):
    """Additional shape properties configuration."""
    borderDashes: list[int] | bool
    borderRadius: int
    interpolation: bool
    useImageSize: bool
    useBorderWithImage: bool
    coordinateOrigin: Literal["center", "top-left"]

ShapePropertiesConfig = ShapeProperties

class ShadowConfig(TypedDict, total=False):
    """Shadow configuration for nodes."""
    enabled: bool
    color: str
    size: int
    x: int
    y: int

Shadow = bool | ShadowConfig

class ChosenNodeConfig(TypedDict, total=False):
    """Configuration for node appearance when chosen/selected."""
    color: str
    borderWidth: int
    borderColor: str
    size: int
    borderDashes: list[int] | bool
    borderRadius: int
    shadow: bool
    shadowColor: str
    shadowSize: int
    shadowX: int
    shadowY: int

class ChosenLabelConfig(TypedDict, total=False):
    """Configuration for label appearance when node is chosen/selected."""
    color: str
    size: int
    face: str
    mod: str
    vadjust: int
    strokeWidth: int
    strokeColor: str

class ChosenConfig(TypedDict, total=False):
    """Configuration for chosen (selected/hovered) states."""
    node: bool | Callable[[ChosenNodeConfig, str | int, bool, bool], None]
    label: bool | Callable[[ChosenLabelConfig, str | int, bool, bool], None]

Chosen = bool | ChosenConfig

class WidthConstraintConfig(TypedDict, total=False):
    """Width constraint configuration for nodes."""
    minimum: int
    maximum: int

WidthConstraint = bool | int | WidthConstraintConfig

class HeightConstraintConfig(TypedDict, total=False):
    """Height constraint configuration for nodes."""
    minimum: int
    valign: Literal["top", "middle", "bottom"]

HeightConstraint = bool | int | HeightConstraintConfig

class ScalingLabelConfig(TypedDict, total=False):
    """Scaling configuration for node labels."""
    enabled: bool
    min: int
    max: int
    maxVisible: int
    drawThreshold: int

class ScalingConfig(TypedDict, total=False):
    """Scaling configuration for nodes based on value."""
    min: int
    max: int
    label: ScalingLabelConfig
    customScalingFunction: Callable[[int, int, int, int], float]

Scaling = ScalingConfig

# Edge/Link type definitions

class ArrowConfig(TypedDict, total=False):
    """Arrow configuration for edges."""
    enabled: bool
    imageHeight: int
    imageWidth: int
    scaleFactor: float
    src: str
    type: Literal["arrow", "bar", "circle", "box", "crow", "curve", "diamond", "inv_curve", "triangle", "inv_triangle", "vee"]


class ArrowsConfig(TypedDict, total=False):
    """Arrows configuration for edge directions."""
    to: ArrowConfig | bool
    middle: ArrowConfig | bool
    from_: ArrowConfig | bool  # Using from_ since from is a Python keyword


Arrows = str | ArrowsConfig

class EdgeColor(TypedDict, total=False):
    """Color configuration for edges."""
    color: str
    highlight: str
    hover: str
    inherit: bool | Literal["from", "to", "both"]
    opacity: float


class EdgeFont(FontStyle, total=False):
    """Font configuration for edge labels."""
    color: str
    size: int
    face: str
    background: str
    strokeWidth: int
    strokeColor: str
    align: Literal["horizontal", "top", "middle", "bottom"]
    multi: bool | Literal["html", "markdown", "md"]
    vadjust: int
    bold: FontStyle
    ital: FontStyle
    boldital: FontStyle
    mono: FontStyle


class EdgeShadowConfig(TypedDict, total=False):
    """Shadow configuration for edges."""
    enabled: bool
    color: str
    size: int
    x: int
    y: int


EdgeShadow = bool | EdgeShadowConfig

class SmoothConfig(TypedDict, total=False):
    """Smooth curve configuration for edges."""
    enabled: bool
    type: Literal[
        "dynamic",
        "continuous",
        "discrete",
        "diagonalCross",
        "straightCross",
        "horizontal",
        "vertical",
        "curvedCW",
        "curvedCCW",
        "cubicBezier",
    ]
    roundness: float
    forceDirection: bool | Literal["horizontal", "vertical", "none"]


Smooth = bool | SmoothConfig

class DashesConfig(TypedDict, total=False):
    """Dashes configuration for edges."""
    enabled: bool
    pattern: list[int]


Dashes = bool | list[int] | DashesConfig


class EdgeBackground(TypedDict, total=False):
    """Background configuration for edge labels."""
    enabled: bool
    color: str
    size: int
    dashes: bool | list[int]


class WidthConstraintEdge(TypedDict, total=False):
    """Width constraint for edge labels."""
    maximum: int


class IconConfig(TypedDict, total=False):
    """Icon configuration for icon-based nodes."""
    face: str
    code: str
    size: int
    color: str
    weight: int | str

class ShapeProperties(TypedDict, total=False):
    """Additional shape properties configuration."""
    borderDashes: list[int] | bool
    borderRadius: int
    interpolation: bool
    useImageSize: bool
    useBorderWithImage: bool
    coordinateOrigin: Literal['center', 'top-left']

class ShadowConfig(TypedDict, total=False):
    """Shadow configuration for nodes."""
    enabled: bool
    color: str
    size: int
    x: int
    y: int



class ChosenNodeConfig(TypedDict, total=False):
    """Configuration for node appearance when chosen/selected."""
    color: str
    borderWidth: int
    borderColor: str
    size: int
    borderDashes: list[int] | bool
    borderRadius: int
    shadow: bool
    shadowColor: str
    shadowSize: int
    shadowX: int
    shadowY: int


class ChosenLabelConfig(TypedDict, total=False):
    """Configuration for label appearance when node is chosen/selected."""
    color: str
    size: int
    face: str
    mod: str
    vadjust: int
    strokeWidth: int
    strokeColor: str


class ChosenConfig(TypedDict, total=False):
    """Configuration for chosen (selected/hovered) states."""
    node: bool | Callable[[ChosenNodeConfig, str | int, bool, bool], None]
    label: bool | Callable[[ChosenLabelConfig, str | int, bool, bool], None]


Chosen = bool | ChosenConfig


class WidthConstraintConfig(TypedDict, total=False):
    """Width constraint configuration for nodes."""
    minimum: int
    maximum: int


class HeightConstraintConfig(TypedDict, total=False):
    """Height constraint configuration for nodes."""
    minimum: int
    valign: Literal['top', 'middle', 'bottom']


class ScalingConfig(TypedDict, total=False):
    """Scaling configuration for nodes based on value."""
    min: int
    max: int
    label: 'ScalingLabelConfig'
    customScalingFunction: Callable[[int, int, int, int], int]


class ScalingLabelConfig(TypedDict, total=False):
    """Scaling configuration for node labels."""
    enabled: bool
    min: int
    max: int
    maxVisible: int
    drawThreshold: int

class SelfReferenceConfig(TypedDict, total=False):
    """Configuration for self-referencing edges."""
    size: float
    angle: float
    renderBehindTheNode: bool


class HierarchicalConfig(TypedDict, total=False):
    """Hierarchical layout configuration."""
    enabled: bool
    levelSeparation: int
    nodeSpacing: int
    treeSpacing: int
    blockShifting: bool
    edgeMinimization: bool
    parentCentralization: bool
    direction: Literal['UD', 'DU', 'LR', 'RL']
    sortMethod: Literal['hubsize', 'directed']
    shakeTowards: Literal['roots', 'leaves']

class LayoutConfig(TypedDict, total=False):
    """Layout configuration for the network."""
    randomSeed: int | str
    improvedLayout: bool
    clusterThreshold: int
    hierarchical: HierarchicalConfig

class KeyboardSpeedConfig(TypedDict, total=False):
    """Speed configuration for keyboard interaction."""
    x: int
    y: int
    zoom: float

class KeyboardConfig(TypedDict, total=False):
    """Keyboard configuration for network interaction."""
    enabled: bool
    speed: KeyboardSpeedConfig
    bindToWindow: bool
    autoFocus: bool

class InteractionConfig(TypedDict, total=False):
    """Interaction configuration for the network."""
    dragNodes: bool
    dragView: bool
    hideEdgesOnDrag: bool
    hideEdgesOnZoom: bool
    hideNodesOnDrag: bool
    hover: bool
    hoverConnectedEdges: bool
    keyboard: KeyboardConfig
    multiselect: bool
    navigationButtons: bool
    selectable: bool
    selectConnectedEdges: bool
    tooltipDelay: int
    zoomSpeed: int
    zoomView: bool

class BarnesHutConfig(TypedDict, total=False):
    """Barnes-Hut physics configuration."""
    theta: float
    gravitationalConstant: float
    centralGravity: float
    springLength: float
    springConstant: float
    damping: float
    avoidOverlap: float

class ForceAtlas2BasedConfig(TypedDict, total=False):
    """Force Atlas 2 based physics configuration."""
    theta: float
    gravitationalConstant: float
    centralGravity: float
    springLength: float
    springConstant: float
    damping: float
    avoidOverlap: float

class RepulsionConfig(TypedDict, total=False):
    """Repulsion physics configuration."""
    centralGravity: float
    springLength: float
    springConstant: float
    nodeDistance: float
    damping: float

class HierarchicalRepulsionConfig(TypedDict, total=False):
    """Hierarchical repulsion physics configuration."""
    centralGravity: float
    springLength: float
    springConstant: float
    nodeDistance: float
    damping: float
    avoidOverlap: float

class StabilizationConfig(TypedDict, total=False):
    """Stabilization configuration for physics simulation."""
    enabled: bool
    iterations: int
    updateInterval: int
    onlyDynamicEdges: bool
    fit: bool

class WindConfig(TypedDict, total=False):
    """Wind configuration for physics simulation."""
    x: float
    y: float

class PhysicsConfig(TypedDict, total=False):
    """Physics configuration for the network."""
    enabled: bool
    barnesHut: BarnesHutConfig
    forceAtlas2Based: ForceAtlas2BasedConfig
    repulsion: RepulsionConfig
    hierarchicalRepulsion: HierarchicalRepulsionConfig
    maxVelocity: float
    minVelocity: float
    solver: Literal['barnesHut', 'repulsion', 'hierarchicalRepulsion', 'forceAtlas2Based']
    stabilization: StabilizationConfig
    timestep: float
    adaptiveTimestep: bool
    wind: WindConfig


class NodeConfig(TypedDict, total=False):
    """Node configuration for vis.js network."""
    borderWidth: int
    borderWidthSelected: int
    color: Color
    opacity: float
    fixed: Fixed
    font: FontConfig
    group: str
    heightConstraint: HeightConstraint
    hidden: bool
    icon: Icon
    id: str | int
    image: Image
    imagePadding: ImagePadding
    label: str
    labelHighlightBold: bool
    level: int
    mass: float
    margin: Margin
    shadow: Shadow
    physics: bool
    scaling: Scaling
    shape: Shape
    shapeProperties: ShapePropertiesConfig
    size: int
    widthConstraint: WidthConstraint
    title: str
    value: int | float
    x: int
    y: int

class EdgeConfig(TypedDict, total=False):
    """Edge configuration for vis.js network."""
    arrows: Arrows
    color: EdgeColor
    dashes: Dashes
    font: EdgeFont
    from_: str | int
    hidden: bool
    hoverWidth: int
    id: str | int
    label: str
    labelHighlightBold: bool
    length: int
    physics: bool
    scaling: Scaling
    selectionWidth: int
    selfReferenceSize: float
    selfReference: SelfReferenceConfig
    shadow: EdgeShadow
    smooth: Smooth
    title: str
    to: str | int
    value: int | float
    width: int | float
    widthConstraint: WidthConstraintEdge
