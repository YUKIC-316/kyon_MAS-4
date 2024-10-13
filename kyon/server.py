import mesa

from kyon.agents import Trap, Kyon, VegetationDensity
from kyon.model import KyonModel

def kyon_portrayal(agent):
    if agent is None:
        return

    portrayal = {}

    if isinstance(agent, Kyon):
        portrayal["Shape"] = "kyon/resources/kyon.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1
        portrayal["text"] = round(agent.after_birth, 1)
        portrayal["text_color"] = "Black"

    elif isinstance(agent, Trap):
        portrayal["Shape"] = "kyon/resources/hunter.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 2


    elif isinstance(agent, VegetationDensity):
        if agent.density == "dense":
            portrayal["Color"] = ["#006400", "#008000", "#32CD32"]  # 濃い植生
        elif agent.density == "normal":
            portrayal["Color"] = ["#228B22", "#32CD32", "#7CFC00"]  # 普通の植生
        else:
            portrayal["Color"] = ["#9ACD32", "#ADFF2F", "#BFFF00"]  # 薄い植生
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    return portrayal

# キャンバス要素を作成
canvas_element = mesa.visualization.CanvasGrid(kyon_portrayal, 100, 100, 1000, 1000)

# チャート要素を作成
chart_element = mesa.visualization.ChartModule(
    [
        # {"Label": "Wolves", "Color": "#AA0000"},  # ラベル「Wolves」を表示する
        {"Label": "Kyon", "Color": "#666666"},  # ラベル「Kyon」を表示する
        # {"Label": "EatenGrass", "Color": "#00AA00"},  # ラベル「EatenGrass」を表示する
    ]
)

# チャート要素2を作成
chart_element2 = mesa.visualization.ChartModule(
    [
        {"Label": "BornKyon", "Color": "#00AA00"},  # 「生まれたキョン」を表示する
        {"Label": "DeadinLifeKyon", "Color": "#666666"},  # 「寿命で死んだキョン」を表示する
        {"Label": "CapturedKyon", "Color": "#AA0000"},  # 「トラップに捕まったキョン」を表示する
    ]
)

# チャート要素3を作成
#chart_element3 = mesa.visualization.ChartModule(
    #[
        #{"Label": "EatenGrass", "Color": "#00AA00"},  # 「食べられた草」を表示する
    #]
#)

# モデルパラメータの定義
model_params = {
    # 以下の行は、StaticTextの例です。
    "title": mesa.visualization.StaticText("パラメータ:"),
    # "grass": mesa.visualization.Checkbox("草の有効化", True),
    #"grass_regrowth_time": mesa.visualization.Slider("草の再成長時間", 2, 1, 10),  
    "initial_sheep": mesa.visualization.Slider(
        "初期キョン個体数", 60, 10, 300 
    ), 
    "sheep_reproduce": mesa.visualization.Slider(
        "キョンの再生産率", 0.005, 0.001, 1.0, 0.001
    ),
    #"initial_wolves": mesa.visualization.Slider("初期ハンター個体数", 10, 0, 100),
    "base_success_rate": mesa.visualization.Slider(
        "キョン捕獲成功率", 0.06, 0.001, 1.0, 0.001
    ),
    "simuration_counter": mesa.visualization.Slider("シミュレーションカウンター", 1, 1, 10),
    # "wolf_reproduce": mesa.visualization.Slider(
    #     "ハンターの再生産率",
    #     0.0,
    #     0.0,
    #     1.0,
    #     0.01,
    #     description="ハンターエージェントが再生産する割合。",
    # ),
    # "wolf_gain_from_food": mesa.visualization.Slider(
    #     "ハンターの食物から得るエネルギー", 0, 0, 50
    # ),
    # "sheep_gain_from_food": mesa.visualization.Slider("キョンの食物から得るエネルギー", 4, 1, 10),
}

# サーバーの設定
server = mesa.visualization.ModularServer(
    KyonModel, [canvas_element, chart_element, chart_element2, ], "キョン繁殖シミュレーション", model_params
)
server.port = 8526
