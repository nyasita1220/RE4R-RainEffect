# RE4R Rain Texture Swap

生化危机4重制版 湿身自动换贴图插件

检测游戏湿身状态（下雨/下水/踩水坑），自动将指定贴图替换为湿身版本，变干后恢复原贴图。

## 效果

- 下雨时自动切换为湿身贴图
- 下水、踩水坑等任何湿身状态都会触发
- 变干后自动恢复晴天贴图
- 支持任意贴图槽（法线、漫反射、粗糙度等）

## 前置要求

- [REFramework](https://github.com/praydog/REFramework)（RE4R 版）
- Rain_ 湿身贴图需要被游戏加载（通过 MDF 引用）

## 快速开始

### 1. 让游戏加载 Rain_ 贴图

Rain_ 贴图必须被 MDF 文件引用才能被游戏加载。
解决方法为：
1.根据需要随便创建一个部件（下面简称为引用部件），名字随便起，建议创建空模型，不影响mod正常显示和使用等
2.创建引用部件对应的MDF，MDF中的文件路径为生效后你要切换的贴图，写哪个槽位都可以，我为了方便原贴图用的哪个槽位我就写的哪个槽位
3.现在进游戏就可以正常加载替换贴图了

### 2. 生成脚本

运行配置生成器 `RainEffect_Sawp_Generator.py`，根据提示操作

### 3. 打包进你的MOD

将生成的 `.lua` 文件放入 `<MOD文件夹>/reframework/autorun/`即可完成

## 文件结构示例

```
RESIDENT EVIL 4  BIOHAZARD RE4/
  reframework/
    autorun/
      MyMod_rain_texture_swap.lua   ← 生成的脚本
  natives/STM/_Chainsaw/
    Character/ch/cha0/cha000/00/
      cha000_00_NRMR.tex            ← 原贴图
      Rain_cha000_00_NRMR.tex       ← 湿身贴图
```

## 工作原理

1. 读取 `chainsaw.WeatherManager._CurrentGlobalWetRate` 检测湿身状态
2. 扫描场景中所有 `via.render.Mesh` 组件
3. 匹配配置中指定的贴图路径
4. 通过 `via.render.Mesh.setMaterialTexture` 替换贴图

## 技术细节

- 预加载机制：场景就绪后一次性扫描并缓存目标 mesh 位置
- 状态切换只遍历缓存的目标（无需重复扫描全场景）
- 贴图替换在 `BeginRendering` 阶段执行，避免渲染冲突
- 使用 `ResourceHolder` 包装确保引擎兼容性

## 致谢

- [REFramework](https://github.com/praydog/REFramework) by praydog
- [EMV-Engine](https://github.com/alphazolam/EMV-Engine) by alphaZomega
- [Weather FX](https://www.nexusmods.com/residentevil42023/mods/107) by SilverEzredes
