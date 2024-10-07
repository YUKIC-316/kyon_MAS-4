import mesa
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Slider, Choice
from kyon.model import KyonModel
from kyon.agents import Kyon, Trap, GrassPatch, FoodResource


def agent_portrayal(agent):
    """
    エージェントの視覚的な表現を設定する関数。
    キョン、罠、植生、食物資源エリアのそれぞれに対して異なるアイコンや色を指定します。
    """
    if isinstance(agent, Kyon):
        portrayal = {
            "Shape": "kyon/resources/kyon.png",  # キョンの画像
            "scale": 0.9,
            "Layer": 1
        }
    elif isinstance(agent, Trap):
        portrayal = {
            "Shape": "kyon/resources/hunter.png",  # 罠の画像
            "scale": 0.9,
            "Layer": 2
        }
    elif isinstance(agent, GrassPatch):
        # 植生の密度に基づく色分け
        if agent.density == "dense":
            portrayal = {
                "Shape": "rect",
                "Color": "darkgreen",  # 濃い植生
                "Layer": 0,
                "w": 1,
                "h": 1
            }
        elif agent.density == "medium":
            portrayal = {
                "Shape": "rect",
                "Color": "green",  # 中密度の植生
                "Layer": 0,
                "w": 1,
                "h": 1
            }
        else:
            portrayal = {
                "Shape": "rect",
                "Color": "lightgreen",  # 薄い植生
                "Layer": 0,
                "w": 1,
                "h": 1
            }
    elif isinstance(agent, FoodResource):
        # 食物資源エリアの密度に基づく色分け
        if agent.density == "dense":
            portrayal = {
                "Shape": "rect",
                "Color": "yellowgreen",  # 濃い密度の食物資源エリア
                "Layer": 0,
                "w": 1,
                "h": 1
            }
        elif agent.density == "medium":
            portrayal = {
                "Shape": "rect",
                "Color": "lightyellow",  # 中密度の食物資源エリア
                "Layer": 0,
                "w": 1,
                "h": 1
            }
        else:
            portrayal = {
                "Shape": "rect",
                "Color": "yellow",  # 薄い密度の食物資源エリア
                "Layer": 0,
                "w": 1,
                "h": 1
            }
    return portrayal


# キャンバスの設定
canvas_element = CanvasGrid(agent_portrayal, 40, 40, 500, 500)

# グラフモジュールの設定（キョンの数と罠の数をグラフ化）
chart_element = ChartModule([
    {"Label": "Kyons", "Color": "green"},
    {"Label": "Traps", "Color": "red"}
])

# インタラクティブに選べるシミュレーションのパラメータ設定
model_params = {
    "initial_kyon": Slider("Initial Kyon Population", 100, 10, 300, 10),
    "initial_traps": Slider("Trap Count", 10, 1, 50, 1),
    "trap_placement": Choice("Trap Placement Strategy", ["random", "sparse", "food"]),  # 罠の配置パターンの選択
    "grass_regrowth_time": Slider("Grass Regrowth Time", 3, 1, 10, 1),
    "kyon_reproduce": Slider("Kyon Reproduction Rate", 0.005, 0.001, 1.0, 0.001),
    "capture_success_rate": Slider("Capture Success Rate", 0.3, 0.1, 1.0, 0.1),
}

# サーバー設定
server = ModularServer(
    KyonModel,
    [canvas_element, chart_element],
    "Kyon Simulation",
    model_params
)

# サーバーポートの設定
server.port = 8527

# サーバーの起動
server.launch()
