import mesa
from kyon.agents import Trap, Kyon,  FoodResourceArea, BeastPath    #VegetationDensity,
from kyon.model import KyonModel

def kyon_portrayal(agent):
    if agent is None:
        return      
        
    portrayal = {}

    if isinstance(agent, Kyon):
        portrayal["Shape"] = "kyon/resources/kyon.png"
        portrayal["scale"] = 0.8
        portrayal["Layer"] = 3
        #portrayal["text"] = round(agent.after_birth, 1)
        portrayal["text_color"] = "Black"

    elif isinstance(agent, Trap):
        portrayal["Shape"] = "kyon/resources/hunter.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 3


#    elif isinstance(agent, VegetationDensity):
#        if agent.density == "dense":
#            portrayal["Color"] = ["#006400", "#008000", "#32CD32"]  # 濃い植生
#        elif agent.density == "normal":
#            portrayal["Color"] = ["#228B22", "#32CD32", "#7CFC00"]  # 普通の植生
#        else:
#            portrayal["Color"] = ["#9ACD32", "#ADFF2F", "#BFFF00"]  # 薄い植生
#        portrayal["Shape"] = "rect"
#        portrayal["Filled"] = "true"
#        portrayal["Layer"] = 0
#        portrayal["w"] = 1
#        portrayal["h"] = 1
        
    elif isinstance(agent, FoodResourceArea):
        portrayal["Color"] = ["#FFD700", "#FFEC8B", "#FFFACD"]  # 食物資源エリアを黄色で表示
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 1
        portrayal["w"] = 1
        portrayal["h"] = 1

    elif isinstance(agent, BeastPath):
        portrayal["Color"] = ["#8B4513"]  # 獣道を茶色で表示
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 2
        portrayal["w"] = 1
        portrayal["h"] = 1

    # 以下のコードで全フィールドに緑色の背景を設定
    if portrayal == {}:
        portrayal["Color"] = "#228B22"  # 普通の植生の緑色
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    return portrayal

# キャンバス要素を作成
canvas_element = mesa.visualization.CanvasGrid(kyon_portrayal, 400, 400, 1200, 1200)
#canvas_element = mesa.visualization.CanvasGrid(kyon_portrayal, 200, 200, 1000, 1000)

# チャート要素を作成
chart_element = mesa.visualization.ChartModule(
    [
        {"Label": "Kyon", "Color": "#666666"},  # ラベル「Kyon」を表示する
    ]
)

# チャート要素2を作成
chart_element2 = mesa.visualization.ChartModule(
    [
        #{"Label": "BornKyon", "Color": "#00AA00"},  # 「生まれたキョン」を表示する
        #{"Label": "DeadinLifeKyon", "Color": "#666666"},  # 「寿命で死んだキョン」を表示する
        {"Label": "CapturedKyon", "Color": "#AA0000"},  # 「トラップに捕まったキョン」を表示する
    ]
)

# モデルパラメータの定義
model_params = {
    "title": mesa.visualization.StaticText("パラメータ:"),
    "initial_kyon": mesa.visualization.Slider("初期キョン個体数", 250, 0, 300), 
    "initial_traps": mesa.visualization.Slider("初期罠数", 90, 0, 1000), 
    "base_success_rate": mesa.visualization.Slider("キョン捕獲成功率", 0.6, 0, 1, 0.01),
    #"placement_method": mesa.visualization.Choice("罠の配置方法", value="random", choices=["random",  "food_resource"]),  #"dense_vegetation",を削除
    #"simulation_counter": mesa.visualization.Slider("シミュレーションカウンター", 1, 1, 10),
}

# サーバーの設定
server = mesa.visualization.ModularServer(
    KyonModel, [ chart_element, chart_element2], "キョン繁殖シミュレーション", model_params
    )

#server = mesa.visualization.ModularServer(
#    KyonModel, [canvas_element, chart_element, chart_element2], "キョン繁殖シミュレーション", model_params
#    )




server.port = 8604


