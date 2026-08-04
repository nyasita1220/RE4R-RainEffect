# RE4R Rain Texture Swap

生化危机4重制版 湿身自动换贴图插件

检测游戏湿身状态（下雨/下水/踩水坑），自动将指定贴图替换为湿身版本，变干后恢复原贴图。

## 效果

- 下雨时自动切换为湿身贴图
- 下水、踩水坑等任何湿身状态都会触发
- 变干后自动恢复晴天贴图
- 支持任意贴图槽（法线、漫反射、粗糙度等）
- 不绑定特定角色名，按贴图路径匹配

## 前置要求

- [REFramework](https://github.com/praydog/REFramework)（RE4R 版）
- Rain_ 湿身贴图需要被游戏加载（通过 MDF 引用）

## 快速开始

### 1. 生成脚本

运行配置生成器：

```bash
python build_rainswap.py
```

按提示输入贴图路径对：

```
法线1 原贴图: _Chainsaw/Character/ch/cha0/cha000/00/cha000_00_NRMR.tex
法线1 浸湿贴图: _Chainsaw/Character/ch/cha0/cha000/00/Rain_cha000_00_NRMR.tex
法线2 原贴图: cplt

脚本文件名 (不含.lua): MyMod_rain_texture_swap
```

### 2. 让游戏加载 Rain_ 贴图

Rain_ 贴图必须被 MDF 文件引用才能被游戏加载。方法：

1. 使用 [REasy](https://github.com/alphazolam/RE_RSZ) 或其他 MDF 编辑工具
2. 打开角色 MDF 文件
3. 在纹理资源列表中添加上你的 Rain_ 贴图路径
4. 或者：创建一个空 GameObject 的 MDF，在其中引用 Rain_ 贴图

### 3. 安装

1. 将生成的 `.lua` 文件放入 `<游戏目录>/reframework/autorun/`
2. 确保雨天的湿身贴图与 MDF 中引用的路径一致
3. 重启游戏

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
